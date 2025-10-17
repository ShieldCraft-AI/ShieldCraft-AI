#!/usr/bin/env python3
"""Summarise recent GitHub Actions runs and optionally download failure logs.

Usage examples
--------------
python scripts/github_actions_report.py \
    --repo ShieldCraft-AI/ShieldCraft-AI --limit 5

python scripts/github_actions_report.py \
    --repo ShieldCraft-AI/ShieldCraft-AI --workflow monitoring --download-logs

Set ``GITHUB_TOKEN`` (or ``GH_TOKEN``) in your environment. Provide the ``workflow``
scope (or repo admin rights) when you want to download job logs.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
import re
import json
import subprocess
import zipfile
from typing import Any, Dict, Iterable, Optional, List, Tuple

import requests

API_ROOT = "https://api.github.com"
DEFAULT_REPO = "ShieldCraft-AI/ShieldCraft-AI"
TOKEN_ENV_VARS = ("GITHUB_TOKEN", "GH_TOKEN")


class GitHubActionsClient:
    """Thin wrapper around the GitHub Actions REST API."""

    def __init__(self, token: Optional[str] = None) -> None:
        self.session = requests.Session()
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "shieldcraft-actions-reporter",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.session.headers.update(headers)

    def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = f"{API_ROOT}{path}"
        response = self.session.request(method, url, timeout=30, **kwargs)
        if response.status_code == 403 and "Must have admin rights" in response.text:
            raise PermissionError(
                "403: admin rights required for this operation. Provide a token with "
                "appropriate permissions (workflow scope or repo admin)."
            )
        if not response.ok:
            raise RuntimeError(
                f"GitHub API request failed ({response.status_code}): {response.text}"
            )
        return response.json()

    def download_job_logs(self, repo: str, job_id: int) -> bytes:
        url = f"{API_ROOT}/repos/{repo}/actions/jobs/{job_id}/logs"
        response = self.session.get(url, timeout=60, stream=True)
        if response.status_code == 403 and "Must have admin rights" in response.text:
            raise PermissionError(
                "403: admin rights required to download logs (workflow scope needed)."
            )
        if response.status_code == 302 and "Location" in response.headers:
            redirect = response.headers["Location"]
            response = self.session.get(redirect, timeout=60, stream=True)
        if not response.ok:
            raise RuntimeError(
                f"GitHub API log download failed ({response.status_code}): {response.text}"
            )
        return response.content

    def list_runs(
        self,
        repo: str,
        per_page: int,
        limit: int,
        status_filter: Optional[str] = None,
    ) -> Iterable[Dict[str, Any]]:
        """Yield workflow runs up to ``limit`` entries, optionally filtering by status."""

        fetched = 0
        page = 1
        while fetched < limit:
            params = {"per_page": per_page, "page": page}
            if status_filter:
                params["status"] = status_filter
            data = self._request("GET", f"/repos/{repo}/actions/runs", params=params)
            runs = data.get("workflow_runs", [])
            if not runs:
                break
            for run in runs:
                yield run
                fetched += 1
                if fetched >= limit:
                    return
            page += 1

    def list_jobs(self, repo: str, run_id: int) -> Iterable[Dict[str, Any]]:
        """Return job details for a workflow run."""

        jobs: list[Dict[str, Any]] = []
        page = 1
        while True:
            params = {"per_page": 100, "page": page}
            data = self._request(
                "GET", f"/repos/{repo}/actions/runs/{run_id}/jobs", params=params
            )
            page_jobs = data.get("jobs", [])
            if not page_jobs:
                break
            jobs.extend(page_jobs)
            if len(page_jobs) < 100:
                break
            page += 1
        return jobs

    # --- Generic Issues API helpers (safe, minimal) ---
    def list_issues(
        self, repo: str, per_page: int = 30, limit: int = 30, state: str = "open"
    ) -> Iterable[Dict[str, Any]]:
        """Yield issues (not pull requests) for the repo. Unauthenticated requests are rate-limited."""
        fetched = 0
        page = 1
        while fetched < limit:
            params = {"per_page": per_page, "page": page, "state": state}
            data = self._request("GET", f"/repos/{repo}/issues", params=params)
            issues = [i for i in data if not i.get("pull_request")]
            if not issues:
                break
            for issue in issues:
                yield issue
                fetched += 1
                if fetched >= limit:
                    return
            page += 1

    def add_issue_labels(
        self, repo: str, issue_number: int, labels: List[str]
    ) -> Dict[str, Any]:
        return self._request(
            "POST",
            f"/repos/{repo}/issues/{issue_number}/labels",
            json={"labels": labels},
        )

    def create_issue_comment(
        self, repo: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        return self._request(
            "POST", f"/repos/{repo}/issues/{issue_number}/comments", json={"body": body}
        )

    def update_issue_state(
        self, repo: str, issue_number: int, state: str = "closed"
    ) -> Dict[str, Any]:
        return self._request(
            "PATCH", f"/repos/{repo}/issues/{issue_number}", json={"state": state}
        )


def resolve_token() -> Optional[str]:
    for var in TOKEN_ENV_VARS:
        token = os.environ.get(var)
        if token:
            return token
    return None


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help="GitHub repo in owner/name form (default: %(default)s)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of workflow runs to inspect (default: %(default)s)",
    )
    parser.add_argument(
        "--per-page",
        type=int,
        default=20,
        help="GitHub API page size when listing runs (default: %(default)s)",
    )
    parser.add_argument(
        "--include-success",
        action="store_true",
        help="Show successful runs as well (default: failures only)",
    )
    parser.add_argument(
        "--show-logs-url",
        action="store_true",
        help="Print log download URLs for each job (requires admin/workflow scope to access).",
    )
    parser.add_argument(
        "--workflow",
        help="Filter runs by workflow name or file path substring (case-insensitive).",
    )
    parser.add_argument(
        "--download-logs",
        action="store_true",
        help="Download zipped job logs for failing jobs (requires workflow scope).",
    )
    parser.add_argument(
        "--log-dir",
        default="github-workflow-logs",
        help="Directory for downloaded job logs (default: %(default)s)",
    )
    parser.add_argument(
        "--scan-logs",
        action="store_true",
        help="Scan downloaded or local logs for common failure patterns (writes summary to --log-dir).",
    )
    parser.add_argument(
        "--scan-workflows",
        action="store_true",
        help="Scan .github/workflows for deprecated artifact action versions (dry-run by default).",
    )
    parser.add_argument(
        "--apply-fixes",
        action="store_true",
        help="Apply safe fixes to workflow files (replaces v3 -> v4 for known artifact actions).",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="When used with --apply-fixes, create a local git commit with the changes.",
    )
    parser.add_argument(
        "--list-issues",
        action="store_true",
        help="List recent issues for the repo (excludes PRs).",
    )
    parser.add_argument(
        "--issue-limit",
        type=int,
        default=20,
        help="Number of recent issues to fetch with --list-issues (default: 20).",
    )
    parser.add_argument(
        "--apply-issue-actions",
        action="store_true",
        help="Apply safe triage actions to selected issues (labels/comments); requires token and is opt-in.",
    )
    parser.add_argument(
        "--issue-labels",
        help="Comma-separated list of labels to add when --apply-issue-actions is used (e.g. 'triage,needs-info')",
    )
    return parser.parse_args(argv)


### Log & workflow scanning helpers


def scan_log_bytes(content: bytes, filename: str) -> List[str]:
    """Scan raw log bytes and return a list of human-friendly findings.

    The function is deliberately tolerant: many downloaded job logs are plain text
    even when the API returns a zipped archive. We decode with 'replace'.
    """
    text = content.decode("utf-8", errors="replace")
    findings: List[str] = []

    # Patterns to detect
    if "NoRegionError" in text or "You must specify a region" in text:
        findings.append("NoRegionError: AWS region not configured in job")
    if "Must have admin rights" in text:
        findings.append(
            "PermissionError: workflow scope / admin rights required to download logs"
        )
    if "actions/upload-artifact@v3" in text or "actions/download-artifact@v3" in text:
        findings.append(
            "Deprecated artifact action v3 detected (upload/download) in workflow files or logs"
        )
    # Playwright / E2E common failures
    if "expect(" in text and "toBeVisible" in text:
        findings.append("Playwright assertion failures: expect(...).toBeVisible() seen")
    if (
        "locator('text=" in text
        or "Unexpected token '=' while parsing css selector" in text
    ):
        findings.append("Playwright selector parsing/strict-mode issues detected")
    if (
        "This request has been automatically failed because it uses a deprecated version"
        in text
    ):
        findings.append(
            "Workflow automatic failure due to deprecated action version (v3)"
        )

    # Grep for explicit 'failure' lines to give context
    failure_lines = [
        ln for ln in text.splitlines() if re.search(r"fail|error|exception", ln, re.I)
    ]
    if failure_lines:
        # Add up to 5 representative failure lines
        findings.append(
            "Representative failure lines:\n" + "\n".join(failure_lines[:5])
        )

    return findings


def scan_log_file(path: str) -> List[str]:
    """Scan a log file on disk. If it's a zip, inspect contained files; otherwise scan raw bytes."""
    try:
        if zipfile.is_zipfile(path):
            findings: List[str] = []
            with zipfile.ZipFile(path, "r") as z:
                # examine each file inside
                for name in z.namelist():
                    try:
                        data = z.read(name)
                    except Exception:
                        continue
                    sub = scan_log_bytes(data, name)
                    if sub:
                        findings.extend([f"{name}: {s}" for s in sub])
            return findings
        else:
            with open(path, "rb") as fh:
                data = fh.read()
            return scan_log_bytes(data, path)
    except Exception as exc:
        return [f"Error scanning {path}: {exc}"]


