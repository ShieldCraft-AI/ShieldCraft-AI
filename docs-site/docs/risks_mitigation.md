<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="./checklist.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<h1 align="center" style="margin-top:0; font-size:2em;">⚠️ ShieldCraft AI: Technical, Ethical & Operational Risks</h1>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">

## Overview
This document identifies and tracks the major technical, ethical, and operational risks for ShieldCraft AI, along with mitigation strategies and status. Risks are reviewed at each milestone and updated as the project evolves.

---

<table style="width:100%; text-align:center; background:#181818; color:#fff; border-radius:8px;">
  <thead style="background:#232323; color:#a5b4fc;">
    <tr>
      <th>Risk</th>
      <th>Category</th>
      <th>Likelihood</th>
      <th>Impact</th>
      <th>Mitigation</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>LLM hallucination or unsafe output</td><td>Technical/Ethical</td><td>High</td><td>High</td><td>Output validation, prompt engineering, human-in-the-loop review</td><td>Open</td></tr>
    <tr><td>Model bias or discrimination</td><td>Ethical</td><td>Medium</td><td>High</td><td>Bias audits, diverse data, explainability, regular reviews</td><td>Open</td></tr>
    <tr><td>Data privacy breach (PII/PHI)</td><td>Operational/Compliance</td><td>Medium</td><td>High</td><td>Encryption, access controls, privacy impact assessments</td><td>Open</td></tr>
    <tr><td>Cloud cost overrun</td><td>Operational</td><td>Medium</td><td>Medium</td><td>Cost monitoring, alerts, reserved/spot instances</td><td>Open</td></tr>
    <tr><td>Service downtime/outage</td><td>Operational</td><td>Low</td><td>High</td><td>Multi-AZ, backups, incident response plan</td><td>Open</td></tr>
    <tr><td>Regulatory non-compliance</td><td>Compliance</td><td>Low</td><td>High</td><td>Legal review, compliance matrix, regular audits</td><td>Open</td></tr>
    <tr><td>Data pipeline failure</td><td>Technical</td><td>Medium</td><td>Medium</td><td>Monitoring, retries, alerting</td><td>Open</td></tr>
    <tr><td>Model drift or performance degradation</td><td>Technical</td><td>Medium</td><td>Medium</td><td>Model monitoring, retraining, feedback loops</td><td>Open</td></tr>
    <tr><td>Insufficient documentation or onboarding</td><td>Operational</td><td>Medium</td><td>Medium</td><td>Continuous doc updates, onboarding guides, training</td><td>Open</td></tr>
  </tbody>
</table>

---

## 📋 Next Steps
<ul>
  <li>Review and update risk log at each project milestone.</li>
  <li>Assign owners for each open risk and track mitigation progress.</li>
  <li>Integrate risk review into regular project meetings.</li>
  <li>See also: <a href="./risk_log.md" style="color:#a5b4fc;">Full Risk Log</a></li>
</ul>

</section>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1em; background:#181825; color:#a5b4fc; font-size:0.95em; text-align:center;">
  <em>Related: <a href="./risks_mitigation.md" style="color:#a5b4fc;">Risk Mitigation</a> | <a href="./adrs.md" style="color:#a5b4fc;">ADRs</a> | <a href="./risk_log.md" style="color:#a5b4fc;">Risk Log</a></em>
</section>
