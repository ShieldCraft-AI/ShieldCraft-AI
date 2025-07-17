from pathlib import Path
import re

# --- Section-to-Signal Mapping ---
SECTION_SIGNALS = {
    "AWS Cloud Foundation": [
        {"type": "dir", "path": "infra/"},
        {"type": "file", "path": "docs-site/docs/github/aws_stack_architecture.md"},
        {"type": "file", "path": "infra/stacks/stack-context.txt"},
        {"type": "test", "path": "tests/infra/test_cloud_native_hardening_stack.py"},
        {"type": "test", "path": "tests/infra/test_networking_stack.py"},
        {"type": "test", "path": "tests/infra/test_s3_stack.py"},
        {"type": "test", "path": "tests/infra/test_glue_stack.py"},
        {"type": "test", "path": "tests/infra/test_lambda_stack.py"},
        {"type": "test", "path": "tests/infra/test_lakeformation_stack.py"},
        {"type": "test", "path": "tests/infra/test_attack_simulation_stack.py"},
        {"type": "test", "path": "tests/infra/test_iam_role_stack.py"},
        {"type": "test", "path": "tests/infra/test_msk_topics_integration.py"},
        {"type": "test", "path": "tests/infra/test_opensearch_stack.py"},
        {"type": "test", "path": "tests/infra/test_budget_stack.py"},
        {"type": "test", "path": "tests/infra/test_msk_stack.py"},
        {"type": "test", "path": "tests/infra/test_compliance_stack.py"},
        {"type": "test", "path": "tests/infra/test_airbyte_stack.py"},
        {"type": "test", "path": "tests/infra/test_dataquality_stack.py"},
        {"type": "test", "path": "tests/infra/test_sagemaker_stack.py"},
        {"type": "test", "path": "tests/infra/test_secrets_manager_stack.py"},
        {"type": "test", "path": "tests/infra/test_eventbridge_stack.py"},
        {"type": "test", "path": "tests/infra/test_cloud_native_hardening_stack.py"},
    ],
    "Data Preparation": [
        {"type": "dir", "path": "data_prep/"},
        {"type": "file", "path": "docs-site/docs/data_prep/data_inputs_overview.md"},
        {"type": "test", "path": "tests/infra/test_dataquality_stack.py"},
        {"type": "file", "path": "data_prep/api_gateway_logs/schema.py"},
        {"type": "file", "path": "data_prep/api_gateway_logs/ingest.py"},
        {"type": "file", "path": "data_prep/tickets/schema.py"},
        {"type": "file", "path": "data_prep/tickets/ingest.py"},
        {"type": "file", "path": "data_prep/configs/schema.py"},
        {"type": "file", "path": "data_prep/configs/ingest.py"},
        {"type": "file", "path": "data_prep/custom_telemetry/schema.py"},
        {"type": "file", "path": "data_prep/custom_telemetry/ingest.py"},
        {"type": "file", "path": "data_prep/logs/schema.py"},
        {"type": "file", "path": "data_prep/logs/ingest.py"},
        {"type": "file", "path": "data_prep/email_security/schema.py"},
        {"type": "file", "path": "data_prep/email_security/ingest.py"},
        {"type": "file", "path": "data_prep/osint/schema.py"},
        {"type": "file", "path": "data_prep/osint/ingest.py"},
        {"type": "file", "path": "data_prep/threat_feed/schema.py"},
        {"type": "file", "path": "data_prep/threat_feed/ingest.py"},
        {"type": "file", "path": "data_prep/dlp_events/schema.py"},
        {"type": "file", "path": "data_prep/dlp_events/ingest.py"},
        {"type": "file", "path": "data_prep/assets/schema.py"},
        {"type": "file", "path": "data_prep/assets/ingest.py"},
        {"type": "file", "path": "data_prep/vuln_scans/schema.py"},
        {"type": "file", "path": "data_prep/vuln_scans/ingest.py"},
        {"type": "file", "path": "data_prep/container_events/schema.py"},
        {"type": "file", "path": "data_prep/container_events/ingest.py"},
        {"type": "file", "path": "data_prep/endpoint_telemetry/schema.py"},
        {"type": "file", "path": "data_prep/endpoint_telemetry/ingest.py"},
        {"type": "file", "path": "data_prep/alerts/schema.py"},
        {"type": "file", "path": "data_prep/alerts/ingest.py"},
        {"type": "file", "path": "data_prep/network_flows/schema.py"},
        {"type": "file", "path": "data_prep/network_flows/ingest.py"},
        {"type": "file", "path": "data_prep/saas_security/schema.py"},
        {"type": "file", "path": "data_prep/saas_security/ingest.py"},
        {"type": "file", "path": "data_prep/user_identities/schema.py"},
        {"type": "file", "path": "data_prep/user_identities/ingest.py"},
    ],
    "AI Core Development": [
        {"type": "dir", "path": "src/shieldcraft_ai/"},
        {"type": "file", "path": "docs-site/docs/github/checklist.md"},
        {"type": "test", "path": "tests/test_stepfunctions_stack.py"},
        {"type": "file", "path": "src/shieldcraft_ai/main.py"},
        {"type": "file", "path": "src/shieldcraft_ai/config.py"},
        {"type": "dir", "path": "src/shieldcraft_ai/utils/"},
        {"type": "file", "path": "src/shieldcraft_ai/__init__.py"},
    ],
    "Application Layer & Integration": [
        {"type": "dir", "path": "src/api/"},
        {"type": "file", "path": "src/api/main.py"},
        {"type": "file", "path": "src/api/__init__.py"},
        {"type": "file", "path": "src/main.py"},
        {"type": "file", "path": "src/main_healthcheck.py"},
    ],
    "MLOps, Deployment & Monitoring": [
        {"type": "file", "path": "noxfile.py"},
        {"type": "file", "path": "Dockerfile"},
        {"type": "file", "path": "docker-compose.yml"},
        {"type": "file", "path": "docker-compose.override.yml"},
        {"type": "file", "path": "pyproject.toml"},
        {"type": "file", "path": "poetry.lock"},
        {"type": "file", "path": "requirements.txt"},
        {"type": "file", "path": "pytest.ini"},
        {"type": "file", "path": ".pre-commit-config.yaml"},
        {"type": "file", "path": "nox_sessions/test.py"},
        {"type": "file", "path": "nox_sessions/deploy.py"},
        {"type": "file", "path": "nox_sessions/commit.py"},
        {"type": "file", "path": "nox_sessions/docker.py"},
        {"type": "file", "path": "nox_sessions/yaml.py"},
        {"type": "file", "path": "nox_sessions/security.py"},
        {"type": "file", "path": "nox_sessions/notebook.py"},
        {"type": "file", "path": "nox_sessions/release.py"},
        {"type": "file", "path": "nox_sessions/utils_poetry.py"},
        {"type": "file", "path": "nox_sessions/utils_color.py"},
        {"type": "file", "path": "nox_sessions/utils_encoding.py"},
        {"type": "file", "path": "nox_sessions/docs.py"},
        {"type": "file", "path": "nox_sessions/lint.py"},
        {"type": "file", "path": "nox_sessions/utils.py"},
        {"type": "file", "path": "nox_sessions/bootstrap.py"},
    ],
    "Security & Governance": [
        {"type": "dir", "path": "infra/stacks/security/"},
        {"type": "file", "path": "docs-site/docs/security/aws-secrets-management.md"},
        {"type": "file", "path": "infra/stacks/compliance_stack.py"},
        {"type": "file", "path": "infra/stacks/iam/"},
    ],
    "Documentation & Enablement": [
        {"type": "dir", "path": "docs-site/docs/"},
        {"type": "file", "path": "docs-site/README.md"},
        {"type": "file", "path": "docs-site/docs/github/checklist.md"},
        {"type": "file", "path": "docs-site/docs/github/aws_stack_architecture.md"},
        {"type": "file", "path": "docs-site/docs/data_prep/data_inputs_overview.md"},
        {"type": "file", "path": "docs-site/docs/site/checklist.mdx"},
        {"type": "file", "path": "docs-site/docusaurus.config.ts"},
        {"type": "file", "path": "docs-site/sidebars.ts"},
        {"type": "file", "path": "docs-site/package.json"},
        {"type": "file", "path": "docs-site/package-lock.json"},
    ],
}