def scan_workflow_files(
    root: str = ".github/workflows",
) -> Dict[str, List[Tuple[int, str]]]:
    """Scan YAML workflow files for deprecated artifact actions.

    Returns a mapping path -> list of (line_no, matched_line).
    """
    findings: Dict[str, List[Tuple[int, str]]] = {}
    import glob

    for path in glob.glob(f"{root}/*.yml") + glob.glob(f"{root}/*.yaml"):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                lines = fh.readlines()
        except Exception:
            continue
        matches: List[Tuple[int, str]] = []
        for i, ln in enumerate(lines, start=1):
            if (
                "actions/upload-artifact@v3" in ln
                or "actions/download-artifact@v3" in ln
            ):
                matches.append((i, ln.strip()))
        if matches:
            findings[path] = matches
    return findings


def fix_workflow_file(path: str, apply: bool = False) -> Tuple[bool, str, str]:
    """Replace known deprecated artifact action versions in the workflow file.

    Returns (changed, original_text, new_text). If apply=False this is a dry-run.
    """
    with open(path, "r", encoding="utf-8") as fh:
        original = fh.read()
    new = original
    new = new.replace("actions/upload-artifact@v3", "actions/upload-artifact@v4")
    new = new.replace("actions/download-artifact@v3", "actions/download-artifact@v4")
    changed = new != original
    if changed and apply:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)
    return changed, original, new


