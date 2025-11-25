from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Sequence


CLI_VERSION = "0.1.0"


@dataclass(frozen=True)
class ShieldcraftMetadata:
    name: str = "ShieldCraft CLI"
    version: str = CLI_VERSION
    description: str = "Deterministic CLI surface for ShieldCraft AI platform context."
    docs_url: str = "https://shieldcraft-ai/docs"

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "docs_url": self.docs_url,
        }


def _normalize_args(argv: Iterable[str]) -> List[str]:
    return list(argv)


def run_cli(argv: Iterable[str] | None = None) -> int:
    args = _normalize_args(argv or [])
    if not args:
        _print_help()
        return 0

    if args in (["--help"], ["-h"]):
        _print_help()
        return 0

    if args == ["--version"]:
        print(CLI_VERSION)
        return 0

    command, *options = args
    handler = _COMMANDS.get(command)
    if handler is None:
        _print_help()
        return 1
    return handler(options)


def _print_help() -> None:
    print(
        """ShieldCraft CLI

Usage:
  shieldcraft info [--json]   Display platform metadata.
  shieldcraft --version       Show CLI version.
  shieldcraft --help          Show this help text.
""".strip()
    )


def _info_command(options: Sequence[str]) -> int:
    mode = "json" if options == ["--json"] else "text"
    if options and mode != "json":
        _print_help()
        return 1

    metadata = ShieldcraftMetadata()
    if mode == "json":
        print(json.dumps(metadata.to_dict(), sort_keys=True))
    else:
        print(
            f"{metadata.name}\n"
            f"Version: {metadata.version}\n"
            f"Docs: {metadata.docs_url}\n"
            f"Description: {metadata.description}"
        )
    return 0


_COMMANDS: Dict[str, Callable[[Sequence[str]], int]] = {
    "info": _info_command,
}


if __name__ == "__main__":
    raise SystemExit(run_cli())
