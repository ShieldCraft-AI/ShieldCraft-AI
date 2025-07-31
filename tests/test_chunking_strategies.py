"""
Unit tests for chunking strategies in ai_core.chunking.chunk
"""

import pytest
from ai_core.chunking.chunk import (
    FixedChunkingStrategy,
    SemanticChunkingStrategy,
    RecursiveChunkingStrategy,
    SentenceChunkingStrategy,
    TokenBasedChunkingStrategy,
    SlidingWindowChunkingStrategy,
    CustomHeuristicChunkingStrategy,
    Chunk,
)


def test_fixed_chunking():
    text = "abcdefghij"
    strategy = FixedChunkingStrategy(chunk_size=3, overlap=1, min_length=2)
    chunks = strategy.chunk(text)
    assert len(chunks) > 0
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].text == "abc"
    assert chunks[1].text == "bcd"


def test_semantic_chunking():
    text = "para1\n\npara2\n\npara3"
    strategy = SemanticChunkingStrategy()
    chunks = strategy.chunk(text)
    assert len(chunks) == 3
    assert chunks[0].text == "para1"
    assert chunks[1].text == "para2"
    assert chunks[2].text == "para3"


def test_recursive_chunking():
    text = "A long paragraph. " * 50  # Should trigger fallback
    strategy = RecursiveChunkingStrategy(max_chunk_size=30, min_length=5)
    chunks = strategy.chunk(text)
    assert all(len(c.text) <= 30 for c in chunks)
    assert all(isinstance(c, Chunk) for c in chunks)


def test_sentence_chunking():
    text = "Hello world! How are you? I am fine."
    strategy = SentenceChunkingStrategy()
    chunks = strategy.chunk(text)
    assert len(chunks) == 3
    assert chunks[0].text.endswith("!")
    assert chunks[1].text.endswith("?")
    assert chunks[2].text.endswith(".")


def test_token_based_chunking():
    # Dummy tokenizer: splits on space, returns list of tokens, decode joins
    class DummyTokenizer:
        def __call__(self, text):
            return text.split()

        def decode(self, tokens):
            return " ".join(tokens)

    text = "a b c d e f g h i j"
    strategy = TokenBasedChunkingStrategy(
        DummyTokenizer(), chunk_size=3, overlap=1, min_length=2
    )
    chunks = strategy.chunk(text)
    assert len(chunks) > 0
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].text == "a b c"
    assert chunks[1].text == "b c d"


def test_sliding_window_chunking():
    text = "abcdefghij"
    strategy = SlidingWindowChunkingStrategy(window_size=4, step_size=2, min_length=2)
    chunks = strategy.chunk(text)
    assert len(chunks) > 0
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].text == "abcd"
    assert chunks[1].text == "cdef"


def test_custom_heuristic_chunking():
    text = "section1\n---\nsection2\n---\nsection3"
    strategy = CustomHeuristicChunkingStrategy(delimiter="\n---\n")
    chunks = strategy.chunk(text)
    assert len(chunks) == 3
    assert chunks[0].text == "section1"
    assert chunks[1].text == "section2"
    assert chunks[2].text == "section3"


@pytest.mark.parametrize(
    "strategy_cls",
    [
        FixedChunkingStrategy,
        SemanticChunkingStrategy,
        RecursiveChunkingStrategy,
        SentenceChunkingStrategy,
        SlidingWindowChunkingStrategy,
        CustomHeuristicChunkingStrategy,
    ],
)
def test_empty_input(strategy_cls):
    if strategy_cls is TokenBasedChunkingStrategy:
        return  # skip, needs tokenizer
    strategy = (
        strategy_cls()
        if strategy_cls is not RecursiveChunkingStrategy
        else strategy_cls(max_chunk_size=10)
    )
    with pytest.raises(ValueError):
        strategy.chunk("")
