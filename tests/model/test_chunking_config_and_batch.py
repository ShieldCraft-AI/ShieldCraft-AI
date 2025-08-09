"""
Test suite for chunking strategies.
"""

import pytest
from ai_core.chunking.chunk import (
    Chunker,
    get_chunking_strategy_from_config,
    FixedChunkingStrategy,
    SemanticChunkingStrategy,
    RecursiveChunkingStrategy,
    SentenceChunkingStrategy,
    TokenBasedChunkingStrategy,
    SlidingWindowChunkingStrategy,
    CustomHeuristicChunkingStrategy,
    Chunk,
)


# --- Config-driven tests ---
def test_strategy_selection_and_params(monkeypatch):
    # Patch config loader to return a custom config
    class DummyConfigLoader:
        def get_section(self, section):
            return {
                "strategy": "fixed",
                "fixed": {"chunk_size": 5, "overlap": 2, "min_length": 2},
            }

    monkeypatch.setattr(
        "ai_core.chunking.chunk.get_config_loader", lambda: DummyConfigLoader()
    )
    strategy_class, params = get_chunking_strategy_from_config()
    assert strategy_class is FixedChunkingStrategy
    assert params == {"chunk_size": 5, "overlap": 2, "min_length": 2}


# --- Validation tests ---
def test_missing_strategy_block(monkeypatch):
    class DummyConfigLoader:
        def get_section(self, section):
            return {"strategy": "fixed"}  # missing 'fixed' block

    monkeypatch.setattr(
        "ai_core.chunking.chunk.get_config_loader", lambda: DummyConfigLoader()
    )
    with pytest.raises(ValueError):
        get_chunking_strategy_from_config()


def test_missing_required_params(monkeypatch):
    class DummyConfigLoader:
        def get_section(self, section):
            return {"strategy": "fixed", "fixed": {"chunk_size": 5}}

    monkeypatch.setattr(
        "ai_core.chunking.chunk.get_config_loader", lambda: DummyConfigLoader()
    )
    with pytest.raises(ValueError):
        get_chunking_strategy_from_config()


# --- Batch API tests ---
def test_chunk_batch_parallel(monkeypatch):
    # Use fixed strategy with small chunks
    class DummyConfigLoader:
        def get_section(self, section):
            return {
                "strategy": "fixed",
                "fixed": {"chunk_size": 2, "overlap": 0, "min_length": 1},
            }

    monkeypatch.setattr(
        "ai_core.chunking.chunk.get_config_loader", lambda: DummyConfigLoader()
    )
    chunker = Chunker()
    texts = ["abcdef", "ghijkl", "mnopqr"]
    doc_ids = ["doc1", "doc2", "doc3"]
    results = chunker.chunk_batch(texts, doc_ids, max_workers=2)
    assert len(results) == 3
    for chunks in results:
        assert all(isinstance(c, Chunk) for c in chunks)


# --- Edge case tests ---
def test_chunk_batch_empty(monkeypatch):
    class DummyConfigLoader:
        def get_section(self, section):
            return {
                "strategy": "fixed",
                "fixed": {"chunk_size": 2, "overlap": 0, "min_length": 1},
            }

    monkeypatch.setattr(
        "ai_core.chunking.chunk.get_config_loader", lambda: DummyConfigLoader()
    )
    chunker = Chunker()
    results = chunker.chunk_batch([], [])
    assert results == []


def test_chunk_batch_docid_length_mismatch(monkeypatch):
    class DummyConfigLoader:
        def get_section(self, section):
            return {
                "strategy": "fixed",
                "fixed": {"chunk_size": 2, "overlap": 0, "min_length": 1},
            }

    monkeypatch.setattr(
        "ai_core.chunking.chunk.get_config_loader", lambda: DummyConfigLoader()
    )
    chunker = Chunker()
    with pytest.raises(ValueError):
        chunker.chunk_batch(["abc", "def"], ["doc1"])  # mismatch


# --- Strategy-specific parameter passing ---
def test_token_based_chunking_param_passing(monkeypatch):
    class DummyTokenizer:
        def __call__(self, text):
            return text.split()

        def decode(self, tokens):
            return " ".join(tokens)

    class DummyConfigLoader:
        def get_section(self, section):
            return {
                "strategy": "token_based",
                "token_based": {
                    "chunk_size": 2,
                    "overlap": 0,
                    "min_length": 1,
                    "tokenizer": DummyTokenizer(),
                },
            }

    monkeypatch.setattr(
        "ai_core.chunking.chunk.get_config_loader", lambda: DummyConfigLoader()
    )
    chunker = Chunker()
    chunks = chunker.chunk("a b c d", doc_id="docX")
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].text == "a b"
    assert chunks[1].text == "c d"


