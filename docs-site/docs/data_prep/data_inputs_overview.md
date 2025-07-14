
<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="../checklist.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<h1 align="center" style="margin-top:0; font-size:2em; color:#a5b4fc;">🗂️ ShieldCraft AI Data Inputs Overview</h1>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">Purpose</h2>
<div style="color:#b3b3b3;">This document describes the modular, extensible data ingestion architecture for ShieldCraft AI. It details supported input types, schema governance, and onboarding for new data sources. All design aligns with production-grade, cloud-native, and privacy-first MLOps best practices.</div>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">Supported Data Input Types</h2>
<table style="width:100%; background:#181818; color:#fff; border-radius:8px; margin-bottom:1.5em;">
  <thead style="background:#232323; color:#a5b4fc;">
    <tr>
      <th style="text-align:left;">Type</th>
      <th style="text-align:left;">Description</th>
      <th style="text-align:left;">Example Sources</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Security Logs</td><td>Structured/unstructured logs from SIEM, firewalls, EDR, cloud, and OS.</td><td>CloudTrail, VPC Flow Logs, Syslog, Windows Event Log, Splunk</td></tr>
    <tr><td>Threat Feeds</td><td>External or internal threat intelligence feeds</td><td>AlienVault OTX, MISP, AWS GuardDuty, STIX/TAXII, AbuseIPDB</td></tr>
    <tr><td>Cloud Events</td><td>Cloud resource/configuration change events</td><td>AWS Config, S3 Events, IAM, Lambda logs</td></tr>
    <tr><td>Application Logs</td><td>Web/API server logs, custom app logs</td><td>CloudWatch, API Gateway, Nginx, custom JSON</td></tr>
    <tr><td>Vulnerability Scans</td><td>Automated scan results and findings</td><td>Nessus, AWS Inspector, Snyk, Trivy</td></tr>
    <tr><td>Asset Inventory</td><td>CMDB, cloud, and network asset lists</td><td>AWS Resource Inventory, network scans</td></tr>
    <tr><td>User/Identity Data</td><td>Authentication, SSO, and identity logs</td><td>IAM, Okta, Active Directory, SSO logs</td></tr>
    <tr><td>Incident Reports</td><td>Case management, ticketing, or analyst notes</td><td>Jira, ServiceNow, custom CSV/JSON</td></tr>
    <tr><td>Configuration Files</td><td>System, network, or application configs</td><td>YAML, JSON, INI, AWS Config</td></tr>
    <tr><td>Knowledge Base</td><td>Playbooks, SOPs, documentation</td><td>Markdown, Confluence, SharePoint</td></tr>
    <tr><td>Ticketing/Workflow</td><td>Incident response, workflow, and ticketing</td><td>Jira, ServiceNow, custom platforms</td></tr>
  </tbody>
</table>
<div style="color:#b3b3b3;">All input types are processed via modular connectors and normalized to a unified schema for downstream AI and analytics. Additional sources can be onboarded as needed for new use cases.</div>

<div style="margin-top:1.5em; color:#a5b4fc; font-weight:bold;">See also:</div>
<ul style="color:#b3b3b3; margin-bottom:0;">
</ul>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">Modular Data Ingestion Architecture</h2>
<ul style="color:#e0e0e0;">
</ul>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<h2 style="color:#a5b4fc; margin-top:0;">Onboarding a New Data Source</h2>
<ol style="color:#e0e0e0;">
</ol>

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:2em 0 0 0; box-shadow:0 2px 8px #222; padding:1em; background:#181825; color:#a5b4fc; font-size:0.95em; text-align:center;">
  <em>Related: <a href="../checklist.md" style="color:#a5b4fc;">Checklist</a> | <a href="./schemas.md" style="color:#a5b4fc;">Schemas</a> | <a href="../risk_log.md" style="color:#a5b4fc;">Risk Log</a></em>
