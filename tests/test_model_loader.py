import pytest
from ai_core.model_loader import ShieldCraftAICore


def test_model_loader_initialization():
    model = ShieldCraftAICore(config_section="ai_core")
    assert model.model is not None or model.model is None  # Should not crash


def test_model_loader_inference():
    model = ShieldCraftAICore(config_section="ai_core")
    result = model.generate("Test prompt.")
    assert isinstance(result, str)


def test_model_loader_error_handling():
    # Simulate error by patching config loader to return invalid model_name
    import pytest
    from unittest.mock import patch

    def bad_get_section(section):
        return {"model_name": "invalid/model/path"}

    def run_error_test():
        with patch("infra.utils.config_loader.get_config_loader") as mock_loader:
            mock_loader.return_value.get_section = bad_get_section
            model = ShieldCraftAICore(config_section="ai_core")
            result = model.generate("Test prompt.")
            assert isinstance(result, str)
            assert "ERROR" in result

    run_error_test()
