import glob
import re

DISALLOWED_REGEX = re.compile(
    r"\b(cdk\s+deploy|aws\s+cloudformation\s+deploy|aws\s+proton\b|boto3\.client\(|boto3\.resource\()",
    re.IGNORECASE,
)


def test_repo_has_no_deploy_commands():
    paths = (
        glob.glob("**/*.sh", recursive=True)
        + glob.glob(".github/workflows/**/*.yml", recursive=True)
        + glob.glob("scripts/**/*.py", recursive=True)
    )
    whitelist = [
        # allow-list documented deploy helpers and validation workflows (repo-relative)
        "scripts/deploy-auth.sh",
        "scripts/deploy-auth-safe.sh",
        "scripts/aws_safety_checker.py",
        "scripts/deployment_safety_guard.py",
        "scripts/update_msk_arn.py",
        "scripts/pull_amplify_config.py",
        "scripts/setup_cognito_idp.py",
        "scripts/commit-script.sh",
        ".github/workflows/ci.yml",
        ".github/workflows/deployment-validation.yml",
    ]
    hits = []
    for p in set(paths):
        if any(w in p for w in whitelist):
            continue
        try:
            with open(p, "r", errors="ignore") as fh:
                content = fh.read()
        except Exception:
            # skip unreadable files
            continue
        if DISALLOWED_REGEX.search(content):
            hits.append(p)

    assert not hits, f"Found disallowed deploy-related calls in: {hits}"
