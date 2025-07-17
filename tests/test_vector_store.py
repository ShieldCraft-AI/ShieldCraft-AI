import pytest
import numpy as np
from ai_core.vector_store import VectorStore


def test_vector_store_initialization():
    store = VectorStore()
    assert store.conn is not None
    assert isinstance(store.table_name, str)


def test_vector_store_upsert_and_query(monkeypatch):
    # Mock connection and cursor for safe CI/dev testing
    class DummyCursor:
        def execute(self, *args, **kwargs):
            pass

        def fetchall(self):
            return [("test text", np.zeros(384))]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class DummyConn:
        def cursor(self):
            return DummyCursor()

        def commit(self):
            pass

    store = VectorStore()
    store.conn = DummyConn()
    texts = ["test text"]
    embeddings = np.zeros((1, 384))
    result = store.upsert_embeddings(texts, embeddings)
    assert result is None or "ERROR" not in str(result)
    results = store.query(embeddings[0], top_k=1)
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0][0] == "test text"


def test_vector_store_error_handling():
    store = VectorStore()
    store.conn = None
    result = store.upsert_embeddings(["text"], np.zeros((1, 384)))
    assert "ERROR" in str(result)
    result = store.query(np.zeros(384), top_k=1)
    assert "ERROR" in str(result)
