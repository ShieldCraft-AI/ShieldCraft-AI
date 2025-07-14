[⬅️ Back to Checklist](./checklist.md)

# 📁 Project Structure, Version Control & Docusaurus Docs

This document describes the initial setup of the ShieldCraft AI project structure, version control strategy, and documentation system using Docusaurus.

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

## 2. Version Control

- **Git** for all code and documentation
- **Branching model:** `main` (production), `dev` (integration), feature branches (`feature/*`)
- **Pre-commit hooks:** Linting, formatting, and security checks automated
- **Commit message style:** Conventional Commits (e.g., `feat:`, `fix:`, `docs:`)
- **Pull request workflow:** All changes reviewed before merge
- **Automated checks:** CI runs tests, lint, and build on PRs

## 3. Docusaurus Documentation

- **Docusaurus** powers the `docs-site/` for all project documentation
- **Live preview:** `npm start` in `docs-site/` for local docs
- **Docs structure:** Mirrors repo layout for easy navigation
- **Custom theme:** Dark mode, ShieldCraft branding, and progress bar
- **Checklist integration:** Implementation checklist auto-updates progress
- **Cross-linking:** All docs interlinked for seamless navigation

Related:ADRs|Risk Log|Project Structure

<!-- Unhandled tags: em -->