# --- Signal Check Functions ---
def check_signal(signal):
    path = Path(signal["path"])
    # Directory check: must exist and contain at least one non-empty file
    if signal["type"] == "dir":
        if not path.is_dir():
            return False
        files = [f for f in path.iterdir() if f.is_file() and f.stat().st_size > 0]
        return len(files) > 0

    # File check: content-aware for all major sections
    elif signal["type"] == "file":
        if not path.is_file():
            return False
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            return False

        # --- AI Core ---
        if signal["path"] == "src/shieldcraft_ai/main.py":
            ml_libs = [
                "transformers",
                "torch",
                "sklearn",
                "tensorflow",
                "keras",
                "xgboost",
                "lightgbm",
            ]
            has_ml_import = any(
                f"import {lib}" in content or f"from {lib}" in content
                for lib in ml_libs
            )
            has_model_code = re.search(
                r"class [A-Za-z0-9_]+|def (train|fit|predict|inference|transform)",
                content,
            )
            lines = [
                l
                for l in content.splitlines()
                if l.strip()
                and not l.strip().startswith("#")
                and not l.strip().startswith("import")
                and not l.strip().startswith("from")
            ]
            substantive_lines = [
                l for l in lines if l.strip() not in ("pass", "TODO", "...")
            ]
            enough_code = len(substantive_lines) > 10
            return has_ml_import and has_model_code and enough_code

        # --- Data Preparation ---
        if signal["path"].startswith("data_prep/") and signal["path"].endswith((".py")):
            # Require at least one class/function and >10 lines of substantive code
            has_class_or_func = re.search(
                r"class [A-Za-z0-9_]+|def [A-Za-z0-9_]+", content
            )
            has_data_lib = any(
                lib in content for lib in ["pandas", "pyarrow", "dask", "fastparquet"]
            )
            lines = [
                l
                for l in content.splitlines()
                if l.strip()
                and not l.strip().startswith("#")
                and not l.strip().startswith("import")
                and not l.strip().startswith("from")
            ]
            substantive_lines = [
                l for l in lines if l.strip() not in ("pass", "TODO", "...")
            ]
            return has_class_or_func and (has_data_lib or len(substantive_lines) > 10)

        # --- Application Layer & Integration ---
        if signal["path"].startswith("src/api/") or signal["path"] in [
            "src/main.py",
            "src/main_healthcheck.py",
        ]:
            # Require FastAPI/Flask import, at least one endpoint, and >10 lines of code
            has_api_import = any(
                lib in content for lib in ["fastapi", "flask", "starlette", "quart"]
            )
            has_endpoint = re.search(
                r"@app\.route|@app\.get|@app\.post|@app\.put|@app\.delete|@router\.get|@router\.post",
                content,
            )
            lines = [
                l
                for l in content.splitlines()
                if l.strip()
                and not l.strip().startswith("#")
                and not l.strip().startswith("import")
                and not l.strip().startswith("from")
            ]
            substantive_lines = [
                l for l in lines if l.strip() not in ("pass", "TODO", "...")
            ]
            return has_api_import and has_endpoint and len(substantive_lines) > 10

        # --- MLOps, Deployment & Monitoring ---
        if signal["path"] in [
            "noxfile.py",
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.override.yml",
        ]:
            # Require at least one session/command and >10 lines of non-comment code
            has_session = re.search(
                r"def [A-Za-z0-9_]+|session|FROM |RUN |CMD |ENTRYPOINT", content
            )
            lines = [
                l
                for l in content.splitlines()
                if l.strip() and not l.strip().startswith("#")
            ]
            substantive_lines = [
                l for l in lines if l.strip() not in ("pass", "TODO", "...")
            ]
            return has_session and len(substantive_lines) > 10

        # --- Security & Governance ---
        if signal["path"].startswith("infra/stacks/") and signal["path"].endswith(
            ".py"
        ):
            # Require at least one resource/policy and >10 lines of code
            has_resource = re.search(
                r"class [A-Za-z0-9_]+|def [A-Za-z0-9_]+|policy|resource", content
            )
            lines = [
                l
                for l in content.splitlines()
                if l.strip() and not l.strip().startswith("#")
            ]
            substantive_lines = [
                l for l in lines if l.strip() not in ("pass", "TODO", "...")
            ]
            return has_resource and len(substantive_lines) > 10

        # --- Documentation & Enablement ---
        if signal["path"].startswith("docs-site/docs/") and signal["path"].endswith(
            (".md", ".mdx")
        ):
            # Require at least one paragraph, code sample, or diagram reference
            has_paragraph = re.search(r"\n\n[A-Za-z]", content)
            has_code = re.search(r"```", content)
            has_diagram = re.search(r"!\[.*\]\(.*\)", content)
            return has_paragraph or has_code or has_diagram

        # For other files, just check existence
        return path.stat().st_size > 0

    # Test file check: require at least one test function/class with assertion
    elif signal["type"] == "test":
        if not path.is_file():
            return False
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            return False
        has_test = re.search(r"def test_[A-Za-z0-9_]+", content)
        has_assert = "assert" in content
        return has_test and has_assert
    return False


