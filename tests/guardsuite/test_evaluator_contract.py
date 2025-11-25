"""GuardSuite evaluator scaffolding is not tracked inside ShieldCraft-AI.

These tests remain as placeholders to remind us that the GuardSuite pillar work lives in
its own repository. Mark them as skipped at collection time so pytest does not try to
import nonexistent modules.
"""

import pytest


pytest.skip(
    "GuardSuite evaluator components are maintained outside this repo.",
    allow_module_level=True,
)
