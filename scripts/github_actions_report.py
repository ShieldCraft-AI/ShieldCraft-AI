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
from typing import Any, Dict, Iterable, Optional

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
    return parser.parse_args(argv)


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
    log_dir = Path(args.log_dir) if args.download_logs else None
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
