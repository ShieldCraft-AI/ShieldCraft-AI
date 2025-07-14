<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="./checklist.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<h1 align="center" style="margin-top:0; font-size:2em;">⚙️ Noxfile & Developer Workflow Automation</h1>
<div style="margin-bottom:1.2em; color:#b3b3b3; font-size:1em;">
  This document describes the Noxfile and developer automation workflows for ShieldCraft AI, ensuring consistency, quality, and speed across all environments.
</div>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">

## 1. Noxfile Overview

*   **Central automation entrypoint** for all developer and CI/CD tasks
*   **Session-based:** Each task (lint, test, build, docs, security, etc.) is a Nox session
*   **Python-native:** No Makefile or Bash required; works cross-platform
*   **Auto-discovers** and runs sessions based on code changes or developer needs

***

## 1a. Modular Session Layout

*   **Each Nox session is defined in its own file** under `nox_sessions/`, named for its function (e.g., `lint`, `test`, `docs`, `docker`, `bootstrap`, `security`).
*   The main `noxfile` imports all sessions, making them available as top-level Nox commands.
*   **To add or modify a session:**
    *   Edit the relevant file in `nox_sessions/` (e.g., add a new session to `security.py` for a new security check)
    *   Or create a new file for a new automation area, and import it in `noxfile.py`
*   **Benefits:**
    *   Clear separation of concerns and easy discoverability
    *   Easier maintenance and onboarding for new contributors
    *   Sessions can be tested and iterated independently

***

## 2. Automated Developer Workflows

*   **Pre-commit & Pre-push Hooks:**
    *   Linting (Ruff), formatting (Black), type checks (Mypy), and security scans (Bandit)
    *   Run automatically before every commit/push via local Git hooks (managed by pre-commit) and in CI
    *   GitHub hooks (e.g., branch protection, required status checks) ensure all Nox sessions pass before merge
*   **Testing:**
    *   Unit, integration, and smoke tests run via Nox
    *   Coverage reports generated and enforced
*   **Build & Docker:**
    *   Build, tag, and push Docker images for all services (API, ingestion, etc.)
    *   Compose orchestration for local and CI/CD
*   **Docs:**
    *   Build and serve Docusaurus docs
    *   Validate doc links and structure
*   **Release & Versioning:**
    *   Automated version bump, changelog, and release tagging
    *   PyPI and Docker registry publishing

***

## 3. CI/CD Integration & Disk Management

*   **GitHub Actions** and other CI/CD systems invoke Nox sessions for all checks
*   **Consistent local and CI/CD environments** (same Noxfile, same results)
*   **Fail-fast:** CI fails on first error, with clear logs and actionable output
*   **Aggressive disk cleanup:** CI jobs now clean up Python, Nox, and Docker artifacts before and after major steps to prevent disk exhaustion. This includes:
    *   `rm -rf .pytest_cache .nox dist build __pycache__ *.pyc *.pyo` before and after Nox orchestration
    *   `docker system prune -af --volumes` and `docker builder prune -af` after Docker builds
*   **Minimized Docker build context:** Dockerfiles only copy `pyproject.toml`, `poetry.lock`, and the `src/` directory, reducing build context size and intermediate layer bloat.
*   **Optional job splitting:** For very large projects, Nox sessions can be split into separate CI jobs to further control disk usage and resource allocation.

***

## 4. Developer Experience & Resource Awareness

*   **One-liner onboarding:** `nox -l` lists all available sessions; `nox -s <session>` runs any task
*   **Self-documenting:** Each session has a description and help output
*   **Fast feedback:** Only changed code is checked/tested where possible
*   **Extensible:** Easy to add new sessions for new tools or workflows
*   **Resource awareness:** Developers and CI/CD maintainers are encouraged to monitor disk usage (`df -h`) and clean up artifacts regularly, especially when working with large datasets or running extensive test suites.

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1em; background:#181825; color:#a5b4fc; font-size:0.95em; text-align:center;">
  <em>Related: <a href="./docker_hardening.md" style="color:#a5b4fc;">Docker Hardening</a> | <a href="./modular_mlops_governance.md" style="color:#a5b4fc;">Modular System & MLOps</a> | <a href="./project_structure.md" style="color:#a5b4fc;">Project Structure</a></em>
