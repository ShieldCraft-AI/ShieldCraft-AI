---
id: developer-workflow
slug: /developer-workflow
title: 🛠️ Developer Workflow (Best-in-Class)
sidebar_position: 2
---

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🚀</span> Getting Started
</h2>
<ol style="margin-bottom:0.5em;">
  <li>Clone the repo: <code>git clone https://github.com/Dee66/shieldcraft-ai.git</code></li>
  <li>Install dependencies: <code>poetry install</code></li>
  <li>Deploy infrastructure: See <code>/infrastructure</code> for AWS CDK deployment scripts</li>
</ol>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
</h2>
<ol style="margin-bottom:0.5em;">
  <li><b>Install Poetry</b>: <a href="https://python-poetry.org/docs/#installation" style="color:#a5b4fc;">Poetry installation guide</a></li>
  <li><b>No need to install Nox manually</b> – it is auto-installed by the commit script if missing.</li>
  <li><b>Commit and push using the unified script:</b><br/>
    <code>./scripts/commit-script.sh</code>
    <ul>
      <li>Ensures you are up-to-date with <code>origin/main</code></li>
      <li>Installs dependencies and self-heals the Poetry environment if needed</li>
      <li>Installs and configures pre-commit hooks</li>
      <li>Stages all changes</li>
      <li><b>Runs the full Nox suite before commit:</b> lint, typecheck, tests, safety, precommit, format check, docs lint, meta, requirements export, Docker build, Docker scan, notebook validation/lint</li>
      <li>Prompts for a conventional commit message</li>
      <li>Bumps the version in <code>pyproject.toml</code> (with auto-commit)</li>
      <li>Updates the checklist progress bar (with auto-commit)</li>
      <li><b>Runs the full Nox suite after commit for final validation</b></li>
      <li>Prompts to push to remote</li>
    </ul>
  </li>
  <li><b>Nox Usage</b> (optional, for advanced/CI):
    <ul>
      <li>Run all code checks: <code>poetry run nox -s check</code></li>
      <li>Run all sessions: <code>poetry run nox -s all</code></li>
      <li>Run CI suite: <code>poetry run nox -s ci</code></li>
      <li>See <code>noxfile.py</code> for all available sessions, including: <code>lint</code>, <code>format</code>, <code>format_check</code>, <code>typecheck</code>, <code>tests</code>, <code>precommit</code>, <code>safety</code>, <code>notebooks</code>, <code>notebook_lint</code>, <code>docs</code>, <code>docs_lint</code>, <code>docker_build</code>, <code>docker_scan</code>, <code>meta</code>, <code>requirements</code>, <code>checklist</code>, <code>clean</code>, <code>check</code>, <code>ci</code>, <code>all</code></li>
    </ul>
  </li>
</ol>
<div style="border-left:4px solid #a5b4fc; padding-left:1em; margin-bottom:1em;">
<b>What does this give you?</b><br/>
<ul>
  <li><b>Maximum reproducibility</b>: All checks run in isolated, reproducible Nox sessions.</li>
  <li><b>Security</b>: Automated safety checks, Docker image scanning, and dependency validation.</li>
  <li><b>Automation</b>: Version bumping, checklist progress, and pre-commit hooks are all handled for you.</li>
  <li><b>CI/CD parity</b>: The same checks run locally and in CI, so you catch issues before pushing.</li>
</ul>
For more, see the comments in <code>scripts/commit-script.sh</code> and <code>noxfile.py</code>.
</div>
</section>
