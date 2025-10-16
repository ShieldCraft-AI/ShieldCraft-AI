#!/usr/bin/env python3
"""Create a GitHub Actions workflow template to inject Amplify runtime config.

Defensive, dry-run by default. Use --commit to apply changes and create a git
commit. This script does not create AWS infra.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = (
    REPO_ROOT / ".github" / "workflows" / "inject-amplify-config-secretsmanager.yml"
)
README_PATH = REPO_ROOT / "scripts" / "README_AMPLIFY_AUTOMATION.md"

WORKFLOW_TEMPLATE = """
name: Inject Amplify Config from Secrets Manager (template)

on:
  workflow_dispatch:
    inputs:
      run_build:
        description: 'Run npm build after injecting config? (yes/no)'
        required: false
        default: 'no'

jobs:
  inject-amplify-config:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS credentials (assume role via OIDC)
        uses: aws-actions/configure-aws-credentials@v3
        with:
          role-to-assume: ${{ secrets.ROLE_TO_ASSUME }}
          aws-region: __AWS_REGION__

      - name: Fetch Amplify config from Secrets Manager
        env:
          SECRET_NAME: ${{ secrets.SECRET_NAME }}
        run: |
          set -euo pipefail
          echo "Fetching secret: $SECRET_NAME"
          mkdir -p docs-site/static
          aws secretsmanager get-secret-value --secret-id "$SECRET_NAME" --query SecretString --output text > docs-site/static/amplify-config.json
          echo "Wrote docs-site/static/amplify-config.json (preview:)"
          head -c 400 docs-site/static/amplify-config.json || true

      - name: Optional: run docs-site build
        if: ${{ github.event.inputs.run_build == 'yes' }}
        run: |
          cd docs-site
          npm ci
          npm run build
"""

README_TEXT = """
Amplify config automation
=========================

This helper creates a workflow template that fetches a JSON runtime config
from AWS Secrets Manager (via GitHub OIDC) and writes
`docs-site/static/amplify-config.json` before a build.

Security: this script does NOT create AWS resources. Create the Secrets
Manager secret and an IAM role with OIDC trust separately. Store only the
role ARN and secret name in repository secrets (ROLE_TO_ASSUME and SECRET_NAME).
"""


def run(cmd: List[str], capture: bool = False) -> Tuple[int, str]:
    try:
        if capture:
            out = subprocess.check_output(cmd, cwd=REPO_ROOT, stderr=subprocess.STDOUT)
            return 0, out.decode(errors="ignore")
        subprocess.check_call(cmd, cwd=REPO_ROOT)
        return 0, ""
    except subprocess.CalledProcessError as e:
        return e.returncode, (
            getattr(e, "output", b"").decode(errors="ignore") if capture else ""
        )


def create_workflow_file(path: Path, dry_run: bool = True) -> Tuple[bool, str]:
    # Respect existing workflow unless forced. Caller can set path.exists() handling.
    if path.exists():
        return False, f"Workflow {path} already exists"
    if dry_run:
        return True, "DRY RUN: would create workflow:\n" + WORKFLOW_TEMPLATE[:1000]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(WORKFLOW_TEMPLATE)
    README_PATH.write_text(README_TEXT)
    return True, f"Wrote {path} and {README_PATH}"


def audit_amplify_usage(root: Path) -> Tuple[List[Path], Optional[dict]]:
    """Search the repo for references to amplify-config.json and return paths found.

    Also try to parse docs-site/static/amplify-config.json if present and return the JSON.
    """
    hits: List[Path] = []
    for p in root.rglob("*"):
        try:
            if p.is_file() and p.suffix not in {
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".woff",
                ".woff2",
                ".pdf",
            }:
                text = p.read_text(errors="ignore")
                if "amplify-config.json" in text:
                    hits.append(p)
        except Exception:
            continue
    cfg = None
    static_cfg = root / "docs-site" / "static" / "amplify-config.json"
    if static_cfg.exists():
        try:
            import json

            cfg = json.loads(static_cfg.read_text())
        except Exception:
            cfg = None
    return hits, cfg


def maybe_git_commit(files: List[Path], message: str) -> Tuple[bool, str]:
    for p in files:
        rc, out = run(["git", "add", str(p)])
        if rc != 0:
            return False, f"git add failed: {out}"
    rc, out = run(["git", "commit", "-m", message])
    if rc != 0:
        return False, f"git commit failed: {out}"
    return True, "Committed changes"


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--create-workflow", action="store_true")
    p.add_argument("--commit", action="store_true")
    p.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing workflow when used with --commit",
    )
    p.add_argument(
        "--region",
        default="af-south-1",
        help="AWS region to write into the workflow template",
    )
    p.add_argument(
        "--audit",
        action="store_true",
        help="scan the repo for amplify-config.json usage and show static config preview",
    )
    args = p.parse_args(argv)

    changed_files: List[Path] = []

    if args.create_workflow:
        # replace placeholder region token in the template
        tpl = WORKFLOW_TEMPLATE.replace("__AWS_REGION__", args.region)
        if WORKFLOW_PATH.exists() and args.commit and args.force:
            WORKFLOW_PATH.unlink()
        if WORKFLOW_PATH.exists():
            ok, msg = False, f"Workflow {WORKFLOW_PATH} already exists"
        else:
            if args.commit:
                WORKFLOW_PATH.parent.mkdir(parents=True, exist_ok=True)
                WORKFLOW_PATH.write_text(tpl)
                README_PATH.write_text(README_TEXT)
                ok, msg = True, f"Wrote {WORKFLOW_PATH} and {README_PATH}"
                changed_files.append(WORKFLOW_PATH)
            else:
                ok, msg = True, "DRY RUN: would create workflow:\n" + tpl[:1000]
        print(msg)

    if args.audit:
        hits, cfg = audit_amplify_usage(REPO_ROOT)
        print("Found references to amplify-config.json in these files:")
        for h in hits:
            try:
                print(" -", h.relative_to(REPO_ROOT))
            except Exception:
                print(" -", h)
        if cfg is not None:
            import json

            print("\nStatic docs-site/static/amplify-config.json preview:")
            print(json.dumps(cfg, indent=2)[:1000])
        else:
            print(
                "\nNo valid docs-site/static/amplify-config.json found or it failed to parse."
            )

    if args.commit and changed_files:
        ok, msg = maybe_git_commit(
            changed_files, "chore: add inject-amplify-config workflow"
        )
        print(msg)

    print("Done. This script is dry-run by default; use --commit to apply changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
