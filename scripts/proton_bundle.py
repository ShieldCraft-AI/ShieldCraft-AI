#!/usr/bin/env python3
"""
Proton bundle packager (local-only, no AWS calls).

- Walks proton/templates/<template>/<version>/
  expecting: manifest.yaml, schema/schema.yaml, infrastructure/cloudformation.yaml
- Emits zip bundles under dist/proton/
- Writes dist/proton/manifest.json summarizing templates and versions

Guardrails:
- Does NOT call aws cli or deploy anything.
- Fails clearly if required files are missing.
"""
from __future__ import annotations

import json
import os
import sys
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover
    print("PyYAML is required. Install with: poetry add -G dev pyyaml", file=sys.stderr)
    raise


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_ROOT = REPO_ROOT / "proton" / "templates"
DIST_ROOT = REPO_ROOT / "dist" / "proton"


@dataclass
class TemplateVersion:
    id: str
    kind: str  # environment | service
    name: str
    displayName: str | None
    version: str
    path: str
    bundle: str


def find_templates() -> list[TemplateVersion]:
    results: list[TemplateVersion] = []
    if not TEMPLATES_ROOT.exists():
        return results

    for tmpl_dir in sorted(TEMPLATES_ROOT.iterdir()):
        if not tmpl_dir.is_dir():
            continue
        kind = infer_kind(tmpl_dir.name)
        for ver_dir in sorted(tmpl_dir.iterdir()):
            if not ver_dir.is_dir():
                continue
            manifest_path = ver_dir / "manifest.yaml"
            infra_path = ver_dir / "infrastructure" / "cloudformation.yaml"
            schema_path = ver_dir / "schema" / "schema.yaml"
            missing = [
                p for p in [manifest_path, infra_path, schema_path] if not p.exists()
            ]
            if missing:
                raise FileNotFoundError(
                    f"Template '{tmpl_dir.name}/{ver_dir.name}' is missing required files: "
                    + ", ".join(str(p.relative_to(REPO_ROOT)) for p in missing)
                )

            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = yaml.safe_load(f) or {}

            name = str(manifest.get("name") or tmpl_dir.name)
            display = manifest.get("displayName")
            version = str(manifest.get("version") or ver_dir.name)

            bundle_name = f"{name}-v{version}.zip"
            results.append(
                TemplateVersion(
                    id=tmpl_dir.name,
                    kind=kind,
                    name=name,
                    displayName=str(display) if display else None,
                    version=version,
                    path=str(ver_dir.relative_to(REPO_ROOT)),
                    bundle=f"dist/proton/{bundle_name}",
                )
            )
    return results


def infer_kind(name: str) -> str:
    # Convention: *-environment -> environment, otherwise service
    return "environment" if name.endswith("-environment") else "service"


def create_zip(src_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(src_dir):
            for fn in files:
                p = Path(root) / fn
                rel = p.relative_to(src_dir)
                zf.write(p, arcname=str(rel))


def main() -> int:
    templates = find_templates()
    if not templates:
        print("No templates found under proton/templates.")
        return 0

    for tv in templates:
        src = REPO_ROOT / tv.path
        dst = REPO_ROOT / tv.bundle
        create_zip(src, dst)
        print(f"Bundled {tv.name}@{tv.version} -> {dst}")

    manifest = {
        "templates": [asdict(t) for t in templates],
        "count": len(templates),
    }
    DIST_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = DIST_ROOT / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Wrote manifest -> {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
