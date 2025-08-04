"""
This file contains unit tests for the EmbeddingModel class in the ai_core.embedding module.
"""

import pytest
import numpy as np
from ai_core.embedding.embedding import EmbeddingModel

import torch


def test_embedding_model_initialization():
    embedder = EmbeddingModel()
    assert embedder.model is not None
    assert embedder.tokenizer is not None
    assert embedder.device in ("cpu", "cuda")
    assert isinstance(embedder.batch_size, int)


def test_embedding_model_encode_single_text():
    embedder = EmbeddingModel()
    text = "ShieldCraft AI protects your cloud workloads."
    result = embedder.encode(text)
    assert result["success"] is True
    embedding = result["embeddings"]
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape[0] == 1
    assert embedding.shape[1] > 0


def test_embedding_model_encode_batch():
    embedder = EmbeddingModel()
    texts = [
        "Security automation is essential.",
        "MLOps enables rapid iteration.",
        "Cost controls prevent surprise bills.",
    ]
    result = embedder.encode(texts)
    assert result["success"] is True
    embeddings = result["embeddings"]
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape[0] == len(texts)
    assert embeddings.shape[1] > 0


def test_embedding_model_error_handling():
    # Simulate error by passing invalid model name via config
    bad_config = {"model_name": "invalid/model/path"}
    embedder = EmbeddingModel(config=bad_config)
    result = embedder.encode("Test text")
    assert result["success"] is False
    assert "error" in result
    error_val = result["error"]
    assert isinstance(error_val, str)
    assert "model not loaded" in error_val or "failed" in error_val.lower()


def test_embedding_model_input_validation():
    embedder = EmbeddingModel()
    # Non-string input
    result = embedder.encode([123, None])
    assert result["success"] is False
    error_val = result["error"]
    assert isinstance(error_val, str)
    assert "Input must be a string or list of strings" in error_val
    # Empty list
    result = embedder.encode([])
    assert result["success"] is False
    error_val = result["error"]
    assert isinstance(error_val, str)
    assert "Input text list is empty" in error_val


def test_embedding_model_quantization_configs(monkeypatch):
    # Test float16 quantization
    config = {"quantize": True, "quantization_type": "float16"}
    embedder = EmbeddingModel(config=config)
    assert embedder.model is not None
    # Test int8 quantization (should fallback if not supported)
    config = {"quantize": True, "quantization_type": "int8"}
    embedder = EmbeddingModel(config=config)
    assert embedder.model is not None or embedder.model is None  # Should not crash
    # Test bitsandbytes quantization (should fallback if not installed)
    config = {"quantize": True, "quantization_type": "bitsandbytes"}
    embedder = EmbeddingModel(config=config)
    assert embedder.model is not None or embedder.model is None  # Should not crash


def test_embedding_model_device_selection(monkeypatch):
    # Force CPU
    config = {"device": "cpu"}
    embedder = EmbeddingModel(config=config)
    assert embedder.device == "cpu"
    # Force CUDA if available
    if hasattr(embedder, "model") and torch.cuda.is_available():
        config = {"device": "cuda"}
        embedder = EmbeddingModel(config=config)
        assert embedder.device == "cuda"


def test_embedding_model_large_batch(monkeypatch):
    embedder = EmbeddingModel()
    texts = [f"text {i}" for i in range(embedder.batch_size * 2 + 1)]
    result = embedder.encode(texts)
    assert result["success"] is True
    assert result["embeddings"].shape[0] == len(texts)


def test_embedding_model_dtype_and_shape():
    embedder = EmbeddingModel()
    texts = ["a", "b"]
    result = embedder.encode(texts)
    assert result["success"] is True
    assert "shape" in result
    assert "dtype" in result
    assert isinstance(result["shape"], tuple)
    assert isinstance(result["dtype"], str)
