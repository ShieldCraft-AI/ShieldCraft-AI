import abc
from typing import Dict, Any, Optional

class ConfigBackend(abc.ABC):
    """Abstract base class for config backends."""
    @abc.abstractmethod
    def load(self, env: str) -> Dict[str, Any]:
        pass

class LocalYamlBackend(ConfigBackend):
    def __init__(self, config_dir: str):
        self.config_dir = config_dir

    def load(self, env: str) -> Dict[str, Any]:
        import os
        import yaml
        path = os.path.join(self.config_dir, f"{env}.yml")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r") as f:
            return yaml.safe_load(f)

class S3Backend(ConfigBackend):
    def __init__(self, bucket: str, prefix: str = ""):
        self.bucket = bucket
        self.prefix = prefix

    def load(self, env: str) -> Dict[str, Any]:
        import boto3
        import yaml
        s3 = boto3.client("s3")
        key = f"{self.prefix}{env}.yml" if self.prefix else f"{env}.yml"
        obj = s3.get_object(Bucket=self.bucket, Key=key)
        return yaml.safe_load(obj["Body"].read())

class SSMBackend(ConfigBackend):
    def __init__(self, param_prefix: str):
        self.param_prefix = param_prefix

    def load(self, env: str) -> Dict[str, Any]:
        import boto3
        import yaml
        ssm = boto3.client("ssm")
        param_name = f"{self.param_prefix}/{env}"
        resp = ssm.get_parameter(Name=param_name, WithDecryption=True)
        return yaml.safe_load(resp["Parameter"]["Value"])
