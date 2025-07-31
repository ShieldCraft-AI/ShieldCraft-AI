"""
Chunking module for text processing.
"""

from typing import List, Dict, Any
from abc import ABC, abstractmethod
from pydantic import BaseModel
from infra.utils.config_loader import get_config_loader


class Chunk(BaseModel):
    text: str
    doc_id: str = ""
    chunk_index: int = 0
    start_offset: int = 0
    end_offset: int = 0
    metadata: Dict[str, Any] = {}

    def __str__(self):
        return f"Chunk(doc_id={self.doc_id}, idx={self.chunk_index}, start={self.start_offset}, end={self.end_offset}, text='{self.text[:30]}...')"

    def __repr__(self):
        return self.__str__()


class ChunkingStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str, doc_id: str = "") -> List[Chunk]:
        pass


class FixedChunkingStrategy(ChunkingStrategy):
    @staticmethod
    def chunk(
        text: str,
        doc_id: str = "",
        chunk_size: int = 512,
        overlap: int = 0,
        min_length: int = 0,
    ) -> List[Chunk]:
        if not isinstance(text, str) or not text:
            raise ValueError("Input text must be a non-empty string.")
        chunks = []
        start = 0
        idx = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]
            if len(chunk_text) >= min_length:
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        doc_id=doc_id,
                        chunk_index=idx,
                        start_offset=start,
                        end_offset=end,
                    )
                )
                idx += 1
            start += chunk_size - overlap if chunk_size > overlap else chunk_size
        return chunks


# 2. Semantic Chunking: split by paragraphs (double newline) as a simple semantic proxy
class SemanticChunkingStrategy(ChunkingStrategy):
    @staticmethod
    def chunk(text: str, doc_id: str = "") -> List[Chunk]:
        if not isinstance(text, str) or not text:
            raise ValueError("Input text must be a non-empty string.")
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        chunks = []
        for idx, para in enumerate(paragraphs):
            start_offset = text.find(para)
            end_offset = start_offset + len(para)
            chunks.append(
                Chunk(
                    text=para,
                    doc_id=doc_id,
                    chunk_index=idx,
                    start_offset=start_offset,
                    end_offset=end_offset,
                )
            )
        return chunks


# 3. Recursive Chunking: try semantic, then fixed if too large
class RecursiveChunkingStrategy(ChunkingStrategy):
    @staticmethod
    def chunk(
        text: str, doc_id: str = "", max_chunk_size: int = 512, min_length: int = 0
    ) -> List[Chunk]:
        semantic = SemanticChunkingStrategy()
        sem_chunks = semantic.chunk(text, doc_id)
        final_chunks = []
        idx = 0
        for chunk in sem_chunks:
            if len(chunk.text) > max_chunk_size:
                sub_chunks = FixedChunkingStrategy.chunk(
                    chunk.text, doc_id, max_chunk_size, 0, min_length
                )
                for sub in sub_chunks:
                    sub.chunk_index = idx
                    final_chunks.append(sub)
                    idx += 1
            else:
                chunk.chunk_index = idx
                final_chunks.append(chunk)
                idx += 1
        return final_chunks


# 4. Sentence Chunking: split by period, exclamation, or question mark
import re


class SentenceChunkingStrategy(ChunkingStrategy):
    @staticmethod
    def chunk(text: str, doc_id: str = "") -> List[Chunk]:
        if not isinstance(text, str) or not text:
            raise ValueError("Input text must be a non-empty string.")
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks = []
        offset = 0
        for idx, sent in enumerate(sentences):
            sent = sent.strip()
            if not sent:
                continue
            start_offset = text.find(sent, offset)
            end_offset = start_offset + len(sent)
            offset = end_offset
            chunks.append(
                Chunk(
                    text=sent,
                    doc_id=doc_id,
                    chunk_index=idx,
                    start_offset=start_offset,
                    end_offset=end_offset,
                )
            )
        return chunks


# 5. Token-Based Chunking: requires a tokenizer callable
class TokenBasedChunkingStrategy(ChunkingStrategy):
    @staticmethod
    def chunk(
        text: str,
        doc_id: str = "",
        tokenizer=None,
        chunk_size: int = 512,
        overlap: int = 0,
        min_length: int = 0,
    ) -> List[Chunk]:
        if not callable(tokenizer):
            raise ValueError("Tokenizer must be callable.")
        tokens = tokenizer(text)
        chunks = []
        start = 0
        idx = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = (
                tokenizer.decode(chunk_tokens)
                if hasattr(tokenizer, "decode")
                else " ".join(chunk_tokens)
            )
            if len(chunk_tokens) >= min_length:
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        doc_id=doc_id,
                        chunk_index=idx,
                        start_offset=start,
                        end_offset=end,
                    )
                )
                idx += 1
            start += chunk_size - overlap if chunk_size > overlap else chunk_size
        return chunks


