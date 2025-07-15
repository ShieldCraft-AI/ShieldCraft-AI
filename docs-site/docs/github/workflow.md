<div align="center" style="display: flex; align-items: center; justify-content: center; margin-bottom:2em">
  <img src="https://img.shields.io/badge/Workflow-Shieldcraft%20AI-blueviolet?style=for-the-badge&logo=github&logoColor=white" alt="Shieldcraft AI Workflow" />
</div>

<h1 align="center">🛠️ ShieldCraft AI: Commit & Deployment Workflow</h1>
<p align="center"><em>Enterprise-Grade MLOps, CI/CD, and Cloud-Native Automation</em></p>

<div id="progress-bar" align="center" style="margin-bottom:1.5em;">
  <strong>Project Progress</strong>
  <a href="./checklist.md" style="margin-left:0.75em; font-size:0.95em; color:#a5b4fc; text-decoration:none;">(checklist)</a><br/>
  <progress id="shieldcraft-progress" value="32" max="100" style="width: 60%; height: 18px;"></progress>
  <div id="progress-label">32% Complete</div>
</div>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🔎</span> Workflow Overview
</h2>
<ul>
  <li><b>Commit Script Automation:</b> <br>
    <ul>
      <li>Cleans all Poetry environments for reproducibility and hygiene.</li>
      <li>Ensures pre-commit hooks and lockfile are up-to-date.</li>
      <li>Validates repo state, merges with <code>main</code>, and stages changes.</li>
      <li>Checks for large or secret files before commit.</li>
      <li>Prompts for commit type and message, then commits changes.</li>
      <li>Kicks off the main Nox orchestration (<code>poetry run nox -s commit_flow</code>).</li>
    </ul>
  </li>
  <li><b>Nox Orchestration:</b> <br>
    <ul>
      <li>Registers all Nox sessions: bootstrap, lint, format, typecheck, precommit, tests, notebooks, docs, docker_build, security, commit_flow, cdk_deploy.</li>
      <li><code>commit_flow</code> session orchestrates:</li>
      <ul>
        <li>Bootstrap (serial, ensures Poetry/dev env is ready).</li>
        <li>Code quality checks (lint, format, typecheck, precommit) in parallel.</li>
        <li>Tests and notebook execution in parallel.</li>
        <li>Security checks (serial).</li>
        <li>Docs and Docker build in parallel.</li>
        <li>All steps log to <code>commit_nox_debug.log</code> for traceability.</li>
      </ul>
    </ul>
  </li>
  <li><b>Notebook Hygiene:</b> <br>
    <ul>
      <li>Executes and saves all Jupyter notebooks in the repo, ensuring outputs are fresh and reproducible.</li>
    </ul>
  </li>
  <li><b>Dependency & Environment Management:</b> <br>
    <ul>
      <li>Python version pinned via <code>.python-version</code> (3.12).</li>
      <li>Poetry for dependency management (<code>pyproject.toml</code>).</li>
      <li>Pre-commit hooks for code hygiene (<code>.pre-commit-config.yaml</code>).</li>
    </ul>
  </li>
  <li><b>Build & Deployment:</b> <br>
    <ul>
      <li>Multi-stage Dockerfiles for main, API, and ingestion services.</li>
      <li>Non-root users and healthchecks for security and reliability.</li>
      <li>Compose files orchestrate service startup, healthchecks, and resource limits.</li>
      <li>BuildKit enabled for caching and parallel builds.</li>
      <li>AWS Amplify ensures Node.js 20+ for Docusaurus frontend builds.</li>
      <li>Monorepo config for correct appRoot and build artifact paths.</li>
      <li>AWS CDK for infrastructure as code, gated by <code>CDK_DEPLOY_ENABLED=1</code> for safety.</li>
      <li>Parallel stack deployment via CDK with concurrency.</li>
    </ul>
  </li>
  <li><b>CI/CD Pipeline:</b> <br>
    <ul>
      <li>GitHub Actions runs Nox orchestration, Docker builds, and CDK deploys.</li>
      <li>Caches Poetry/pip, sets up Python from <code>.python-version</code>.</li>
      <li>Deploys only after successful commit flow.</li>
      <li>Optional notification hooks for failed builds.</li>
    </ul>
  </li>
  <li><b>Secrets & Config Management:</b> <br>
    <ul>
      <li>All sensitive secrets managed via AWS Secrets Manager.</li>
      <li>Environment-specific config for S3, networking, MSK, Lambda, OpenSearch, Airbyte, LakeFormation, SageMaker, tags, and compliance.</li>
    </ul>
  </li>
</ul>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">✨</span> Architectural Insights & Best Practices
</h2>
<ul>
  <li><b>Parallelism:</b> Nox and Docker builds leverage parallel execution for speed and efficiency.</li>
  <li><b>Environment Hygiene:</b> Aggressive cleaning of Poetry environments and artifacts ensures reproducibility and reduces “works on my machine” issues.</li>
  <li><b>Security:</b> Pre-commit hooks, secret file checks, and non-root Docker users are best practices for production MLOps.</li>
  <li><b>Cloud-Native:</b> AWS CDK and CLI usage, environment variable-driven config, and BuildKit caching align with modern cloud-native deployment.</li>
  <li><b>Extensibility:</b> Modular Nox sessions and Docker targets make it easy to add new workflows or services.</li>
</ul>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">✅</span> Checklist Alignment
</h2>
<ul>
  <li>Environment hygiene and reproducibility.</li>
  <li>Secrets management via AWS.</li>
  <li>Parallelized CI/CD and build steps.</li>
  <li>Infrastructure as code and cloud-native deployment.</li>
  <li>Automated code quality and security checks.</li>
</ul>
</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1em; background:#181825; color:#a5b4fc; font-size:0.95em; text-align:center;">
  <em>Related: <a href="./project_structure.md" style="color:#a5b4fc;">Project Structure</a> | <a href="./noxfile_workflow.md" style="color:#a5b4fc;">Noxfile & Workflow</a> | <a href="./security_governance.md" style="color:#a5b4fc;">Security & Governance</a></em>
</section>
