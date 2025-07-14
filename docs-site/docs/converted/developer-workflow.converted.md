---
id: developer-workflow
slug: /developer-workflow
title: 🛠️ Developer Workflow (Best-in-Class)
sidebar_position: 2
---

[⬅️ Back to Project Overview](../../README.md)

## 🚀Getting Started

1. Clone the repo:git clone https://github.com/Dee66/shieldcraft-ai.git
1. Install dependencies:poetry install
1. Deploy infrastructure: All AWS deployments useCDK v2andAWS CLI v2only.Authentication is via IAM Identity Center (SSO) for developers, or OIDC for CI/CD.Static AWS credentials and CDK v1 are not supported.Before deploying, run:aws configure ssoand select your assigned profile and region.See below for onboarding steps.

##

1. Install Poetry:Poetry installation guide
1. No need to install Nox manually– it is auto-installed by the commit script if missing.
1. Commit and push using the unified script:./scripts/commit-script.shEnsures you are up-to-date withorigin/mainInstalls dependencies and self-heals the Poetry environment if neededInstalls and configures pre-commit hooksStages all changesRuns the full Nox suite before commit:lint, typecheck, tests, safety, precommit, format check, docs lint, meta, requirements export, Docker build, Docker scan, notebook validation/lintPrompts for a conventional commit messageBumps the version inpyproject.toml(with auto-commit)Updates the checklist progress bar (with auto-commit)Runs the full Nox suite after commit for final validationPrompts to push to remote
1. Nox Usage(optional, for advanced/CI):Run all code checks:poetry run nox -s checkRun all sessions:poetry run nox -s allRun CI suite:poetry run nox -s ciSeenoxfile.pyfor all available sessions, including:lint,format,format_check,typecheck,tests,precommit,safety,notebooks,notebook_lint,docs,docs_lint,docker_build,docker_scan,meta,requirements,checklist,clean,check,ci,all

What does this give you?  * Maximum reproducibility: All checks run in isolated, reproducible Nox sessions.
* Security: Automated safety checks, Docker image scanning, and dependency validation.
* Automation: Version bumping, checklist progress, and pre-commit hooks are all handled for you.
* CI/CD parity: The same checks run locally and in CI, so you catch issues before pushing. For more, see the comments in `scripts/commit-script.sh` and `noxfile.py` .

<!-- Unhandled tags: b, br, li -->
