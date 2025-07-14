[⬅️ Back to Checklist](../checklist.md)

# 🗂️ ShieldCraft AI Data Inputs Overview

## Purpose

This document describes the modular, extensible data ingestion architecture for ShieldCraft AI. It details supported input types, schema governance, and onboarding for new data sources. All design aligns with production-grade, cloud-native, and privacy-first MLOps best practices.

## Supported Data Input Types

| Type | Description | Example Sources |
| --- | --- | --- |
| Security Logs | Structured/unstructured logs from SIEM, firewalls, EDR, cloud, and OS. | CloudTrail, VPC Flow Logs, Syslog, Windows Event Log, Splunk |
| Threat Feeds | External or internal threat intelligence feeds | AlienVault OTX, MISP, AWS GuardDuty, STIX/TAXII, AbuseIPDB |
| Cloud Events | Cloud resource/configuration change events | AWS Config, S3 Events, IAM, Lambda logs |
| Application Logs | Web/API server logs, custom app logs | CloudWatch, API Gateway, Nginx, custom JSON |
| Vulnerability Scans | Automated scan results and findings | Nessus, AWS Inspector, Snyk, Trivy |
| Asset Inventory | CMDB, cloud, and network asset lists | AWS Resource Inventory, network scans |
| User/Identity Data | Authentication, SSO, and identity logs | IAM, Okta, Active Directory, SSO logs |
| Incident Reports | Case management, ticketing, or analyst notes | Jira, ServiceNow, custom CSV/JSON |
| Configuration Files | System, network, or application configs | YAML, JSON, INI, AWS Config |
| Knowledge Base | Playbooks, SOPs, documentation | Markdown, Confluence, SharePoint |
| Ticketing/Workflow | Incident response, workflow, and ticketing | Jira, ServiceNow, custom platforms |

All input types are processed via modular connectors and normalized to a unified schema for downstream AI and analytics. Additional sources can be onboarded as needed for new use cases.

See also:

* Data Sources & Expected Outputs
* Required Data Sources

## Modular Data Ingestion Architecture

* Connector-based:Each source type uses a dedicated, reusable connector (e.g., Airbyte, AWS Lambda, custom ETL).
* Streaming & Batch:Supports both real-time (Kafka/MSK, Kinesis) and batch (S3, Glue) ingestion.
* Schema Normalization:All data is mapped to a versioned, extensible schema (seeschemas.md).
* Governance:Data quality, lineage, and privacy enforced via Lake Formation, Great Expectations, and Deequ.
* Extensibility:New sources can be onboarded with minimal code changes, see onboarding below.

## Onboarding a New Data Source

1. Define the new source and its business value.
1. Implement or configure a connector (Airbyte, Lambda, or custom ETL).
1. Map fields to the unified schema
1. Register the source in the data catalog (Lake Formation).
1. Set up data quality checks and privacy controls.
1. Test end-to-end ingestion and validate with sample data.
1. Document the new source and update onboarding guides.

Related:Checklist|Schemas|Risk Log

<!-- Unhandled tags: em, li -->