# --- Test all strategies from config ---
import itertools


@pytest.mark.parametrize(
    "strategy,params,text,expected_count",
    [
        ("fixed", {"chunk_size": 3, "overlap": 1, "min_length": 2}, "abcdef", 3),
        ("semantic", {"min_length": 2}, "para1\n\npara2", 2),
        ("recursive", {"max_chunk_size": 3, "min_length": 2}, "para1\n\npara2", 4),
        ("sentence", {"min_length": 2}, "A. B! C?", 3),
        (
            "token_based",
            {
                "chunk_size": 2,
                "overlap": 0,
                "min_length": 1,
                "tokenizer": lambda t: t.split(),
            },
            "a b c d",
            2,
        ),
        (
            "sliding_window",
            {"window_size": 3, "step_size": 2, "min_length": 2},
            "abcdef",
            3,
        ),
        (
            "custom_heuristic",
            {"delimiter": "-", "min_length": 1, "rules": {}},
            "a-b-c",
            3,
        ),
    ],
)
def test_all_strategies(monkeypatch, strategy, params, text, expected_count):
    class DummyConfigLoader:
        def get_section(self, section):
            return {"strategy": strategy, strategy: params}

    monkeypatch.setattr(
        "ai_core.chunking.chunk.get_config_loader", lambda: DummyConfigLoader()
    )
    chunker = Chunker()
    chunks = chunker.chunk(text)
    assert len(chunks) == expected_count
    assert all(isinstance(c, Chunk) for c in chunks)


# --- Test __str__ and __repr__ ---
def test_chunk_str_repr():
    c = Chunk(text="abc", doc_id="d1", chunk_index=1, start_offset=0, end_offset=3)
    s = str(c)
    r = repr(c)
    assert "Chunk(doc_id=d1" in s
    assert s == r


# --- Direct tests for all chunking strategies ---
def test_semantic_chunking():
    text = "para1\n\npara2\n\npara3"
    chunks = SemanticChunkingStrategy.chunk(text)
    assert len(chunks) == 3
    assert chunks[0].text == "para1"
    assert chunks[1].text == "para2"
    assert chunks[2].text == "para3"


def test_semantic_chunking_empty():
    with pytest.raises(ValueError):
        SemanticChunkingStrategy.chunk("")


def test_recursive_chunking():
    text = "A long paragraph. " * 20
    chunks = RecursiveChunkingStrategy.chunk(text, max_chunk_size=30, min_length=5)
    assert all(len(c.text) <= 30 for c in chunks)
    assert all(isinstance(c, Chunk) for c in chunks)


def test_sentence_chunking():
    text = "Hello world! How are you? I am fine."
    chunks = SentenceChunkingStrategy.chunk(text)
    assert len(chunks) == 3
    assert chunks[0].text.endswith("!")
    assert chunks[1].text.endswith("?")
    assert chunks[2].text.endswith(".")


def test_sentence_chunking_empty():
    with pytest.raises(ValueError):
        SentenceChunkingStrategy.chunk("")


def test_token_based_chunking():
    class DummyTokenizer:
        def __call__(self, text):
            return text.split()

        def decode(self, tokens):
            return " ".join(tokens)

    text = "a b c d e f g h i j"
    chunks = TokenBasedChunkingStrategy.chunk(
        text, tokenizer=DummyTokenizer(), chunk_size=3, overlap=1, min_length=2
    )
    assert len(chunks) > 0
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].text == "a b c"
    assert chunks[1].text == "c d e"


def test_token_based_chunking_invalid_tokenizer():
    with pytest.raises(ValueError):
        TokenBasedChunkingStrategy.chunk("abc", tokenizer=None)


def test_sliding_window_chunking():
    text = "abcdefghij"
    chunks = SlidingWindowChunkingStrategy.chunk(
        text, window_size=4, step_size=2, min_length=2
    )
    assert len(chunks) > 0
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].text == "abcd"
    assert chunks[1].text == "cdef"


def test_sliding_window_chunking_empty():
    with pytest.raises(ValueError):
        SlidingWindowChunkingStrategy.chunk("")


def test_custom_heuristic_chunking():
    text = "section1\n---\nsection2\n---\nsection3"
    chunks = CustomHeuristicChunkingStrategy.chunk(text, delimiter="\n---\n")
    assert len(chunks) == 3
    assert chunks[0].text == "section1"
    assert chunks[1].text == "section2"
    assert chunks[2].text == "section3"


def test_custom_heuristic_chunking_empty():
    with pytest.raises(ValueError):
        CustomHeuristicChunkingStrategy.chunk("")
