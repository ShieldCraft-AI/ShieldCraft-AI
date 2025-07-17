import pytest
from ai_core.chunking import Chunker, ChunkingConfig


class TestChunker:
    def test_fixed_chunk_happy_path(self):
        config = ChunkingConfig(chunk_size=5, overlap=2, strategy="fixed", min_length=2)
        chunker = Chunker(config)
        text = "abcdefghij"
        chunks = chunker.chunk(text)
        # Expect chunks: ['abcde', 'cdefg', 'efghi', 'ghij']
        assert chunks == ["abcde", "cdefg", "efghi", "ghij"]

    def test_empty_input(self):
        config = ChunkingConfig(chunk_size=5, overlap=2, strategy="fixed", min_length=2)
        chunker = Chunker(config)
        with pytest.raises(ValueError):
            chunker.chunk("")

    def test_invalid_chunk_size(self):
        config = ChunkingConfig(chunk_size=0, overlap=0, strategy="fixed", min_length=2)
        chunker = Chunker(config)
        with pytest.raises(ValueError):
            chunker.chunk("abcdef")

    def test_min_length(self):
        config = ChunkingConfig(chunk_size=3, overlap=1, strategy="fixed", min_length=3)
        chunker = Chunker(config)
        text = "abcdefg"
        chunks = chunker.chunk(text)
        # Only chunks of length >= 3
        assert all(len(chunk) >= 3 for chunk in chunks)

    def test_strategy_not_implemented(self):
        config = ChunkingConfig(
            chunk_size=5, overlap=2, strategy="semantic", min_length=2
        )
        chunker = Chunker(config)
        with pytest.raises(NotImplementedError):
            chunker.chunk("abcdefg")

    def test_overlap_greater_than_size(self):
        config = ChunkingConfig(chunk_size=3, overlap=5, strategy="fixed", min_length=1)
        chunker = Chunker(config)
        text = "abcdef"
        chunks = chunker.chunk(text)
        # Should not get stuck in infinite loop
        assert isinstance(chunks, list)

    def test_non_string_input(self):
        config = ChunkingConfig(chunk_size=3, overlap=1, strategy="fixed", min_length=1)
        chunker = Chunker(config)
        with pytest.raises(ValueError):
            chunker.chunk(None)
        with pytest.raises(ValueError):
            chunker.chunk(123)
