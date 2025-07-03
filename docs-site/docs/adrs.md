<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="./checklist.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<h1 align="center" style="margin-top:0; font-size:2em;">🛡️ ShieldCraft AI: Architecture Decision Records (ADRs)</h1>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">

<p style="color:#b3b3b3;">This document tracks key architectural decisions for ShieldCraft AI. Each ADR includes context, decision, and consequences.</p>

---

<table style="width:100%; text-align:left; background:#181818; color:#fff; border-radius:8px;">
  <thead style="background:#232323; color:#a5b4fc;">
    <tr>
      <th style="width:20%">ADR</th>
      <th style="width:25%">Context</th>
      <th style="width:25%">Decision</th>
      <th style="width:30%">Consequences</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Cloud Provider Selection</b></td>
      <td>Need for scalable, secure, and cost-effective infrastructure.</td>
      <td>Use AWS as primary cloud provider; design for future multi-cloud support.</td>
      <td>Leverages AWS services, but some vendor lock-in.</td>
    </tr>
    <tr>
      <td><b>Container Orchestration</b></td>
      <td>Need for scalable deployment and management of microservices.</td>
      <td>Use Amazon ECS/EKS for orchestration.</td>
      <td>Simplifies scaling, but requires AWS-specific expertise.</td>
    </tr>
    <tr>
      <td><b>Vector Database</b></td>
      <td>Need for efficient similarity search for RAG and AI features.</td>
      <td>Use Postgres with pgvector extension for MVP.</td>
      <td>Lower cost and operational complexity for MVP; can migrate to managed vector DB later.</td>
    </tr>
  </tbody>
</table>

---

<h3 style="color:#a5b4fc;">How to Use</h3>
<ul>
  <li>Add a new ADR for each major technical or architectural decision.</li>
  <li>Reference ADRs in code and documentation where relevant.</li>
</ul>

</section>
<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1em; background:#181825; color:#a5b4fc; font-size:0.95em; text-align:center;">
  <em>Related: <a href="./risk_log.md" style="color:#a5b4fc;">Risk Log</a> | <a href="./threat_modeling.md" style="color:#a5b4fc;">Threat Modeling</a> | <a href="./security_governance.md" style="color:#a5b4fc;">Security & Governance</a></em>
</section>
