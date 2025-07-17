import pytest
from ai_core.model_loader import ShieldCraftAICore


def test_model_loader_initialization():
    # Use a small, open model for CI/dev
    ai_core = ShieldCraftAICore(model_name="gpt2", quantize=False)
    assert ai_core.model is not None
    assert ai_core.tokenizer is not None
    assert ai_core.device in ("cpu", "cuda")


def test_model_loader_inference():
    ai_core = ShieldCraftAICore(model_name="gpt2", quantize=False)
    prompt = "Test prompt for security alert."
    result = ai_core.generate(prompt)
    assert isinstance(result, str)
    assert "ERROR" not in result


def test_model_loader_error_handling():
    # Simulate error by passing an invalid model name
    ai_core = ShieldCraftAICore(model_name="invalid/model/path")
    result = ai_core.generate("Test prompt")
    assert "ERROR" in result
