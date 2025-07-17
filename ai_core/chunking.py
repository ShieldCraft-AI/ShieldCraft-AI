from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError


class ChunkingConfig(BaseModel):
    chunk_size: int = Field(
        ..., gt=0, description="Size of each chunk in tokens/characters"
    )
    overlap: int = Field(
        0, ge=0, description="Number of tokens/characters to overlap between chunks"
    )
    strategy: str = Field(
        "fixed", description="Chunking strategy: fixed, semantic, recursive"
    )
    min_length: int = Field(0, ge=0, description="Minimum length for a chunk")


class Chunker:
    def __init__(self, config: ChunkingConfig):
        self.config = config

    def chunk(self, text: str) -> List[str]:
        if not isinstance(text, str) or not text:
            raise ValueError("Input text must be a non-empty string.")
        if self.config.strategy == "fixed":
            return self._fixed_chunk(text)
        # Placeholder for future strategies
        raise NotImplementedError(
            f"Chunking strategy '{self.config.strategy}' not implemented."
        )

    def _fixed_chunk(self, text: str) -> List[str]:
        size = self.config.chunk_size
        overlap = self.config.overlap
        if size <= 0:
            raise ValueError("Chunk size must be positive.")
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            chunk = text[start:end]
            if len(chunk) >= self.config.min_length:
                chunks.append(chunk)
            start += size - overlap if size > overlap else size
        return chunks


# Example usage:
# config = ChunkingConfig(chunk_size=512, overlap=32, strategy="fixed", min_length=128)
# chunker = Chunker(config)
# chunks = chunker.chunk("Some long text...")