# --- Section Status Calculation ---
def section_status(signals):
    results = [check_signal(s) for s in signals]
    # For AI Core, require substantive code in main.py
    if signals and signals[0].get("path", "").startswith("src/shieldcraft_ai/"):
        main_py_signal = next(
            (s for s in signals if s.get("path") == "src/shieldcraft_ai/main.py"), None
        )
        if main_py_signal:
            if not check_signal(main_py_signal):
                # If main.py is missing or only stub, downgrade to started
                return "🟨" if any(results) else "🟥"
    if all(results):
        return "🟩"
    elif any(results):
        return "🟨"
    else:
        return "🟥"


# --- Progress Review ---
def review_progress(section_signals):
    summary = {}
    for section, signals in section_signals.items():
        status = section_status(signals)
        summary[section] = status
    return summary


# --- Checklist Update ---
def update_checklist_progress(checklist_path, progress):
    with open(checklist_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Count green and red checkboxes in the checklist file
    green = len(re.findall(r"🟩", content))
    red = len(re.findall(r"🟥", content))
    total = green + red
    percent = int(round((green / total) * 100)) if total > 0 else 0
    PROGRESS_BAR_PATTERN = re.compile(
        r'(<progress[^>]+id="shieldcraft-progress"[^>]+value=")\d+("[^>]+max=")\d+("[^>]*>)',
        re.MULTILINE,
    )
    PROGRESS_LABEL_PATTERN = re.compile(
        r'(<div id="progress-label">)\d+% Complete(</div>)', re.MULTILINE
    )
    content_new = PROGRESS_BAR_PATTERN.sub(rf"\g<1>{percent}\g<2>100\g<3>", content)
    content_new = PROGRESS_LABEL_PATTERN.sub(
        rf"\g<1>{percent}% Complete\g<2>", content_new
    )
    # Do not insert or update section status summary at the top
    with open(checklist_path, "w", encoding="utf-8") as f:
        f.write(content_new)
    print(
        f"[checklist_lite_review] Progress bar and section summary updated in {checklist_path}: {percent}% complete."
    )


# --- Main Execution ---
if __name__ == "__main__":
    REPO_ROOT = Path(__file__).resolve().parent
    CHECKLIST_PATH = REPO_ROOT / "docs-site" / "docs" / "github" / "checklist.md"
    progress = review_progress(SECTION_SIGNALS)
    print("ShieldCraft Checklist Lite Review:")
    for section, status in progress.items():
        print(f"  {section}: {status}")
    update_checklist_progress(CHECKLIST_PATH, progress)
