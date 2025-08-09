"""
Unit tests for BEIR Lambda handler
"""
import json
import pytest
from lambda.beir_benchmark.handler import handler

class DummyContext:
    pass

def test_handler_happy_path(monkeypatch):
    # Mock run_beir to return a success result
    def mock_run_beir(**kwargs):
        return {"results": {"scifact": {"nDCG": 0.8}}, "errors": {}}
    monkeypatch.setattr("lambda.beir_benchmark.handler.run_beir", mock_run_beir)
    event = {
        "datasets": ["scifact"],
        "data_path": "./beir_datasets",
        "output_path": "/tmp/beir_results.json",
        "batch_size": 32,
    }
    response = handler(event, DummyContext())
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "results" in body
    assert body["results"]["scifact"]["nDCG"] == 0.8

def test_handler_unhappy_path(monkeypatch):
    # Mock run_beir to raise an exception
    def mock_run_beir(**kwargs):
        raise RuntimeError("Benchmark failed")
    monkeypatch.setattr("lambda.beir_benchmark.handler.run_beir", mock_run_beir)
    event = {"datasets": ["scifact"]}
    response = handler(event, DummyContext())
    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert "error" in body
    assert body["error"] == "Benchmark failed"
