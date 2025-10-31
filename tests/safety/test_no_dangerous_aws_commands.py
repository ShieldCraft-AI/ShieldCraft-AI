import os
import pytest

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../scripts"))
FORBIDDEN_AWS_COMMANDS = [
    "aws ec2 terminate-instances",
    "aws rds delete-db-instance",
    "aws s3 rb",
    "aws iam delete-user",
    "aws kms schedule-key-deletion",
]


@pytest.mark.parametrize(
    "fname", [f for f in os.listdir(SCRIPTS_DIR) if f.endswith(".sh")]
)
def test_no_dangerous_aws_commands(fname):
    with open(os.path.join(SCRIPTS_DIR, fname)) as f:
        for i, line in enumerate(f, 1):
            if line.strip().startswith("#") or not line.strip():
                continue
            for cmd in FORBIDDEN_AWS_COMMANDS:
                assert (
                    cmd not in line
                ), f"Dangerous AWS command '{cmd}' found in {fname} (line {i})"
