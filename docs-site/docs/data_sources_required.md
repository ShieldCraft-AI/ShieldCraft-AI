

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1.5em; background:#111; color:#fff;">
<div style="margin-bottom:1.5em;">
  <a href="./checklist.md" style="color:#a5b4fc; font-weight:bold; text-decoration:none; font-size:1.1em;">⬅️ Back to Checklist</a>
</div>
<h1 align="center" style="margin-top:0; font-size:2em;">📊 Required Data Sources</h1>
<div style="margin-bottom:1.2em; color:#b3b3b3; font-size:1em;">
  This document identifies and describes all data sources required for ShieldCraft AI, including logs, threat intelligence feeds, reports, and configuration files. Each source is mapped to its purpose, format, and integration notes.
</div>
</section>

<section style="border:1px solid #e0e0e0; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #f0f0f0; padding:1.5em; background:#111; color:#fff;">

<h2 style="margin-top:0;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">🔒 Security Logs</h2>
<ul style="margin-bottom:0.5em;">
  <li><b>Types:</b> Cloud provider logs (AWS CloudTrail, Azure Activity Log, GCP Audit Log), Application logs (web server, API gateway, backend services), OS/system logs (Linux syslog, Windows Event Log), Network logs (firewall, IDS/IPS, VPN, proxy)</li>
  <li><b>Purpose:</b> Detect anomalous activity, trace incidents, support compliance</li>
  <li><b>Format:</b> JSON, CSV, syslog, or vendor-specific formats</li>
  <li><b>Integration:</b> Ingested via log shippers (Fluentd, Filebeat), cloud APIs, or direct S3/GCS bucket access</li>
</ul>

<h2 style="margin-top:1.5em;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">🌐 Threat Intelligence Feeds</h2>
<ul style="margin-bottom:0.5em;">
  <li><b>Types:</b> Commercial feeds (Recorded Future, Mandiant, CrowdStrike), Open-source feeds (AbuseIPDB, AlienVault OTX, Spamhaus), Government/ISAC feeds (US-CERT, FS-ISAC)</li>
  <li><b>Purpose:</b> Enrich detection, block known threats, inform risk scoring</li>
  <li><b>Format:</b> STIX/TAXII, CSV, JSON, REST API</li>
  <li><b>Integration:</b> Pull via scheduled API calls, TAXII clients, or vendor SDKs</li>
</ul>

<h2 style="margin-top:1.5em;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">📝 Security Reports</h2>
<ul style="margin-bottom:0.5em;">
  <li><b>Types:</b> Vulnerability scan results (Nessus, Qualys, AWS Inspector), Penetration test reports, Audit/compliance reports (SOC2, GDPR, POPIA)</li>
  <li><b>Purpose:</b> Track vulnerabilities, compliance status, and remediation</li>
  <li><b>Format:</b> PDF, CSV, JSON, HTML</li>
  <li><b>Integration:</b> Manual upload, secure file share, or API (where available)</li>
</ul>

<h2 style="margin-top:1.5em;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">⚙️ Configuration Files</h2>
<ul style="margin-bottom:0.5em;">
  <li><b>Types:</b> Infrastructure-as-Code (Terraform, CloudFormation, CDK), Application configs (YAML, JSON, .env), Security tool configs (IDS/IPS, firewalls, SIEM)</li>
  <li><b>Purpose:</b> Validate secure configuration, detect drift, support automated checks</li>
  <li><b>Format:</b> YAML, JSON, HCL, INI, plaintext</li>
  <li><b>Integration:</b> Pulled from version control (Git), config management tools, or direct upload</li>
</ul>

---

<h2 style="margin-top:1.5em;display:flex;align-items:center;font-size:1.35em;gap:0.5em;">📋 Data Source Mapping Table</h2>

<div style="overflow-x:auto; margin:1.5em 0;">

