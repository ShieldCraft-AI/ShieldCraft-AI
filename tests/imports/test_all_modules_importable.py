import pytest
import importlib
import pkgutil

# Test that all modules in ai_core, api, infra, data_prep can be imported without error
MODULE_DIRS = [
    "ai_core",
    "api",
    "infra",
    "data_prep",
]


@pytest.mark.parametrize("mod_dir", MODULE_DIRS)
def test_all_modules_importable(mod_dir):
    pkg = importlib.import_module(mod_dir)
    for _, name, ispkg in pkgutil.walk_packages(pkg.__path__, mod_dir + "."):
        importlib.import_module(name)
