<div align="center">
  <img src="https://img.shields.io/badge/Containerization-Docker%20%7C%20Chainguard-blue?style=for-the-badge&logo=docker&logoColor=white" alt="Docker & Chainguard" />
</div>

<h1 align="center">🐳 ShieldCraft AI Dockerization</h1>
<p align="center"><em>Secure, Reproducible, and Production-Ready Container Builds</em></p>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🔎</span> Overview
</h2>
<div style="border-left:4px solid #a5b4fc; padding-left:1em; margin-bottom:1em;">
ShieldCraft AI uses a modern, multi-stage Docker build process for all core services (<b>main</b>, <b>api</b>, <b>ingestion</b>), leveraging <b>Chainguard Python</b> images for minimal attack surface and zero-known CVEs. This ensures secure, reproducible, and environment-specific containers for development, staging, and production.
</div>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">⚙️</span> Build Stages & Process
</h2>
<ul style="margin-bottom:0.5em;">
  <li><b>Base</b>: Chainguard Python image, sets up secure environment and working directory.</li>
  <li><b>Dev</b>: Installs dev tools (pipx, poetry), all dependencies (with dev extras), and full source for rapid iteration and testing.</li>
  <li><b>Staging</b>: Installs only main dependencies, exports requirements, removes dev/test files and caches, and switches to a non-root user for security.</li>
  <li><b>Prod</b>: Inherits from staging, ensuring a clean, production-ready environment.</li>
  <li><b>Final</b>: Uses Chainguard again for a distroless, secure runtime. Copies only built app and dependencies, sets up healthchecks and entrypoints.</li>
</ul>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🧩</span> Orchestration & CI
</h2>
<ul style="margin-bottom:0.5em;">
  <li><b>docker-compose.yml</b> orchestrates all services, mapping volumes for live reload (dev), healthchecks, and resource limits.</li>
  <li><b>GitHub Actions CI</b> builds all images for each service and stage, ensuring reproducibility and security.</li>
  <li><b>nox_sessions/docker.py</b> provides local build and vulnerability scan automation (Trivy, Grype).</li>
</ul>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🔒</span> Security & Best Practices
</h2>
<ul style="margin-bottom:0.5em;">
  <li>All images use <b>Chainguard</b> for minimal, continuously-patched Python runtimes.</li>
  <li>Non-root user enforced in all runtime stages.</li>
  <li>Dev/test files and build artifacts are removed from production images.</li>
  <li>Healthchecks and explicit entrypoints for orchestrator compatibility.</li>
  <li>Automated vulnerability scanning (Trivy, Grype) in local and CI workflows.</li>
</ul>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🚀</span> Quick Reference
</h2>
<ul style="margin-bottom:0.5em;">
  <li><b>Build (dev):</b> <code>docker build --target=dev -t shieldcraft-main:dev .</code></li>
  <li><b>Build (staging):</b> <code>docker build --target=staging -t shieldcraft-main:staging .</code></li>
  <li><b>Build (prod/final):</b> <code>docker build --target=final -t shieldcraft-main:prod .</code></li>
  <li><b>Compose up:</b> <code>docker-compose up --build</code></li>
  <li><b>CI:</b> See <a href=".github/workflows/ci.yml" style="color:#a5b4fc;">ci.yml</a> for full build/test pipeline.</li>
</ul>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">📚</span> Further Reading
</h2>
<ul style="margin-bottom:0.5em;">
  <li><a href="https://github.com/chainguard-images/images/tree/main/images/python" style="color:#a5b4fc;">Chainguard Python</a> (base image)</li>
  <li><a href="https://docs.docker.com/build/buildkit/" style="color:#a5b4fc;">Docker BuildKit</a> (caching, parallelism)</li>
  <li><a href="https://aquasecurity.github.io/trivy/" style="color:#a5b4fc;">Trivy</a> & <a href="https://github.com/anchore/grype" style="color:#a5b4fc;">Grype</a> (vulnerability scanning)</li>
  <li><a href="../../README.md" style="color:#a5b4fc;">Project README</a></li>
</ul>
</section>
