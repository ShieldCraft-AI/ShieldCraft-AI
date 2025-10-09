<div align="center" style="display: flex; align-items: center; justify-content: center; margin-bottom:2em">
  <img src="https://img.shields.io/badge/AI%20Security-Shieldcraft%20AI-blueviolet?style=for-the-badge&logo=amazonaws&logoColor=white" alt="Shieldcraft AI" />
  <a href="https://github.com/Dee66/shieldcraft-ai/actions/workflows/ci.yml" style="margin-left: 1.5em; float: right;">
    <img src="https://github.com/Dee66/shieldcraft-ai/actions/workflows/ci.yml/badge.svg" alt="CI Status" style="vertical-align: middle;" />
  </a>
</div>

<h1 align="center"><img src="docs-site/static/img/logo.png" alt="ShieldCraft AI" style="height:48px;width:auto;vertical-align:middle;border-radius:8px;" /> ShieldCraft AI</h1>
<p align="center"><em>Next-Gen Cloud Cybersecurity: Proactive, Adaptive, Autonomous.</em></p>

<div align="center" style="margin-bottom:1em;">
  <a href="https://github.com/Dee66/CodeCraft-AI" style="color:#a5b4fc; font-size:0.98em;">
    <b>✨ See also: CodeCraft AI – My first custom AI implementation</b>
  </a>
</div>

<div align="center" style="margin-bottom:2em;">
  <a href="https://github.com/Dee66/supervised-learning" style="color:#a5b4fc; font-size:0.98em;">
    <b>✨ See also: Supervised ML: ML theory and real-world system design</b>
  </a>
</div>

<div id="progress-bar" align="center" style="margin-bottom:1.5em;">
  <strong>Project Progress</strong>
  <a href="./docs-site/docs/github/checklist.md" style="margin-left:0.75em; font-size:0.95em; color:#a5b4fc; text-decoration:none;">(checklist)</a><br/>
  <progress id="shieldcraft-progress" value="80" max="100" style="width: 60%; height: 18px;"></progress>
  <div id="progress-label">80% Complete</div>
</div>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🔎</span> Intent
</h2>
<div style="border-left:4px solid #a5b4fc; padding-left:1em; margin-bottom:1em;">
ShieldCraft AI is my capstone architecture artifact, synthesizing AWS platform depth with applied GenAI/ML and security/cloud governance practice. It demonstrates how I design infrastructure via environment‑aware IaC with cost‑optimized service variants to preserve security posture whilst following AWS best practice. The platform enforces structured, auditable remediation planning by running governed ETL jobs to land normalized, lineage‑rich security and configuration telemetry in a queryable data lake, then applying a security‑tuned GenAI layer to score risk and generate reasoned remediation plans, rollback intent, all within approved boundaries. It operationalizes certification domains: secure multi‑account design, governed data layers, least‑privilege and tagging discipline, structured GenAI integration, and resilient deployment patterns, translating theory and ML into proactive threat detection.
</div>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🧠</span> Architecture Principles
</h2>
<ul style="margin:0 0 0.75em 0; font-size:0.95em;">
  <li><b>Guardrails before autonomy:</b> structure & validation precede model freedom.</li>
  <li><b>Environment specificity:</b> every resource name & tag encodes scope and cost intent.</li>
  <li><b>Reversibility:</b> remediation plans must embed rollback intent.</li>
  <li><b>Deterministic foundations for GenAI:</b> retrieval & schema contracts reduce ambiguity.</li>
  <li><b>Cost visibility early:</b> budgets + lifecycle from the first deploy.</li>
  <li><b>Test unhappy paths first:</b> failure modes treated as first‑class design inputs.</li>
</ul>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🧩</span> Core Capabilities
</h2>
<ul style="margin:0 0 0.75em 0; font-size:0.95em;">
  <li><b>Environment isolation & blast radius control:</b> multi‑env CDK stacks with explicit naming + tagging.</li>
  <li><b>Fail‑fast safety layer:</b> Pydantic config + negative path tests block misdeploys early.</li>
  <li><b>Governed data ingestion foundation:</b> ETL scaffolding lands normalized, queryable security & config telemetry (S3 + Glue + Lake Formation).</li>
  <li><b>Structured remediation planning:</b> schema‑validated plans (risk_score, rationale, actions, rollback intent, approval mode).</li>
  <li><b>Cost & governance discipline:</b> budgets, lifecycle policies, standardized tags, least‑privilege intent.</li>
  <li><b>Retrieval readiness:</b> static RAG corpus + interface boundary for future embedding/vector search.</li>
  <li><b>Observability baselines:</b> metrics & audit artifact emission patterns defined (expansion staged).</li>
</ul>
</section>


<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">📚</span> Deep Dive
</h2>
<ul style="margin-bottom:0.5em;">
  <li><a href="./docs-site/docs/github/spec.md" style="color:#a5b4fc;"><b>Platform Architecture</b></a> Business case, architecture, and technical blueprint</li>
  <li><a href="./docs-site/docs/github/attack-simulation.md" style="color:#a5b4fc;"><b>Simulated Attack Testing & BAS</b></a> Automated attack simulation, breach and attack simulation and continuous validation strategies</li>
  <li><a href="./docs-site/docs/github/poa.md" style="color:#a5b4fc;"><b>GenAI Implementation Lifecycle</b></a> Step-by-step GenAI buildout</li>
  <li><a href="./docs-site/docs/github/tooling.md" style="color:#a5b4fc;"><b>Tech Stack and Utilities</b></a> Tech, tools and libraries used</li>
  <li><a href="./docs-site/docs/github/checklist.md" style="color:#a5b4fc;"><b>Project Checklist</b></a> Key milestones and action items</li>