# 6. Sliding Window Chunking: moving window with overlap
class SlidingWindowChunkingStrategy(ChunkingStrategy):
    @staticmethod
    def chunk(
        text: str,
        doc_id: str = "",
        window_size: int = 512,
        step_size: int = 256,
        min_length: int = 0,
    ) -> List[Chunk]:
        if not isinstance(text, str) or not text:
            raise ValueError("Input text must be a non-empty string.")
        chunks = []
        idx = 0
        for start in range(0, len(text), step_size):
            end = min(start + window_size, len(text))
            chunk_text = text[start:end]
            if len(chunk_text) >= min_length:
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        doc_id=doc_id,
                        chunk_index=idx,
                        start_offset=start,
                        end_offset=end,
                    )
                )
                idx += 1
            if end == len(text):
                break
        return chunks


# 7. Custom/Heuristic Chunking: split by custom delimiter or rule
class CustomHeuristicChunkingStrategy(ChunkingStrategy):
    @staticmethod
    def chunk(
        text: str, doc_id: str = "", delimiter: str = "\n---\n", rules: dict = None
    ) -> List[Chunk]:
        if not isinstance(text, str) or not text:
            raise ValueError("Input text must be a non-empty string.")
        parts = [p for p in text.split(delimiter) if p.strip()]
        chunks = []
        for idx, part in enumerate(parts):
            start_offset = text.find(part)
            end_offset = start_offset + len(part)
            chunks.append(
                Chunk(
                    text=part,
                    doc_id=doc_id,
                    chunk_index=idx,
                    start_offset=start_offset,
                    end_offset=end_offset,
                )
            )
        return chunks


def get_chunking_strategy_from_config():
    config_loader = get_config_loader()
    chunking_cfg = config_loader.get_section("chunking")
    strategy = chunking_cfg.get("strategy", "fixed")
    # Validate config for selected strategy
    if strategy not in chunking_cfg:
        raise ValueError(
            f"Missing config block for strategy '{strategy}' in chunking config."
        )
    params = chunking_cfg[strategy] or {}
    # Validate required params for each strategy
    required = {
        "fixed": ["chunk_size", "overlap", "min_length"],
        "semantic": ["min_length"],
        "recursive": ["max_chunk_size", "min_length"],
        "sentence": ["min_length"],
        "token_based": ["chunk_size", "overlap", "min_length", "tokenizer"],
        "sliding_window": ["window_size", "step_size", "min_length"],
        "custom_heuristic": ["delimiter", "min_length", "rules"],
    }
    if strategy not in required:
        raise ValueError(f"Unknown chunking strategy: {strategy}")
    missing = [k for k in required[strategy] if k not in params]
    if missing:
        raise ValueError(
            f"Missing required parameters for strategy '{strategy}': {missing}"
        )
    # Return a tuple: (strategy class, params dict)
    strategy_map = {
        "fixed": FixedChunkingStrategy,
        "semantic": SemanticChunkingStrategy,
        "recursive": RecursiveChunkingStrategy,
        "sentence": SentenceChunkingStrategy,
        "token_based": TokenBasedChunkingStrategy,
        "sliding_window": SlidingWindowChunkingStrategy,
        "custom_heuristic": CustomHeuristicChunkingStrategy,
    }
    return strategy_map[strategy], params


import concurrent.futures


class Chunker:
    def __init__(self):
        self.strategy_class, self.params = get_chunking_strategy_from_config()

    def chunk(self, text: str, doc_id: str = "") -> List[Chunk]:
        # Dynamically pass params to the static method
        return self.strategy_class.chunk(text, doc_id=doc_id, **self.params)

    def chunk_batch(
        self, texts: List[str], doc_ids: List[str] = None, max_workers: int = 4
    ) -> List[List[Chunk]]:
        if doc_ids is None:
            doc_ids = ["" for _ in texts]
        if len(doc_ids) != len(texts):
            raise ValueError("Length of doc_ids must match texts.")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self.chunk, text, doc_id)
                for text, doc_id in zip(texts, doc_ids)
            ]
            return [f.result() for f in futures]
