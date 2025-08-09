import pytest
from ai_core.chunking.chunking import Chunker, ChunkingConfig


def test_fixed_chunk_happy_path():
    config = ChunkingConfig(chunk_size=5, overlap=2, strategy="fixed", min_length=2)
    chunker = Chunker(config)
    text = "abcdefghij"
    chunks = chunker.chunk(text)
    assert [c.text for c in chunks] == ["abcde", "defgh", "ghij"]


def test_empty_input():
    config = ChunkingConfig(chunk_size=5, overlap=2, strategy="fixed", min_length=2)
    chunker = Chunker(config)
    with pytest.raises(ValueError):
        chunker.chunk("")


def test_invalid_chunk_size():
    with pytest.raises(Exception):
        ChunkingConfig(chunk_size=0, overlap=0, strategy="fixed", min_length=2)


def test_min_length():
    config = ChunkingConfig(chunk_size=3, overlap=1, strategy="fixed", min_length=3)
    chunker = Chunker(config)
    text = "abcdefg"
    chunks = chunker.chunk(text)
    assert all(len(chunk.text) >= 3 for chunk in chunks)


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
    assert [c.text for c in chunks] == ["para1", "para2", "para3"]


def test_semantic_chunking_min_length():
    config = ChunkingConfig(
        strategy="semantic", paragraph_delimiter="\n\n", min_length=6
    )
    chunker = Chunker(config)
    text = "short\n\nlongenough"
    chunks = chunker.chunk(text)
    assert [c.text for c in chunks] == ["longenough"]


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
    assert all(len(c.text) <= 10 for c in chunks)
    assert any("short" in c.text for c in chunks)


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


# --- Supplemental/Advanced/Edge Case Tests ---
def test_fixed_chunking_overlap_equals_size():
    config = ChunkingConfig(chunk_size=4, overlap=4, strategy="fixed", min_length=1)
    chunker = Chunker(config)
    text = "abcdefgh"
    chunks = chunker.chunk(text)
    # Should produce two non-overlapping chunks
    assert [c.text for c in chunks] == ["abcd", "efgh"]


def test_fixed_chunking_overlap_greater_than_size():
    config = ChunkingConfig(chunk_size=3, overlap=5, strategy="fixed", min_length=1)
    chunker = Chunker(config)
    text = "abcdef"
    chunks = chunker.chunk(text)
    # Should not error, should step by chunk_size
    assert [c.text for c in chunks] == ["abc", "def"]


def test_semantic_chunking_empty_paragraphs():
    config = ChunkingConfig(strategy="semantic", min_length=1)
    chunker = Chunker(config)
    text = "\n\npara1\n\n\n\npara2\n\n"
    chunks = chunker.chunk(text)
    assert [c.text for c in chunks] == ["para1", "para2"]


def test_sentence_chunking_multiple_punctuations():
    config = ChunkingConfig(strategy="sentence", min_length=1)
    chunker = Chunker(config)
    text = "Wow!! Really? Yes."
    chunks = chunker.chunk(text)
    assert [c.text for c in chunks] == ["Wow!!", "Really?", "Yes."]


def test_token_based_chunking_min_length():
    class DummyTokenizer:
        def __call__(self, text):
            return text.split()

        def decode(self, tokens):
            return " ".join(tokens)

    config = ChunkingConfig(
        strategy="token_based", chunk_size=2, overlap=0, min_length=3
    )
    chunker = Chunker(config)
    text = "a b c d"
    chunks = chunker.chunk(text, tokenizer=DummyTokenizer())
    # No chunk should meet min_length > chunk_size
    assert [c.text for c in chunks] == []


def test_sliding_window_chunking_step_larger_than_text():
    config = ChunkingConfig(strategy="sliding_window", min_length=1)
    chunker = Chunker(config)
    text = "abc"
    chunks = chunker.chunk(text, window_size=2, step_size=10)
    assert [c.text for c in chunks] == ["ab"]


def test_custom_heuristic_chunking_with_rules():
    # Rules are not used in current implementation, but should not error
    config = ChunkingConfig(strategy="custom_heuristic", min_length=1)
    chunker = Chunker(config)
    text = "foo---bar---baz"
    chunks = chunker.chunk(text, delimiter="---", rules={"dummy": True})
    assert [c.text for c in chunks] == ["foo", "bar", "baz"]


def test_recursive_chunking_all_short():
    config = ChunkingConfig(strategy="recursive", max_chunk_size=100, min_length=1)
    chunker = Chunker(config)
    text = "short1\n\nshort2"
    chunks = chunker.chunk(text)
    assert [c.text for c in chunks] == ["short1", "short2"]


def test_recursive_chunking_all_long():
    config = ChunkingConfig(strategy="recursive", max_chunk_size=3, min_length=1)
    chunker = Chunker(config)
    text = "abcdefghi\n\njklmnopqr"
    chunks = chunker.chunk(text)
    # Each paragraph is split into fixed chunks of size 3
    assert [c.text for c in chunks] == ["abc", "def", "ghi", "jkl", "mno", "pqr"]


def test_chunker_invalid_strategy():
    config = ChunkingConfig(strategy="not_a_strategy", min_length=1)
    chunker = Chunker(config)
    with pytest.raises(NotImplementedError):
        chunker.chunk("foo")


def test_chunker_empty_string():
    config = ChunkingConfig(strategy="fixed", chunk_size=3, overlap=1, min_length=1)
    chunker = Chunker(config)
    with pytest.raises(ValueError):
        chunker.chunk("")


def test_chunker_non_string():
    config = ChunkingConfig(strategy="fixed", chunk_size=3, overlap=1, min_length=1)
    chunker = Chunker(config)
    with pytest.raises(ValueError):
        chunker.chunk(None)
