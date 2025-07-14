<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="./checklist.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<h1 align="center" style="margin-top:0; font-size:2em;">📁 Project Structure, Version Control & Docusaurus Docs</h1>
<div style="margin-bottom:1.2em; color:#b3b3b3; font-size:1em;">
  This document describes the initial setup of the ShieldCraft AI project structure, version control strategy, and documentation system using Docusaurus.
</div>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">

## 1. Project Structure

The repository uses a monorepo layout, grouping all code, documentation, and infrastructure in a single place for easier management and traceability. Key top-level folders include:

- `src/` – Main application code (API, ingestion, core logic)
- `tests/` – Automated tests
- `docs-site/` – Docusaurus documentation site
- `nox_sessions/` – Automation scripts for CI/CD, linting, and developer workflow
- `notebooks/` – Jupyter notebooks for experiments and analysis
- `infrastructure/` – Infrastructure as code (IaC) and deployment assets
- `scripts/` – Utility scripts
- `config/`, `data/`, `logs/`, and others for supporting assets

- **Naming conventions:** snake_case for files, PascalCase for classes, kebab-case for docs.
- **Security:** Secrets and environment files are excluded via `.gitignore`.


<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">

## 2. Version Control

- **Git** for all code and documentation
- **Branching model:** `main` (production), `dev` (integration), feature branches (`feature/*`)
- **Pre-commit hooks:** Linting, formatting, and security checks automated
- **Commit message style:** Conventional Commits (e.g., `feat:`, `fix:`, `docs:`)
- **Pull request workflow:** All changes reviewed before merge
- **Automated checks:** CI runs tests, lint, and build on PRs


<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">

## 3. Docusaurus Documentation

- **Docusaurus** powers the `docs-site/` for all project documentation
- **Live preview:** `npm start` in `docs-site/` for local docs
- **Docs structure:** Mirrors repo layout for easy navigation
- **Custom theme:** Dark mode, ShieldCraft branding, and progress bar
- **Checklist integration:** Implementation checklist auto-updates progress
- **Cross-linking:** All docs interlinked for seamless navigation


<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1em; background:#181825; color:#a5b4fc; font-size:0.95em; text-align:center;">
  <em>Related: <a href="./adrs.md" style="color:#a5b4fc;">ADRs</a> | <a href="./risk_log.md" style="color:#a5b4fc;">Risk Log</a> | <a href="./project_structure.md" style="color:#a5b4fc;">Project Structure</a></em>
