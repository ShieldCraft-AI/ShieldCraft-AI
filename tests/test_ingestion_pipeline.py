import os
import pytest
from data_prep.ingestion_pipeline import DataIngestionPipeline


class DummyConfig:
    def get(self, key, default=None):
        defaults = {
            "source_type": "local",
            "source_path": "tests/assets/",
            "batch_size": 2,
            "allowed_extensions": [".txt", ".log"],
            "enable_chunking": False,
        }
        return defaults.get(key, default)


@pytest.fixture
def setup_test_files(tmp_path):
    test_dir = tmp_path / "assets"
    test_dir.mkdir()
    file1 = test_dir / "file1.txt"
    file2 = test_dir / "file2.log"
    file3 = test_dir / "file3.json"
    file1.write_text("test1", encoding="utf-8")
    file2.write_text("test2", encoding="utf-8")
    file3.write_text("test3", encoding="utf-8")
    return str(test_dir)


def test_list_files_local(setup_test_files, monkeypatch):
    config = DummyConfig()
    original_get = DummyConfig.get
    monkeypatch.setattr(
        config,
        "get",
        lambda k, d=None: (
            setup_test_files if k == "source_path" else original_get(config, k, d)
        ),
    )
    pipeline = DataIngestionPipeline(config=config)
    files = pipeline.list_files()
    assert len(files) == 2
    assert all(f.endswith((".txt", ".log")) for f in files)


def test_read_batch_local(setup_test_files, monkeypatch):
    config = DummyConfig()
    original_get = DummyConfig.get
    monkeypatch.setattr(
        config,
        "get",
        lambda k, d=None: (
            setup_test_files if k == "source_path" else original_get(config, k, d)
        ),
    )
    pipeline = DataIngestionPipeline(config=config)
    files = pipeline.list_files()
    batch = pipeline.read_batch(files)
    # Only .txt and .log files are included
    assert len(batch) == len(files)
    assert set(batch) == {"test1", "test2"}


def test_run_pipeline_no_files(monkeypatch):
    config = DummyConfig()
    monkeypatch.setattr(os, "listdir", lambda path: [])
    pipeline = DataIngestionPipeline(config=config)
    result = pipeline.run()
    assert result == []


def test_run_pipeline_with_files(setup_test_files, monkeypatch):
    config = DummyConfig()
    original_get = DummyConfig.get
    monkeypatch.setattr(
        config,
        "get",
        lambda k, d=None: (
            setup_test_files if k == "source_path" else original_get(config, k, d)
        ),
    )
    pipeline = DataIngestionPipeline(config=config)
    result = pipeline.run()
    # Only .txt and .log files are included
    assert len(result) == 2
    assert set(result) == {"test1", "test2"}


def test_read_batch_chunking(setup_test_files, monkeypatch):
    class ChunkingConfig:
        def __init__(self, **kwargs):
            pass

    class DummyChunk:
        def __init__(self, text):
            self.text = text

    class DummyChunker:
        def chunk(self, text):
            # Simulate chunking: one chunk per file (whole text)
            return [DummyChunk(text)]

    class ChunkingDummyConfig(DummyConfig):
        def get(self, key, default=None):
            if key == "enable_chunking":
                return True
            if key == "chunking":
                return {}
            return super().get(key, default)

    monkeypatch.setattr("ai_core.chunking.chunking.Chunker", lambda cfg: DummyChunker())
    monkeypatch.setattr(
        "ai_core.chunking.chunking.ChunkingConfig",
        lambda **kwargs: ChunkingConfig(**kwargs),
    )
    config = ChunkingDummyConfig()
    original_get = ChunkingDummyConfig.get
    monkeypatch.setattr(
        config,
        "get",
        lambda k, d=None: (
            setup_test_files if k == "source_path" else original_get(config, k, d)
        ),
    )
    pipeline = DataIngestionPipeline(config=config)
    files = pipeline.list_files()
    batch = pipeline.read_batch(files)
    # Each file's text is chunked into chars as DummyChunk objects
    chunk_texts = [c.text for c in batch]
    assert sorted(chunk_texts) == sorted(["test1", "test2"])


def test_run_pipeline_with_chunking(setup_test_files, monkeypatch):
    class ChunkingConfig:
        def __init__(self, **kwargs):
            pass

    class DummyChunk:
        def __init__(self, text):
            self.text = text

    class DummyChunker:
        def chunk(self, text):
            # Simulate chunking: one chunk per file (whole text)
            return [DummyChunk(text)]

    class ChunkingDummyConfig(DummyConfig):
        def get(self, key, default=None):
            if key == "enable_chunking":
                return True
            if key == "chunking":
                return {}
            return super().get(key, default)

    monkeypatch.setattr("ai_core.chunking.chunking.Chunker", lambda cfg: DummyChunker())
    monkeypatch.setattr(
        "ai_core.chunking.chunking.ChunkingConfig",
        lambda **kwargs: ChunkingConfig(**kwargs),
    )
    config = ChunkingDummyConfig()
    original_get = ChunkingDummyConfig.get
    monkeypatch.setattr(
        config,
        "get",
        lambda k, d=None: (
            setup_test_files if k == "source_path" else original_get(config, k, d)
        ),
    )
    pipeline = DataIngestionPipeline(config=config)
    result = pipeline.run()
    # Each file's text is chunked into chars as DummyChunk objects
    chunk_texts = [c.text for c in result]
    assert sorted(chunk_texts) == sorted(["test1", "test2"])
