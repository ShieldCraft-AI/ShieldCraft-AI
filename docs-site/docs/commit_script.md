
<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="./checklist.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<h1 align="center" style="margin-top:0; font-size:2em;">🟩 Commit Script: Automating Checks and Versioning</h1>
</section>



<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">

<div style="margin-bottom:1.2em;">
  <strong style="font-size:1.25em; color:#a5b4fc;">Why a Unified Commit Script?</strong><br/>
  <span style="color:#b3b3b3; font-size:1em;">A robust, unified commit script is essential for maintaining code quality, enforcing standards, and ensuring project progress is tracked automatically. This document details the design, implementation, and usage of the ShieldCraft AI commit script, which automates pre-commit checks, semantic versioning, and progress bar updates in the project checklist.</span>
</div>



<div style="margin-bottom:1.2em;">
  <strong style="font-size:1.15em; color:#a5b4fc;">✨ Key Features</strong>
</div>


<ul style="margin-left:1.2em;">
  <li><strong>Pre-commit Checks:</strong>
    <ul>
      <li>Linting (Ruff, Black)</li>
      <li>Type checks (Mypy)</li>
      <li>Security scans (Bandit)</li>
      <li>Test suite (Pytest)</li>
      <li>Dependency audit (Poetry, pip-audit)</li>
    </ul>
  </li>
  <li><strong>Semantic Versioning:</strong>
    <ul>
      <li>Auto-increment version based on commit message (Major/Minor/Patch)</li>
      <li>Updates <code>pyproject.toml</code> and <code>CHANGELOG.md</code></li>
    </ul>
  </li>
  <li><strong>Checklist Progress Automation:</strong>
    <ul>
      <li>Updates checklist progress bar and completion indicators after successful commit</li>
      <li>Ensures visual feedback in <code>checklist.md</code> is always current</li>
    </ul>
  </li>
  <li><strong>Developer Experience:</strong>
    <ul>
      <li>Single command: <code>./commit-script.sh</code> (Linux/macOS) or <code>commit.ps1</code> (Windows)</li>
      <li>Clear, color-coded output and actionable error messages</li>
      <li>Fails fast on any check, with guidance for remediation</li>
    </ul>
  </li>
</ul>


---


<div style="margin-bottom:1.2em;">
  <strong style="font-size:1.15em; color:#a5b4fc;">🛠️ Implementation Overview</strong>
</div>


<ol style="margin-left:1.2em;">
  <li><strong>Script Location & Structure</strong>
    <ul>
      <li>Located at the project root: <code>commit.sh</code> (Bash) and <code>commit.ps1</code> (PowerShell)</li>
      <li>Modular functions for each check, versioning, and checklist update</li>
      <li>Cross-platform compatibility</li>
    </ul>
  </li>
  <li><strong>Pre-commit Checks</strong>
    <ul>
      <li><strong>Linting:</strong> <code>ruff check .</code> and <code>black --check .</code></li>
      <li><strong>Type Checking:</strong> <code>mypy .</code></li>
      <li><strong>Security:</strong> <code>bandit -r .</code></li>
      <li><strong>Tests:</strong> <code>pytest</code></li>
      <li><strong>Dependencies:</strong> <code>poetry check</code> and <code>pip-audit</code></li>
      <li><strong>Fail on first error, print summary</strong></li>
    </ul>
  </li>
  <li><strong>Versioning Automation</strong>
    <ul>
      <li>Parses commit message for <code>feat</code>, <code>fix</code>, <code>chore</code>, etc.</li>
      <li>Bumps version in <code>pyproject.toml</code> (major/minor/patch)</li>
      <li>Appends to <code>CHANGELOG.md</code> with commit summary</li>
    </ul>
  </li>
  <li><strong>Progress Bar Update</strong>
    <ul>
      <li>Parses <code>checklist.md</code> for completed items (🟩)</li>
      <li>Updates <code>&lt;progress&gt;</code> value and percentage label</li>
      <li>Ensures checklist always reflects latest project state</li>
    </ul>
  </li>
</ol>


---


<div style="margin-bottom:1.2em;">
  <strong style="font-size:1.15em; color:#a5b4fc;">🚀 Usage</strong>
</div>

<div style="background:#222; border-radius:8px; padding:1em 1.5em; margin-bottom:1em; color:#e0e0e0;">
<strong>Linux/macOS:</strong>
<pre style="background:#181818; color:#a5b4fc; border-radius:6px; padding:0.7em 1em; margin:0.5em 0;">./commit-script.sh "feat: add new data pipeline"</pre>
<strong>Windows:</strong>
<pre style="background:#181818; color:#a5b4fc; border-radius:6px; padding:0.7em 1em; margin:0.5em 0;">./commit.ps1 "fix: correct Dockerfile permissions"</pre>
<span style="color:#b3b3b3;">The script will:</span>
<ol style="margin-left:1.2em;">
  <li>Run all checks</li>
  <li>Bump version and update changelog if checks pass</li>
  <li>Update checklist progress</li>
  <li>Commit and push changes</li>
</ol>
</div>


---


<div style="margin-bottom:1.2em;">
  <strong style="font-size:1.15em; color:#a5b4fc;">🧩 Extensibility & Best Practices</strong>
</div>
<ul style="margin-left:1.2em;">
  <li>Add new checks by extending the script functions</li>
  <li>Use <a href="https://typicode.github.io/husky/" style="color:#a5b4fc;">Husky</a> or <a href="https://pre-commit.com/" style="color:#a5b4fc;">pre-commit</a> for local enforcement</li>
  <li>Document all checks in <code>CONTRIBUTING.md</code></li>
  <li>Ensure all team members use the script for every commit</li>
</ul>


---


<div style="margin-bottom:1.2em;">
  <strong style="font-size:1.15em; color:#a5b4fc;">🔗 Related Docs</strong>
</div>
<ul style="margin-left:1.2em;">
  <li><a href="./noxfile_workflow.md" style="color:#a5b4fc;">Noxfile & Workflow Automation</a></li>
  <li><a href="./project_structure.md" style="color:#a5b4fc;">Project Structure & Version Control</a></li>
  <li><a href="./security_governance.md" style="color:#a5b4fc;">Security & Governance</a></li>
</ul>


---


<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1em; background:#181825; color:#a5b4fc; font-size:0.95em; text-align:center;">
  <em>Related: <a href="./project_structure.md" style="color:#a5b4fc;">Project Structure</a> | <a href="./noxfile_workflow.md" style="color:#a5b4fc;">Noxfile & Workflow</a> | <a href="./security_governance.md" style="color:#a5b4fc;">Security & Governance</a></em>
</section>

