---
id: nox-session-architecture
slug: nox-session-architecture
sidebar_position: 2
title: "🛠️ Nox Session Architecture & CI/CD Integration"
description: "Comprehensive overview of ShieldCraft AI's Nox-powered automation, session sequencing, and best practices for production-grade MLOps."
---

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="../../README.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Project Overview</a>
</div>
<h1 align="center" style="margin-top:0; font-size:2em;">🛠️ Nox Session Architecture & CI/CD Integration</h1>
<div id="progress-bar" align="center" style="margin-bottom:1.5em;">
  <strong>Automation Progress</strong>
  <div id="progress-label">100% Session Review Complete</div>
</div>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🔎</span> Overview
</h2>
<p>
ShieldCraft AI leverages a modular, parallel-safe Nox session architecture to automate all aspects of code quality, security, documentation, testing, and deployment. This ensures that every CI/CD run is reproducible, traceable, and production-grade.
</p>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">📋</span> Session Table & Responsibilities
</h2>

<table>
<thead>
<tr>
<th>Session/Function</th>
<th>File</th>
<th>Purpose</th>
<th>Parallel-Safe</th>
<th>CI/CD</th>
<th>Notes</th>
</tr>
</thead>
<tbody>
<tr><td>docker_build</td><td>docker.py</td><td>Builds all Docker images (main, api, ingestion)</td><td>Yes</td><td>Yes</td><td>Run after all quality gates</td></tr>
<tr><td>docker_scan</td><td>docker.py</td><td>Scans Docker images for vulnerabilities</td><td>Yes</td><td>Yes</td><td>Run after docker_build</td></tr>
<tr><td>docs</td><td>docs.py</td><td>Builds Docusaurus documentation</td><td>Yes</td><td>Yes</td><td>Parallel with other checks</td></tr>
<tr><td>docs_dev</td><td>docs.py</td><td>Runs Docusaurus dev server (local)</td><td>Yes</td><td>No</td><td>Local only</td></tr>
<tr><td>docs_lint</td><td>docs.py</td><td>Lints Markdown docs</td><td>Yes</td><td>Yes</td><td>Quality gate</td></tr>
<tr><td>lint</td><td>lint.py</td><td>Lint code with ruff and black</td><td>Yes</td><td>Yes</td><td>Quality gate</td></tr>
<tr><td>format_check</td><td>lint.py</td><td>Check code formatting</td><td>Yes</td><td>Yes</td><td>Parallel with lint</td></tr>
<tr><td>format</td><td>lint.py</td><td>Auto-format code (local)</td><td>Yes</td><td>No</td><td>Local only</td></tr>
<tr><td>typecheck</td><td>lint.py</td><td>Run mypy for static type checking</td><td>Yes</td><td>Yes</td><td>Quality gate</td></tr>
<tr><td>precommit</td><td>lint.py</td><td>Run all pre-commit hooks</td><td>Yes</td><td>Yes</td><td>Ensures local/CI parity</td></tr>
<tr><td>notebooks</td><td>notebook.py</td><td>Test Jupyter notebooks with nbval</td><td>Yes</td><td>Yes</td><td>Quality gate</td></tr>
<tr><td>notebook_lint</td><td>notebook.py</td><td>Lint/format notebooks</td><td>Yes</td><td>Yes</td><td>Parallel with other gates</td></tr>
<tr><td>bump_version</td><td>release.py</td><td>Bump project version and commit</td><td>Yes</td><td>No</td><td>Manual release only</td></tr>
<tr><td>release</td><td>release.py</td><td>Automate version bump, changelog, tag, push</td><td>Yes</td><td>No</td><td>Manual release only</td></tr>
<tr><td>checklist</td><td>release.py</td><td>Update checklist progress bar</td><td>Yes</td><td>No</td><td>Project management</td></tr>
<tr><td>security</td><td>security.py</td><td>Run safety and bandit security checks</td><td>Yes</td><td>Yes</td><td>Quality gate</td></tr>
<tr><td>safety</td><td>security.py</td><td>Run only safety vulnerability scan</td><td>Yes</td><td>Yes</td><td>Parallel with other gates</td></tr>
<tr><td>tests</td><td>test.py</td><td>Run all tests with pytest and coverage</td><td>Yes</td><td>Yes</td><td>Quality gate</td></tr>
<tr><td>test_fast</td><td>test.py</td><td>Run only fast/unit tests</td><td>Yes</td><td>Yes</td><td>Quick feedback</td></tr>
<tr><td>check</td><td>test.py</td><td>Meta-session: lint, typecheck, tests, safety, precommit</td><td>Yes</td><td>Yes</td><td>Meta-session</td></tr>
<tr><td>ci</td><td>test.py</td><td>Meta-session: all CI-required sessions</td><td>Yes</td><td>Yes</td><td>Meta-session</td></tr>
<tr><td>all</td><td>test.py</td><td>Meta-session: everything (local/dev)</td><td>Yes</td><td>No</td><td>Meta-session</td></tr>
<tr><td>file_hash</td><td>utils.py</td><td>Compute SHA256 hash of a file</td><td>Yes</td><td>Yes</td><td>Dependency change detection</td></tr>
<tr><td>nox_session_guard</td><td>utils.py</td><td>Decorator for robust error handling</td><td>Yes</td><td>Yes</td><td>All sessions</td></tr>
</tbody>
</table>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🔄</span> Session Sequencing & Best Practices
</h2>
<ul>
  <li><b>Run all quality gates (lint, typecheck, docs_lint, security, notebooks, tests) in parallel</b> for fast feedback and fail-fast behavior.</li>
  <li><b>Only proceed to docker_build and docker_scan if all gates pass.</b></li>
  <li>Meta-sessions (check, ci, all) are for local/dev use and orchestration, not for CI/CD parallel jobs.</li>
  <li>Release and version bump sessions are manual and should be restricted to authorized users.</li>
  <li>Utility functions enforce reproducibility, fail-fast, and robust error handling across all sessions.</li>
</ul>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🧠</span> Architectural Insights
</h2>
<ul>
  <li>All sessions are single-responsibility, parallel-safe, and reproducible, enabling scalable, production-grade automation.</li>
  <li>Hash-based dependency checks and marker files ensure environments are only rebuilt when necessary.</li>
  <li>Centralized error handling and logging make debugging in CI/CD straightforward.</li>
  <li>Meta-sessions provide local developer convenience without sacrificing CI/CD speed or reliability.</li>
  <li>Security gates are pragmatic, allowing deploys only when vulnerabilities are unfixable and documented (e.g., mlflow).</li>
</ul>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🚀</span> Next Steps
</h2>
<ul>
  <li>Upload test, lint, and security artifacts in CI for traceability and compliance.</li>
  <li>Further tune Poetry and Docker caching for even faster builds.</li>
  <li>Integrate CDK deploy/config sync into CI/CD for full infra automation.</li>
  <li>Expand onboarding docs for contributors, referencing this session architecture.</li>
</ul>
</section>