def maybe_git_commit(paths: List[str], message: str) -> Tuple[bool, str]:
    """Create a local git commit for the specified files. Returns (ok, output).

    This is intentionally conservative: we only run 'git add' and 'git commit' and
    return the subprocess output. Caller must ensure a git repo is present.
    """
    try:
        subprocess.check_output(["git", "add"] + paths, stderr=subprocess.STDOUT)
        out = subprocess.check_output(
            ["git", "commit", "-m", message], stderr=subprocess.STDOUT
        )
        return True, out.decode("utf-8", errors="replace")
    except subprocess.CalledProcessError as exc:
        return False, exc.output.decode("utf-8", errors="replace")


def format_run_summary(run: Dict[str, Any]) -> str:
    name = run.get("name") or run.get("display_title") or "<unknown>"
    conclusion = run.get("conclusion") or run.get("status")
    started = run.get("run_started_at") or run.get("created_at")
    event = run.get("event")
    number = run.get("run_number")
    return (
        f"{name} (run #{number}) – event={event}, conclusion={conclusion}, "
        f"started={started}, run_id={run.get('id')}"
    )


def print_job_details(
    client: GitHubActionsClient,
    repo: str,
    run_id: int,
    show_logs_url: bool,
    download_logs: bool,
    log_dir: Optional[Path],
    run_label: str,
) -> None:
    try:
        jobs = client.list_jobs(repo, run_id)
    except PermissionError as exc:
        print(f"    ! {exc}")
        return

    if not jobs:
        print("    (no jobs returned by API)")
        return

    for job in jobs:
        job_name = job.get("name")
        conclusion = job.get("conclusion") or job.get("status")
        print(f"    - Job: {job_name} (conclusion={conclusion})")
        failed = conclusion in {"failure", "timed_out", "cancelled"}
        for step in job.get("steps", []):
            step_name = step.get("name")
            step_conclusion = step.get("conclusion") or step.get("status")
            if step_conclusion not in {"failure", "cancelled"}:
                continue
            print(f"        • Step failed: {step_name} (conclusion={step_conclusion})")
            failed = True
        if show_logs_url and job.get("html_url"):
            print(f"        logs: {job['html_url']}")
        if download_logs and failed and log_dir is not None:
            try:
                content = client.download_job_logs(repo, job_id=job["id"])
            except PermissionError as exc:
                print(f"        ! {exc}")
                continue
            except RuntimeError as exc:
                print(f"        ! {exc}")
                continue
            log_dir.mkdir(parents=True, exist_ok=True)
            filename = (
                f"{run_id}_{slugify(run_label)}_{slugify(job_name)}_{job['id']}.zip"
            )
            path = log_dir / filename
            with open(path, "wb") as fh:
                fh.write(content)
            print(f"        saved logs -> {path}")


