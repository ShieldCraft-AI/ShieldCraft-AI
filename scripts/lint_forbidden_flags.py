"""Lint for forbidden usage of --skip-validate outside approved paths."""

from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
from typing import Iterable, Sequence

from scripts.lint.lint_events import build_event
from scripts.lint.lint_failure import fail_event, safe_emit

ALLOWED_SEGMENTS = {"tests", "docs", "docs-site", "nox_sessions/drift.py"}
SCAN_EXTENSIONS = {".py", ".md", ".sh", ".yml", ".yaml"}
FORBIDDEN_TOKEN = "--skip-validate"
TARGET_NAME = "lint_forbidden"
ENV_VERBOSE = "SHIELDCRAFT_LINT_VERBOSE"
ENV_ALLOW_QUIET = "SHIELDCRAFT_LINT_ALLOW_QUIET"


def _flag_enabled(name: str) -> bool:
    return os.environ.get(name) == "1"


def _resolve_verbose(override: bool | None = None) -> bool:
    if override is not None:
        return override
    return _flag_enabled(ENV_VERBOSE)


def _resolve_allow_quiet(override: bool | None = None) -> bool:
    if override is not None:
        return override
    return _flag_enabled(ENV_ALLOW_QUIET)


def _git_diff_files(ref: str | None = None) -> list[str]:
    args = ["git", "diff", "--name-only"]
    if ref:
        args.append(ref)
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        diagnostic = result.stderr.strip() or "git diff --name-only failed"
        raise RuntimeError(diagnostic)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _is_allowed(path: pathlib.Path) -> bool:
    relative = path.as_posix()
    if relative == "nox_sessions/drift.py":
        return True
    parts = relative.split("/")
    return any(part in ALLOWED_SEGMENTS for part in parts)


def _should_scan(path: pathlib.Path) -> bool:
    return path.suffix in SCAN_EXTENSIONS and path.exists()


def _contains_forbidden_token(path: pathlib.Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    return FORBIDDEN_TOKEN in text


def lint_changed_files(
    files: Iterable[str],
    *,
    allow_quiet: bool | None = None,
    verbose: bool | None = None,
) -> int:
    allow_quiet = _resolve_allow_quiet(allow_quiet)
    verbose = _resolve_verbose(verbose)
    try:
        violations = []
        for file_name in files:
            path = pathlib.Path(file_name)
            if not _should_scan(path):
                continue
            if _is_allowed(path):
                continue
            if _contains_forbidden_token(path):
                violations.append(path.as_posix())
        if violations:
            for item in violations:
                diagnostic = f"{FORBIDDEN_TOKEN} detected in {item}"
                safe_emit(
                    build_event(TARGET_NAME, "fail", diagnostic),
                    allow_quiet=allow_quiet,
                )
            return 1
        safe_emit(
            build_event(TARGET_NAME, "ok", "no-violations"),
            allow_quiet=allow_quiet,
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        safe_emit(
            fail_event(TARGET_NAME, str(exc)),
            allow_quiet=allow_quiet,
        )
        if verbose:
            raise
        return 1


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lint for forbidden skip-validate usage"
    )
    parser.add_argument(
        "--files",
        nargs="*",
        help="Explicit files to scan (defaults to git diff --name-only)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    allow_quiet = _resolve_allow_quiet()
    verbose = _resolve_verbose()
    try:
        files = args.files or _git_diff_files()
    except RuntimeError as exc:
        safe_emit(fail_event(TARGET_NAME, str(exc)), allow_quiet=allow_quiet)
        if verbose:
            raise
        return 1
    return lint_changed_files(files, allow_quiet=allow_quiet, verbose=verbose)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
