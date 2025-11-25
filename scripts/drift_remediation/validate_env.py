"""Lightweight environment validation for drift tooling."""

from __future__ import annotations

import argparse
import os
import json
from pathlib import Path
from typing import Sequence

SAFE_FALSE_VALUES = {"", "0", "false", "False"}
SENTINEL_NAME = ".validate_env_write_check"


class ValidationError(RuntimeError):
    """Raised when the local environment fails a safety pre-check."""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate local environment guardrails before running drift automation."
        )
    )
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=None,
        help="Path to drift_baselines directory (defaults to ./drift_baselines).",
    )
    parser.add_argument(
        "--unsafe",
        action="store_true",
        help=(
            "Allow execution when NO_APPLY is unset. Intended only for local"
            " experimentation."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit validation result as compact JSON (e.g., for tooling).",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _require_env(var_name: str) -> str:
    value = str(os.environ.get(var_name, "")).strip()
    if not value:
        raise ValidationError(f"Environment variable {var_name} is required")
    return value


def _require_guardrail(allow_unsafe: bool) -> None:
    flag = str(os.environ.get("NO_APPLY", "")).strip()
    if flag not in SAFE_FALSE_VALUES:
        return
    if allow_unsafe:
        return
    raise ValidationError(
        "NO_APPLY must be set (export NO_APPLY=1) unless --unsafe is provided"
    )


def _resolve_baseline_dir(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    return Path.cwd() / "drift_baselines"


def _ensure_writable(directory: Path) -> None:
    if not directory.exists():
        raise ValidationError(f"Baseline directory missing: {directory}")
    if not directory.is_dir():
        raise ValidationError(f"Baseline path is not a directory: {directory}")

    sentinel = directory / SENTINEL_NAME
    try:
        sentinel.write_text("ok", encoding="utf-8")
    except OSError as exc:
        raise ValidationError(
            f"Cannot write to baseline directory {directory}: {exc}"
        ) from exc
    finally:
        try:
            sentinel.unlink()
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise ValidationError(
                f"Failed to clean up sentinel file in {directory}: {exc}"
            ) from exc


def validate_environment(args: argparse.Namespace) -> None:
    _require_env("AWS_DEFAULT_REGION")
    _require_guardrail(allow_unsafe=args.unsafe)
    baseline_dir = _resolve_baseline_dir(args.baseline_dir)
    _ensure_writable(baseline_dir)


def _emit_status(success: bool, as_json: bool, reason: str | None = None) -> None:
    if as_json:
        payload = {"status": "ok" if success else "error"}
        if not success and reason:
            payload["reason"] = reason
        print(json.dumps(payload, separators=(",", ":")))
        return
    if success:
        print("Environment looks safe for drift automation")
    else:
        print(f"[ERROR] {reason}")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        validate_environment(args)
    except ValidationError as exc:
        _emit_status(False, args.json, str(exc))
        raise SystemExit(1) from exc

    _emit_status(True, args.json)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI hook
    raise SystemExit(main())
