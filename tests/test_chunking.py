import pytest
from ai_core.chunking.chunking import Chunker, ChunkingConfig


def test_fixed_chunk_happy_path():
    config = ChunkingConfig(chunk_size=5, overlap=2, strategy="fixed", min_length=2)
    chunker = Chunker(config)
    text = "abcdefghij"
    chunks = chunker.chunk(text)
    assert chunks == ["abcde", "cdefg", "efghi", "ghij"]


def test_empty_input():
    config = ChunkingConfig(chunk_size=5, overlap=2, strategy="fixed", min_length=2)
    chunker = Chunker(config)
    with pytest.raises(ValueError):
        chunker.chunk("")


def test_invalid_chunk_size():
    config = ChunkingConfig(chunk_size=0, overlap=0, strategy="fixed", min_length=2)
    chunker = Chunker(config)
    with pytest.raises(ValueError):
        chunker.chunk("abcdef")


def test_min_length():
    config = ChunkingConfig(chunk_size=3, overlap=1, strategy="fixed", min_length=3)
    chunker = Chunker(config)
    text = "abcdefg"
    chunks = chunker.chunk(text)
    assert all(len(chunk) >= 3 for chunk in chunks)


def test_overlap_greater_than_size():
    config = ChunkingConfig(chunk_size=3, overlap=5, strategy="fixed", min_length=1)
    chunker = Chunker(config)
    text = "abcdef"
    chunks = chunker.chunk(text)
    assert isinstance(chunks, list)


def test_non_string_input():
    config = ChunkingConfig(chunk_size=3, overlap=1, strategy="fixed", min_length=1)
    chunker = Chunker(config)
    with pytest.raises(ValueError):
        chunker.chunk(None)
    with pytest.raises(ValueError):
        chunker.chunk(123)


def test_semantic_chunking_happy_path():
    config = ChunkingConfig(
        strategy="semantic", paragraph_delimiter="\n\n", min_length=1
    )
    chunker = Chunker(config)
    text = "para1\n\npara2\n\npara3"
    chunks = chunker.chunk(text)
    assert chunks == ["para1", "para2", "para3"]


def test_semantic_chunking_min_length():
    config = ChunkingConfig(
        strategy="semantic", paragraph_delimiter="\n\n", min_length=6
    )
    chunker = Chunker(config)
    text = "short\n\nlongenough"
    chunks = chunker.chunk(text)
    assert chunks == ["longenough"]


def test_recursive_chunking_fallback():
    config = ChunkingConfig(
        strategy="recursive",
        paragraph_delimiter="\n\n",
        max_chunk_size=10,
        min_length=1,
        chunk_size=5,
        overlap=0,
    )
    chunker = Chunker(config)
    text = "A very long paragraph that should be split.\n\nshort"
    chunks = chunker.chunk(text)
    # The first paragraph is long, so should be split into fixed chunks of size 5
    assert all(len(c) <= 10 for c in chunks)
    assert "short" in chunks


def test_sentence_chunking_happy_path():
    config = ChunkingConfig(strategy="sentence", min_length=1)
    chunker = Chunker(config)
    text = "Hello world! How are you? I am fine."
    chunks = chunker.chunk(text)
    assert [c.text for c in chunks] == ["Hello world!", "How are you?", "I am fine."]


def test_sentence_chunking_empty():
    config = ChunkingConfig(strategy="sentence", min_length=1)
    chunker = Chunker(config)
    with pytest.raises(ValueError):
        chunker.chunk("")


def test_token_based_chunking_happy_path():
    class DummyTokenizer:
        def __call__(self, text):
            return text.split()

        def decode(self, tokens):
            return " ".join(tokens)

    config = ChunkingConfig(
        strategy="token_based", chunk_size=2, overlap=0, min_length=1
    )
    chunker = Chunker(config)
    text = "a b c d"
    chunks = chunker.chunk(text, tokenizer=DummyTokenizer())
    assert [c.text for c in chunks] == ["a b", "c d"]


def test_token_based_chunking_invalid_tokenizer():
    config = ChunkingConfig(
        strategy="token_based", chunk_size=2, overlap=0, min_length=1
    )
    chunker = Chunker(config)
    with pytest.raises(ValueError):
        chunker.chunk("a b c d", tokenizer=None)


def test_sliding_window_chunking_happy_path():
    config = ChunkingConfig(strategy="sliding_window", min_length=2)
    chunker = Chunker(config)
    text = "abcdefghij"
    chunks = chunker.chunk(text, window_size=4, step_size=2)
    assert [c.text for c in chunks][:2] == ["abcd", "cdef"]


def test_sliding_window_chunking_empty():
    config = ChunkingConfig(strategy="sliding_window", min_length=1)
    chunker = Chunker(config)
    with pytest.raises(ValueError):
        chunker.chunk("")


def test_custom_heuristic_chunking_happy_path():
    config = ChunkingConfig(strategy="custom_heuristic", min_length=2)
    chunker = Chunker(config)
    text = "section1\n---\nsection2\n---\nsection3"
    chunks = chunker.chunk(text, delimiter="\n---\n")
    assert [c.text for c in chunks] == ["section1", "section2", "section3"]


def test_custom_heuristic_chunking_empty():
    config = ChunkingConfig(strategy="custom_heuristic", min_length=1)
    chunker = Chunker(config)
    with pytest.raises(ValueError):
        chunker.chunk("")
