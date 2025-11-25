"""Placeholder tests for GuardSuite CLI contract.

TODO: Phase 3 should assert command matrix described in Phase 1.
"""

from cli import main as cli_main


def test_cli_returns_zero_in_placeholder_mode() -> None:
    """Ensure scaffolded CLI exits cleanly while unimplemented."""
    assert cli_main.run_cli([]) == 0
