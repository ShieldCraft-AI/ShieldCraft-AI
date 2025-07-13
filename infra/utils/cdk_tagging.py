from aws_cdk import Tags


def apply_standard_tags(
    scope,
    project: str,
    environment: str,
    owner: str,
    cost_center: str = None,
    team: str = None,
    compliance: str = None,
    extra_tags: dict = None,
):
    """
    Apply standard tags to all resources in the given CDK scope.
    Args:
        scope: CDK construct (App, Stack, or resource)
        project: Project name (e.g., 'shieldcraft-ai')
        environment: Environment name (e.g., 'dev', 'staging', 'prod')
        owner: Owner/team/email
        cost_center: Optional cost center tag
        team: Optional team tag
        compliance: Optional compliance tag
        extra_tags: Optional dict of additional tags
    """
    Tags.of(scope).add("Project", project)
    Tags.of(scope).add("Environment", environment)
    Tags.of(scope).add("Owner", owner)
    if cost_center:
        Tags.of(scope).add("CostCenter", cost_center)
    if team:
        Tags.of(scope).add("Team", team)
    if compliance:
        Tags.of(scope).add("Compliance", compliance)
    if extra_tags:
        for k, v in extra_tags.items():
            if v:
                Tags.of(scope).add(str(k), str(v))
