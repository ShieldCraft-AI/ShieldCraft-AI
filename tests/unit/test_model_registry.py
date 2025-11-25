from __future__ import annotations

import pytest

from src.model.metadata_schema import ModelMetadata
from src.model.registry import get_model, list_models


def test_list_models_returns_sorted_metadata():
    models = list_models()

    assert all(isinstance(item, ModelMetadata) for item in models)
    model_ids = [model.model_id for model in models]
    assert model_ids == sorted(model_ids)


def test_get_model_returns_matching_entry():
    models = list_models()
    target_id = models[0].model_id

    metadata = get_model(target_id)
    assert metadata.model_id == target_id
    assert metadata.version
    assert metadata.params


def test_get_model_raises_for_missing_id():
    with pytest.raises(KeyError):
        get_model("unknown-model")