<table style="width:100%; min-width:700px; border-collapse:separate; border-spacing:0 0.5em;">
  <thead>
    <tr style="background:#23234a; color:#a5b4fc;">
      <th style="padding:0.7em 1em; text-align:left; border-radius:8px 0 0 8px;">Source Type</th>
      <th style="padding:0.7em 1em; text-align:left;">Providers/Tools</th>
      <th style="padding:0.7em 1em; text-align:left;">Format(s)</th>
      <th style="padding:0.7em 1em; text-align:left; border-radius:0 8px 8px 0;">Integration Method</th>
    </tr>
  </thead>
  <tbody style="background:#181825; color:#e0e0e0;">
    <tr>
      <td style="padding:0.7em 1em;">Cloud Logs</td>
      <td style="padding:0.7em 1em;">
        <a href="https://aws.amazon.com/cloudtrail/" style="color:#a5b4fc;">AWS CloudTrail</a>,
        <a href="https://azure.microsoft.com/en-us/products/monitor/" style="color:#a5b4fc;">Azure Monitor</a>,
        <a href="https://cloud.google.com/logging" style="color:#a5b4fc;">GCP Logging</a>
      </td>
      <td style="padding:0.7em 1em;">JSON, CSV</td>
      <td style="padding:0.7em 1em;">API, S3/GCS, log shipper</td>
    </tr>
    <tr>
      <td style="padding:0.7em 1em;">App/Infra Logs</td>
      <td style="padding:0.7em 1em;">
        <a href="https://nginx.org/en/docs/" style="color:#a5b4fc;">Nginx</a>,
        <a href="https://learn.microsoft.com/en-us/windows/win32/eventlog/event-logging" style="color:#a5b4fc;">Windows Event</a>,
        <a href="https://datatracker.ietf.org/doc/html/rfc5424" style="color:#a5b4fc;">Syslog</a>
      </td>
      <td style="padding:0.7em 1em;">Syslog, JSON</td>
      <td style="padding:0.7em 1em;">Log shipper, agent</td>
    </tr>
    <tr>
      <td style="padding:0.7em 1em;">Threat Feeds</td>
      <td style="padding:0.7em 1em;">
        <a href="https://otx.alienvault.com/" style="color:#a5b4fc;">OTX</a>,
        <a href="https://www.crowdstrike.com/" style="color:#a5b4fc;">CrowdStrike</a>
      </td>
      <td style="padding:0.7em 1em;">STIX, JSON, CSV</td>
      <td style="padding:0.7em 1em;">API, TAXII, SDK</td>
    </tr>
    <tr>
      <td style="padding:0.7em 1em;">Vuln Reports</td>
      <td style="padding:0.7em 1em;">
        <a href="https://www.tenable.com/products/nessus" style="color:#a5b4fc;">Nessus</a>,
        <a href="https://www.qualys.com/apps/vulnerability-management/" style="color:#a5b4fc;">Qualys</a>,
        <a href="https://aws.amazon.com/inspector/" style="color:#a5b4fc;">AWS Inspector</a>
      </td>
      <td style="padding:0.7em 1em;">CSV, JSON, PDF</td>
      <td style="padding:0.7em 1em;">API, upload</td>
    </tr>
    <tr>
      <td style="padding:0.7em 1em;">Config Files</td>
      <td style="padding:0.7em 1em;">
        <a href="https://www.terraform.io/" style="color:#a5b4fc;">Terraform</a>,
        <a href="https://yaml.org/" style="color:#a5b4fc;">YAML</a>,
        <a href="https://12factor.net/config" style="color:#a5b4fc;">.env</a>
      </td>
      <td style="padding:0.7em 1em;">YAML, JSON, HCL</td>
      <td style="padding:0.7em 1em;">Git, upload, config mgmt</td>
    </tr>
  </tbody>
</table>

</div>

---

> **See also:** [Data Sources Overview](./data_sources.md) | [Data Preparation Checklist](./checklist.md#💾-data-preparation)

---

<section style="border:1px solid #a5b4fc; border-radius:10px; margin:1.5em 0; box-shadow:0 2px 8px #222; padding:1em; background:#181825; color:#a5b4fc; font-size:0.98em; text-align:center;">
  ShieldCraft AI &mdash; Data Source Inventory & Integration Map
</section>
