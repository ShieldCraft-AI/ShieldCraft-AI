import os
from aws_cdk import (
    Stack,
    pipelines as pipelines,
    Environment,
)
from constructs import Construct
from infra.shieldcraft_app_stage import ShieldcraftAppStage


class ShieldcraftPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        repo_owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "Dee66")
        repo_name = os.environ.get("GITHUB_REPOSITORY_NAME", "shieldcraft-ai")
        branch = os.environ.get("GITHUB_BRANCH", "main")
        github_connection_arn = os.environ.get(
            "GITHUB_CONNECTION_ARN"
        )  # Set in AWS Secrets Manager or env

        source = pipelines.CodePipelineSource.connection(
            f"{repo_owner}/{repo_name}",
            branch,
            connection_arn=github_connection_arn,
        )

        synth_step = pipelines.CodeBuildStep(
            "Synth",
            input=source,
            install_commands=[
                "npm install -g aws-cdk",
                "pip install poetry",
                "poetry install --with dev --no-root",
            ],
            commands=["poetry run cdk synth"],
            primary_output_directory="infra/cdk.out",
        )

        pipeline = pipelines.CodePipeline(
            self,
            "ShieldcraftPipeline",
            synth=synth_step,
            cross_account_keys=True,
        )

        pipeline.add_stage(
            ShieldcraftAppStage(
                self,
                "Dev",
                env_name="dev",
                env=Environment(account="111111111111", region="af-south-1"),
            )
        )
        pipeline.add_stage(
            ShieldcraftAppStage(
                self,
                "Staging",
                env_name="staging",
                env=Environment(account="222222222222", region="af-south-1"),
            )
        )
        pipeline.add_stage(
            ShieldcraftAppStage(
                self,
                "Prod",
                env_name="prod",
                env=Environment(account="333333333333", region="af-south-1"),
            )
        )
