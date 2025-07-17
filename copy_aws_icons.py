import os
import shutil

# List of keywords for AWS services needed
service_keywords = [
    "VPC",
    "IAM",
    "S3",
    "Secrets-Manager",
    "Glue",
    "Lake-Formation",
    "Kafka",  # MSK
    "Lambda",
    "OpenSearch",
    "SageMaker",
    "RDS",
    "Aurora",
    "CloudWatch",
    "Config",
    "GuardDuty",
    "Security-Hub",
    "CloudTrail",
    "WAF",
    "SNS",
    "Step-Functions",
    "EventBridge",
    "Detective",
    "Cost-Explorer",
]

# Read all SVG paths from the file
with open("/home/dee/workspace/AI/shieldcraft-ai/all_aws_svgs.txt") as f:
    all_svg_paths = [line.strip() for line in f if line.strip().endswith(".svg")]

target_dir = "/home/dee/workspace/AI/shieldcraft-ai/docs-site/static/aws-icons"
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

found = {}
for keyword in service_keywords:
    for path in all_svg_paths:
        if keyword in os.path.basename(path):
            shutil.copy2(path, os.path.join(target_dir, os.path.basename(path)))
            found[keyword] = path
            print(f"Copied for {keyword}: {os.path.basename(path)}")
            break

missing = set(service_keywords) - set(found.keys())
if missing:
    print("Missing icons for keywords:", ", ".join(missing))
else:
    print("All required icons copied successfully.")
