from __future__ import annotations

import json

import pytest

from src.cli import run_cli
from src.cli.main import ShieldcraftMetadata


def test_run_cli_importable():
    assert callable(run_cli)


@pytest.mark.parametrize(
    "argv",
    [[], ["--help"]],
)
def test_help_invocations(argv: list[str], capsys: pytest.CaptureFixture[str]):
    exit_code = run_cli(argv)
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Usage" in captured.out


def test_version_flag_outputs_current_version(capsys: pytest.CaptureFixture[str]):
    exit_code = run_cli(["--version"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out.strip() == ShieldcraftMetadata().version


def test_info_json_mode_returns_deterministic_payload(
    capsys: pytest.CaptureFixture[str],
):
    exit_code = run_cli(["info", "--json"])
    captured = capsys.readouterr()
    assert exit_code == 0

    payload = json.loads(captured.out.strip())
    assert payload == ShieldcraftMetadata().to_dict()
    assert list(payload.keys()) == sorted(payload.keys())


def test_unknown_command_returns_help(capsys: pytest.CaptureFixture[str]):
    exit_code = run_cli(["unknown"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Usage" in captured.out
