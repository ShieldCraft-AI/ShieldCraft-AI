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
    chunks = FixedChunkingStrategy.chunk(text, chunk_size=3, overlap=1, min_length=2)
    assert len(chunks) > 0
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].text == "abc"
    assert chunks[1].text == "cde"


def test_fixed_chunking_min_length():
    text = "abcdefghij"
    # min_length greater than chunk_size, should skip all
    chunks = FixedChunkingStrategy.chunk(text, chunk_size=3, overlap=1, min_length=10)
    assert chunks == []


def test_fixed_chunking_overlap_gt_chunk_size():
    text = "abcdefghij"
    # overlap > chunk_size, should fallback to chunk_size step
    chunks = FixedChunkingStrategy.chunk(text, chunk_size=3, overlap=5, min_length=2)
    assert all(isinstance(c, Chunk) for c in chunks)
    # Should not error, should still produce chunks
    assert len(chunks) > 0


def test_semantic_chunking():
    text = "para1\n\npara2\n\npara3"
    chunks = SemanticChunkingStrategy.chunk(text)
    assert len(chunks) == 3
    assert chunks[0].text == "para1"
    assert chunks[1].text == "para2"
    assert chunks[2].text == "para3"


def test_semantic_chunking_min_length():
    text = "short\n\nlongenough"
    chunks = SemanticChunkingStrategy.chunk(text, min_length=8)
    assert len(chunks) == 1
    assert chunks[0].text == "longenough"


def test_semantic_chunking_whitespace_paragraphs():
    text = "\n\n   \n\nrealpara"
    chunks = SemanticChunkingStrategy.chunk(text)
    assert len(chunks) == 1
    assert chunks[0].text == "realpara"


def test_recursive_chunking():
    text = "A long paragraph. " * 50  # Should trigger fallback
    chunks = RecursiveChunkingStrategy.chunk(text, max_chunk_size=30, min_length=5)
    assert all(len(c.text) <= 30 for c in chunks)
    assert all(isinstance(c, Chunk) for c in chunks)


def test_recursive_chunking_all_large():
    text = ("A long paragraph. " * 100).strip()
    # All paragraphs too large, should fallback to fixed
    chunks = RecursiveChunkingStrategy.chunk(text, max_chunk_size=20, min_length=5)
    assert all(len(c.text) <= 20 for c in chunks)
    assert all(isinstance(c, Chunk) for c in chunks)


def test_sentence_chunking():
    text = "Hello world! How are you? I am fine."
    chunks = SentenceChunkingStrategy.chunk(text)
    assert len(chunks) == 3
    assert chunks[0].text.endswith("!")
    assert chunks[1].text.endswith("?")
    assert chunks[2].text.endswith(".")


def test_sentence_chunking_no_delimiters():
    text = "No sentence delimiter here"
    chunks = SentenceChunkingStrategy.chunk(text)
    assert len(chunks) == 1
    assert chunks[0].text == text


def test_token_based_chunking():
    # Dummy tokenizer: splits on space, returns list of tokens, decode joins
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


def test_token_based_chunking_min_length():
    class DummyTokenizer:
        def __call__(self, text):
            return text.split()

        def decode(self, tokens):
            return " ".join(tokens)

    text = "a b c d e f g h i j"
    # min_length > chunk_size, should skip all
    chunks = TokenBasedChunkingStrategy.chunk(
        text, tokenizer=DummyTokenizer(), chunk_size=3, overlap=1, min_length=10
    )
    assert chunks == []


def test_token_based_chunking_no_decode():
    class DummyTokenizer:
        def __call__(self, text):
            return text.split()

    text = "a b c d e f"
    chunks = TokenBasedChunkingStrategy.chunk(
        text, tokenizer=DummyTokenizer(), chunk_size=2, overlap=1, min_length=1
    )
    assert all(isinstance(c, Chunk) for c in chunks)


def test_sliding_window_chunking():
    text = "abcdefghij"
    chunks = SlidingWindowChunkingStrategy.chunk(
        text, window_size=4, step_size=2, min_length=2
    )
    assert len(chunks) > 0
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].text == "abcd"
    assert chunks[1].text == "cdef"


def test_sliding_window_chunking_window_gt_text():
    text = "abc"
    # window_size > text length, should return one chunk
    chunks = SlidingWindowChunkingStrategy.chunk(
        text, window_size=10, step_size=2, min_length=1
    )
    assert len(chunks) == 1
    assert chunks[0].text == text


def test_custom_heuristic_chunking():
    text = "section1\n---\nsection2\n---\nsection3"
    chunks = CustomHeuristicChunkingStrategy.chunk(text, delimiter="\n---\n")
    assert len(chunks) == 3
    assert chunks[0].text == "section1"
    assert chunks[1].text == "section2"
    assert chunks[2].text == "section3"


def test_custom_heuristic_chunking_delimiter_not_found():
    text = "section1 section2 section3"
    # Delimiter not present, should return one chunk
    chunks = CustomHeuristicChunkingStrategy.chunk(text, delimiter="<notfound>")
    assert len(chunks) == 1
    assert chunks[0].text == text


def test_custom_heuristic_chunking_empty_delimiter():
    text = "abc"
    # Empty delimiter should treat whole text as one chunk
    chunks = CustomHeuristicChunkingStrategy.chunk(text, delimiter="")
    assert len(chunks) == 1
    assert chunks[0].text == text


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
    if strategy_cls is FixedChunkingStrategy:
        with pytest.raises(ValueError):
            FixedChunkingStrategy.chunk("")
    elif strategy_cls is SemanticChunkingStrategy:
        with pytest.raises(ValueError):
            SemanticChunkingStrategy.chunk("")
    elif strategy_cls is RecursiveChunkingStrategy:
        with pytest.raises(ValueError):
            RecursiveChunkingStrategy.chunk("", max_chunk_size=10)
    elif strategy_cls is SentenceChunkingStrategy:
        with pytest.raises(ValueError):
            SentenceChunkingStrategy.chunk("")
    elif strategy_cls is SlidingWindowChunkingStrategy:
        with pytest.raises(ValueError):
            SlidingWindowChunkingStrategy.chunk("")
    elif strategy_cls is CustomHeuristicChunkingStrategy:
        with pytest.raises(ValueError):
            CustomHeuristicChunkingStrategy.chunk("")
