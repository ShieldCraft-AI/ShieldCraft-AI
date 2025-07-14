[⬅️ Back to Checklist](./checklist.md)

# 🟩 Commit Script: Automating Checks and Versioning

Why a Unified Commit Script?A robust, unified commit script is essential for maintaining code quality, enforcing standards, and ensuring project progress is tracked automatically. This document details the design, implementation, and usage of the ShieldCraft AI commit script, which automates pre-commit checks, semantic versioning, and progress bar updates in the project checklist.

✨ Key Features

* Pre-commit Checks:Linting (Ruff, Black)Type checks (Mypy)Security scans (Bandit)Test suite (Pytest)Dependency audit (Poetry, pip-audit)
* Semantic Versioning:Auto-increment version based on commit message (Major/Minor/Patch)Updatespyproject.tomlandCHANGELOG.md
* Checklist Progress Automation:Updates checklist progress bar and completion indicators after successful commitEnsures visual feedback inchecklist.mdis always current
* Developer Experience:Single command:./commit-script.sh(Linux/macOS) orcommit.ps1(Windows)Clear, color-coded output and actionable error messagesFails fast on any check, with guidance for remediation

---

🛠️ Implementation Overview

1. Script Location & StructureLocated at the project root:commit.sh(Bash) andcommit.ps1(PowerShell)Modular functions for each check, versioning, and checklist updateCross-platform compatibility
1. Pre-commit ChecksLinting:ruff check .andblack --check .Type Checking:mypy .Security:bandit -r .Tests:pytestDependencies:poetry checkandpip-auditFail on first error, print summary
1. Versioning AutomationParses commit message forfeat,fix,chore, etc.Bumps version inpyproject.toml(major/minor/patch)Appends toCHANGELOG.mdwith commit summary
1. Progress Bar UpdateParseschecklist.mdfor completed items (🟩)Updates<progress>value and percentage labelEnsures checklist always reflects latest project state

---

🚀 Usage

Linux/macOS:./commit-script.sh "feat: add new data pipeline"Windows:./commit.ps1 "fix: correct Dockerfile permissions"The script will:Run all checksBump version and update changelog if checks passUpdate checklist progressCommit and push changes

---

🧩 Extensibility & Best Practices

* Add new checks by extending the script functions
* UseHuskyorpre-commitfor local enforcement
* Document all checks inCONTRIBUTING.md
* Ensure all team members use the script for every commit

---

🔗 Related Docs

* Noxfile & Workflow Automation
* Project Structure & Version Control
* Security & Governance

---

Related:Project Structure|Noxfile & Workflow|Security & Governance
