"""
Chunking module for text processing.
Extensible for different chunking strategies.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError
from ai_core.chunking.chunk import (
    Chunk,
    FixedChunkingStrategy,
    SemanticChunkingStrategy,
    RecursiveChunkingStrategy,
    SentenceChunkingStrategy,
    TokenBasedChunkingStrategy,
    SlidingWindowChunkingStrategy,
    CustomHeuristicChunkingStrategy,
)


class ChunkingConfig(BaseModel):
    # Common
    strategy: str = Field(
        "fixed", description="Chunking strategy: fixed, semantic, recursive"
    )
    # Fixed
    chunk_size: int = Field(
        512, gt=0, description="Size of each chunk in tokens/characters"
    )
    overlap: int = Field(
        0, ge=0, description="Number of tokens/characters to overlap between chunks"
    )
    min_length: int = Field(0, ge=0, description="Minimum length for a chunk")
    # Semantic
    paragraph_delimiter: str = Field(
        "\n\n", description="Delimiter for semantic chunking (paragraph split)"
    )
    # Recursive
    max_chunk_size: int = Field(
        512, gt=0, description="Max chunk size for recursive chunking"
    )


class Chunker:
    def __init__(self, config: ChunkingConfig):
        self.config = config
        self.strategy_map = {
            "fixed": FixedChunkingStrategy,
            "semantic": SemanticChunkingStrategy,
            "recursive": RecursiveChunkingStrategy,
            "sentence": SentenceChunkingStrategy,
            "token_based": TokenBasedChunkingStrategy,
            "sliding_window": SlidingWindowChunkingStrategy,
            "custom_heuristic": CustomHeuristicChunkingStrategy,
        }

    def chunk(self, text: str, doc_id: str = "", **kwargs) -> List[Chunk]:
        if not isinstance(text, str) or not text:
            raise ValueError("Input text must be a non-empty string.")
        strategy = self.config.strategy
        if strategy not in self.strategy_map:
            raise NotImplementedError(
                f"Chunking strategy '{strategy}' not implemented."
            )
        # Build params for the strategy
        params = self._get_strategy_params(strategy)
        params.update(kwargs)
        return self.strategy_map[strategy].chunk(text, doc_id=doc_id, **params)

    def _get_strategy_params(self, strategy: str) -> Dict[str, Any]:
        # Map config fields to strategy params
        c = self.config
        if strategy == "fixed":
            return dict(
                chunk_size=c.chunk_size, overlap=c.overlap, min_length=c.min_length
            )
        elif strategy == "semantic":
            return dict(min_length=c.min_length)
        elif strategy == "recursive":
            return dict(max_chunk_size=c.max_chunk_size, min_length=c.min_length)
        elif strategy == "sentence":
            return dict(min_length=c.min_length)
        elif strategy == "token_based":
            # Tokenizer must be provided at call time or via config
            return dict(
                chunk_size=c.chunk_size, overlap=c.overlap, min_length=c.min_length
            )
        elif strategy == "sliding_window":
            return dict(
                window_size=getattr(c, "window_size", 512),
                step_size=getattr(c, "step_size", 256),
                min_length=c.min_length,
            )
        elif strategy == "custom_heuristic":
            return dict(
                delimiter=getattr(c, "delimiter", "\n---\n"),
                min_length=c.min_length,
                rules=getattr(c, "rules", None),
            )
        return {}


# Example usage:
# config = ChunkingConfig(chunk_size=512, overlap=32, strategy="fixed", min_length=128)
# chunker = Chunker(config)
# chunks = chunker.chunk("Some long text...")
