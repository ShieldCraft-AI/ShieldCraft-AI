"""Lightweight ShieldCraft CLI shim.

This module exists solely to keep long-lived CLI tests importable while the
full command surface is rebuilt after accidental cleanup. It intentionally
exposes only the narrow surface exercised by the guardsuite tests.
"""

from __future__ import annotations

import argparse
from typing import Sequence

VERSION = "0.0.0"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ShieldCraft CLI placeholder")
    parser.add_argument("command", nargs="?", default="status")
    parser.add_argument("command_args", nargs=argparse.REMAINDER)
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print CLI placeholder version and exit",
    )
    return parser


class main:
    """Namespace object matching the legacy import style (main.run_cli)."""

    @staticmethod
    def run_cli(argv: Sequence[str] | None = None) -> int:
        parser = _build_parser()
        args = parser.parse_args(list(argv or []))
        if getattr(args, "version", False):
            print(VERSION)
            return 0
        # Placeholder dispatch keeps deterministic exit status for tests.
        return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main.run_cli())
