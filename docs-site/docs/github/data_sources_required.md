<section style={{ border: '1px solid #a5b4fc', borderRadius: '10px', margin: '1.5em 0', boxShadow: '0 2px 8px #222', padding: '1.5em', background: '#111', color: '#fff' }}>
<div style={{ marginBottom: '1.5em' }}>
  <a href="../../../README.md" style={{ color: '#a5b4fc', fontWeight: 'bold', textDecoration: 'none', fontSize: '1.1em' }}>⬅️ Back to Project Overview</a>
</div>

# 📊 Required Data Sources

This document identifies and describes all data sources required for ShieldCraft AI, including logs, threat intelligence feeds, reports, and configuration files. Each source is mapped to its purpose, format, and integration notes.

---

## 🔒 Security Logs

- **Types:** Cloud provider logs (AWS CloudTrail, Azure Activity Log, GCP Audit Log), Application logs (web server, API gateway, backend services), OS/system logs (Linux syslog, Windows Event Log), Network logs (firewall, IDS/IPS, VPN, proxy)
- **Purpose:** Detect anomalous activity, trace incidents, support compliance
- **Format:** JSON, CSV, syslog, or vendor-specific formats
- **Integration:** Ingested via log shippers (Fluentd, Filebeat), cloud APIs, or direct S3/GCS bucket access

## 🌐 Threat Intelligence Feeds

- **Types:** Commercial feeds (Recorded Future, Mandiant, CrowdStrike), Open-source feeds (AbuseIPDB, AlienVault OTX, Spamhaus), Government/ISAC feeds (US-CERT, FS-ISAC)
- **Purpose:** Enrich detection, block known threats, inform risk scoring
- **Format:** STIX/TAXII, CSV, JSON, REST API
- **Integration:** Pull via scheduled API calls, TAXII clients, or vendor SDKs

## 📝 Security Reports

- **Types:** Vulnerability scan results (Nessus, Qualys, AWS Inspector), Penetration test reports, Audit/compliance reports (SOC2, GDPR, POPIA)
- **Purpose:** Track vulnerabilities, compliance status, and remediation
- **Format:** PDF, CSV, JSON, HTML
- **Integration:** Manual upload, secure file share, or API (where available)

## ⚙️ Configuration Files

- **Types:** Infrastructure-as-Code (Terraform, CloudFormation, CDK), Application configs (YAML, JSON, .env), Security tool configs (IDS/IPS, firewalls, SIEM)
- **Purpose:** Validate secure configuration, detect drift, support automated checks
- **Format:** YAML, JSON, HCL, INI, plaintext
- **Integration:** Pulled from version control (Git), config management tools, or direct upload

---

## 📋 Data Source Mapping Table

| Source Type    | Providers/Tools                                                                 | Format(s)           | Integration Method           |
|----------------|--------------------------------------------------------------------------------|---------------------|-----------------------------|
| Cloud Logs     | [AWS CloudTrail](https://aws.amazon.com/cloudtrail/), [Azure Monitor](https://azure.microsoft.com/en-us/products/monitor/), [GCP Logging](https://cloud.google.com/logging) | JSON, CSV           | API, S3/GCS, log shipper    |
| App/Infra Logs | [Nginx](https://nginx.org/en/docs/), [Windows Event](https://learn.microsoft.com/en-us/windows/win32/eventlog/event-logging), [Syslog](https://datatracker.ietf.org/doc/html/rfc5424) | Syslog, JSON        | Log shipper, agent          |
| Threat Feeds   | [OTX](https://otx.alienvault.com/), [CrowdStrike](https://www.crowdstrike.com/) | STIX, JSON, CSV     | API, TAXII, SDK             |
| Vuln Reports   | [Nessus](https://www.tenable.com/products/nessus), [Qualys](https://www.qualys.com/apps/vulnerability-management/), [AWS Inspector](https://aws.amazon.com/inspector/) | CSV, JSON, PDF      | API, upload                 |
| Config Files   | [Terraform](https://www.terraform.io/), [YAML](https://yaml.org/), [.env](https://12factor.net/config) | YAML, JSON, HCL     | Git, upload, config mgmt    |

---

**See also:** [Data Sources Overview](./data_sources.md) | [Data Preparation Checklist](./checklist.md#💾-data-preparation)

---

_ShieldCraft AI: Data Source Inventory & Integration Map_
