from aws_cdk import Tags


def apply_standard_tags(
    scope, project: str, environment: str, owner: str, extra_tags: dict = None
):
    """
    Apply standard tags to all resources in the given CDK scope.
    Args:
        scope: CDK construct (App, Stack, or resource)
        project: Project name (e.g., 'shieldcraft-ai')
        environment: Environment name (e.g., 'dev', 'staging', 'prod')
        owner: Owner/team/email
        extra_tags: Optional dict of additional tags
    """
    Tags.of(scope).add("Project", project)
    Tags.of(scope).add("Environment", environment)
    Tags.of(scope).add("Owner", owner)
    if extra_tags:
        for k, v in extra_tags.items():
            Tags.of(scope).add(str(k), str(v))