</ul>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🎓</span> Certification Alignment
</h2>
<table style="width:100%; font-size:0.85em; border-collapse:collapse;">
  <thead>
    <tr style="background:#1b1b1b;">
      <th style="text-align:left; padding:6px; border-bottom:1px solid #333;">Domain Focus</th>
      <th style="text-align:left; padding:6px; border-bottom:1px solid #333;">Implementation</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="padding:6px;">SAA‑C03 Secure Architecture</td><td style="padding:6px;">Env isolation, least‑privilege permissions, cost estimates & budgets, standardized tagging for observability, environment‑scoped config validation</td></tr>
    <tr><td style="padding:6px;">SAA‑C03 Reliability & Ops</td><td style="padding:6px;">Extensive testing, modular domain stacks, defense‑in‑depth, stack isolation, tested fail-over and DR strategies</td></tr>
    <tr><td style="padding:6px;">AIF‑C01 GenAI Integration</td><td style="padding:6px;">Environment aware model implemenation (Mistral-7B-v0.1 as dev FM)</td></tr>
    <tr><td style="padding:6px;">Data Governance</td><td style="padding:6px;">Lake Formation / Glue scaffolding, normalized telemetry intent</td></tr>
    <tr><td style="padding:6px;">FinOps Discipline</td><td style="padding:6px;">Cost guardrails, environment service variance, lifecycle policies</td></tr>
    <tr><td style="padding:6px;">Security Posture</td><td style="padding:6px;">GuardDuty / Security Hub / Inspector domains, remediation guardrail design</td></tr>
  </tbody>
</table>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">📊</span> Status & Roadmap
</h2>

<table style="width:100%; font-size:0.9em; border-collapse:collapse;">
  <thead style="background:#1b1b1b;">
    <tr>
      <th style="text-align:left; padding:6px; border-bottom:1px solid #333;">Domain</th>
      <th style="text-align:left; padding:6px; border-bottom:1px solid #333;">Implemented</th>
      <th style="text-align:left; padding:6px; border-bottom:1px solid #333;">In Progress</th>
      <th style="text-align:left; padding:6px; border-bottom:1px solid #333;">Planned</th>
    </tr>
  </thead>
  <tbody>
    <tr><td style="padding:6px;">Env‑aware IaC & tagging</td><td style="padding:6px;">✅</td><td style="padding:6px;"></td><td style="padding:6px;">-</td></tr>
    <tr><td style="padding:6px;">Config validation (Pydantic)</td><td style="padding:6px;">✅</td><td style="padding:6px;"></td><td style="padding:6px;">Enhance drift detection</td></tr>
    <tr><td style="padding:6px;">Cost guardrails & budgets</td><td style="padding:6px;">✅</td><td style="padding:6px;"></td><td style="padding:6px;">Token/inference attribution</td></tr>
    <tr><td style="padding:6px;">Remediation plan schema</td><td style="padding:6px;">✅</td><td style="padding:6px;">Approval workflow docs</td><td style="padding:6px;">Rollback simulation</td></tr>
    <tr><td style="padding:6px;">ETL / data governance scaffolding</td><td style="padding:6px;">✅ (S3 / Glue / Lake Formation)</td><td style="padding:6px;">Lineage enrichment</td><td style="padding:6px;">Retention automation</td></tr>
    <tr><td style="padding:6px;">RAG retrieval (stub)</td><td style="padding:6px;">✅ (static corpus)</td><td style="padding:6px;">Embedding pipeline</td><td style="padding:6px;">Relevance eval harness</td></tr>
    <tr><td style="padding:6px;">Security posture layers</td><td style="padding:6px;">✅ (GuardDuty / Hub / Inspector)</td><td style="padding:6px;">Threat model doc</td><td style="padding:6px;">Attack scenario injection</td></tr>
    <tr><td style="padding:6px;">Observability baseline</td><td style="padding:6px;">✅ (logging + tests)</td><td style="padding:6px;">Metrics expansion</td><td style="padding:6px;">SLOs & error budgets</td></tr>
    <tr><td style="padding:6px;">ADRs</td><td style="padding:6px;">Foundational set pending</td><td style="padding:6px;">Model / guardrails / retrieval</td><td style="padding:6px;">Cost & rollback strategy</td></tr>
  </tbody>
</table>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">🛠️</span> Developer Workflow
</h2>
<div style="border-left:4px solid #a5b4fc; padding-left:1em; margin-bottom:1em;">

<b>⚡️ AWS Infrastructure Deployment Modernization (2025):</b><br>
All AWS infrastructure is now deployed using <b>AWS CDK v2</b> and <b>AWS CLI v2</b> only. <b>IAM Identity Center (formerly SSO)</b> is required for all developer and CI/CD authentication. Static AWS credentials and CDK v1 are no longer supported.<br>
See <a href="./docs-site/docs/github/developer-workflow.md" style="color:#a5b4fc;"><b>🛠️ Developer Workflow</b></a> for onboarding and SSO/OIDC setup instructions.
</div>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">
<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">
  <span style="font-size:1.2em;">📄</span> License
</h2>
<div style="border-left:4px solid #a5b4fc; padding-left:1em; margin-bottom:1em;">
MIT License
</div>
</section>