def slugify(text: Optional[str]) -> str:
    value = text or "job"
    value = re.sub(r"[^A-Za-z0-9]+", "-", value.strip())
    value = value.strip("-")
    return value or "job"


def main(argv: Iterable[str]) -> int:
    args = parse_args(argv)
    token = resolve_token()
    if not token:
        print(
            "[WARN] No GitHub token detected – you may hit rate limits or be unable to "
            "access private resources.",
            file=sys.stderr,
        )

    client = GitHubActionsClient(token=token)
    status_filter = None if args.include_success else "failure"

    try:
        runs = list(
            client.list_runs(
                repo=args.repo,
                per_page=args.per_page,
                limit=args.limit,
                status_filter=status_filter,
            )
        )
    except RuntimeError as exc:
        print(f"Error retrieving workflow runs: {exc}", file=sys.stderr)
        return 1

    if not runs:
        print("No workflow runs found for the specified parameters.")
        return 0

    if args.workflow:
        needle = args.workflow.lower()
        runs = [
            run
            for run in runs
            if needle
            in (run.get("name", "").lower() + " " + run.get("path", "").lower())
        ]
        if not runs:
            print("No workflow runs matched the provided workflow filter.")
            return 0

    print(f"Found {len(runs)} workflow run(s) for {args.repo}:")
    # Always honor --log-dir for summary output; download only happens when --download-logs is set.
    log_dir = Path(args.log_dir)
    for run in runs:
        print(f"- {format_run_summary(run)}")
        print_job_details(
            client,
            args.repo,
            run_id=run["id"],
            show_logs_url=args.show_logs_url,
            download_logs=args.download_logs,
            log_dir=log_dir,
            run_label=run.get("name") or run.get("path") or str(run.get("id")),
        )

    # Additional scanning and optional fixes
    summary: Dict[str, Any] = {
        "runs_inspected": len(runs),
        "log_scans": {},
        "workflow_scan": {},
        "workflow_fixes": {},
    }

    if args.scan_logs:
        # scan downloaded logs under log_dir (or current dir if none)
        log_base = Path(args.log_dir)
        summary_logs: Dict[str, List[str]] = {}
        if log_base.exists() and log_base.is_dir():
            for entry in log_base.iterdir():
                if entry.is_file():
                    findings = scan_log_file(str(entry))
                    if findings:
                        summary_logs[str(entry)] = findings
                        print(
                            f"Log issues in {entry}: \n  - " + "\n  - ".join(findings)
                        )
        else:
            print(f"No log directory found at {log_base}; skipping log scan")
        summary["log_scans"] = summary_logs

    if args.scan_workflows or args.apply_fixes:
        wf_findings = scan_workflow_files()
        summary["workflow_scan"] = {
            k: [{"line": l, "text": t} for l, t in v] for k, v in wf_findings.items()
        }
        if wf_findings:
            print(
                "Found deprecated artifact action references in the following workflow files:"
            )
            for path, matches in wf_findings.items():
                for ln, txt in matches:
                    print(f"  - {path}:{ln}: {txt}")

        if args.apply_fixes and wf_findings:
            changed_files: List[str] = []
            for path in wf_findings.keys():
                changed, orig, new = fix_workflow_file(path, apply=True)
                summary["workflow_fixes"][path] = {"changed": changed}
                if changed:
                    changed_files.append(path)
                    print(f"Patched {path} (replaced v3 -> v4)")
            if args.commit and changed_files:
                ok, out = maybe_git_commit(
                    changed_files, "ci: update artifact actions to v4 (automated)"
                )
                summary["workflow_fixes"]["git_commit"] = {"ok": ok, "output": out}
                print("Git commit created" if ok else "Git commit failed:\n" + out)

    # write summary JSON
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        summary_path = log_dir / "scan-summary.json"
        with open(summary_path, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
        print(f"Wrote scan summary -> {summary_path}")

    # --- Issue listing & safe triage ---
    if args.list_issues:
        print(f"Listing up to {args.issue_limit} recent issues for {args.repo}")
        issues = list(
            client.list_issues(
                args.repo, per_page=min(30, args.issue_limit), limit=args.issue_limit
            )
        )
        summary["issues"] = []
        for issue in issues:
            brief = {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "user": issue.get("user", {}).get("login"),
                "created_at": issue.get("created_at"),
                "labels": [l.get("name") for l in issue.get("labels", [])],
                "url": issue.get("html_url"),
            }
            summary["issues"].append(brief)
            print(
                f"# {brief['number']}: {brief['title']} (labels={brief['labels']}) by {brief['user']}"
            )

        if args.apply_issue_actions:
            token = resolve_token()
            if not token:
                print(
                    "[WARN] --apply-issue-actions requested but no GITHUB_TOKEN/GH_TOKEN found; aborting apply"
                )
            else:
                labels = [
                    l.strip() for l in (args.issue_labels or "").split(",") if l.strip()
                ]
                for issue in issues:
                    num = issue.get("number")
                    print(f"Applying triage to issue #{num}: adding labels={labels}")
                    if labels:
                        try:
                            client.add_issue_labels(args.repo, num, labels)
                            print(f"  - labels added to #{num}")
                        except Exception as exc:
                            print(f"  ! failed to add labels to #{num}: {exc}")
                    # add a short comment explaining the automated triage
                    comment = (
                        "Automated triage: adding labels for triage. "
                        "If this is incorrect, please update or remove them."
                    )
                    try:
                        client.create_issue_comment(args.repo, num, comment)
                        print(f"  - comment added to #{num}")
                    except Exception as exc:
                        print(f"  ! failed to comment on #{num}: {exc}")

        # update summary file with issues
        with open(summary_path, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
