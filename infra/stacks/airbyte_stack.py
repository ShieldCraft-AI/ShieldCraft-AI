from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_secretsmanager as secretsmanager,
    aws_ecs as ecs
)
from constructs import Construct

class AirbyteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.IVpc, config: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # --- Config Validation ---
        airbyte_cfg = config.get('airbyte', {})
        env = config.get('app', {}).get('env', 'dev')

        # Provide sensible defaults, but validate if present
        instance_type = airbyte_cfg.get('instance_type', 't3.medium')
        desired_count = airbyte_cfg.get('desired_count', 1)
        cpu = airbyte_cfg.get('cpu', 1024)
        memory = airbyte_cfg.get('memory', 2048)
        if not isinstance(desired_count, int) or desired_count < 1:
            raise ValueError("Airbyte desired_count must be a positive integer")
        if cpu and (not isinstance(cpu, int) or cpu < 256):
            raise ValueError("Airbyte cpu must be an integer >= 256")
        if memory and (not isinstance(memory, int) or memory < 512):
            raise ValueError("Airbyte memory must be an integer >= 512")

        # Add a default tag for traceability and cost allocation
        self.tags.set_tag("Project", "ShieldCraftAI")

        secret_arn = airbyte_cfg.get('db_secret_arn')
        db_secret = None
        if secret_arn:
            db_secret = secretsmanager.Secret.from_secret_complete_arn(self, f"{construct_id}AirbyteDbSecret", secret_arn)

        airbyte_sg = ec2.SecurityGroup(
            self, f"{construct_id}AirbyteSecurityGroup",
            vpc=vpc,
            description="Security group for Airbyte",
            allow_all_outbound=True
        )

        self.cluster = ecs.Cluster(
            self, f"{construct_id}AirbyteCluster",
            vpc=vpc
        )

        # --- ECS Task Definition & Service ---
        airbyte_image = airbyte_cfg.get('image', 'airbyte/airbyte:0.50.2')
        container_port = airbyte_cfg.get('container_port', 8000)

        from aws_cdk import aws_iam as iam
        task_role = iam.Role(
            self, f"{construct_id}AirbyteTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        task_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy"))
        if secret_arn:
            task_role.add_to_policy(iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"],
                resources=[secret_arn]
            ))
        s3_arns = airbyte_cfg.get('s3_arns', [])
        if s3_arns:
            task_role.add_to_policy(iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                resources=s3_arns
            ))

        from aws_cdk import aws_logs as logs
        from aws_cdk import RemovalPolicy
        log_group_name = airbyte_cfg.get('log_group', f"/aws/ecs/airbyte-{env}")
        log_group = logs.LogGroup(
            self, f"{construct_id}AirbyteLogGroup",
            log_group_name=log_group_name,
            removal_policy=RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN
        )

        task_def = ecs.FargateTaskDefinition(
            self, f"{construct_id}AirbyteTaskDef",
            cpu=cpu,
            memory_limit_mib=memory,
            task_role=task_role
        )

        env_vars = airbyte_cfg.get('environment', {})
        container_secrets = {}
        if secret_arn:
            # Inject the actual secret value as AIRBYTE_DB_SECRET
            container_secrets['AIRBYTE_DB_SECRET'] = ecs.Secret.from_secrets_manager(db_secret)

        container = task_def.add_container(
            f"{construct_id}AirbyteContainer",
            image=ecs.ContainerImage.from_registry(airbyte_image),
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="airbyte",
                log_group=log_group
            ),
            environment=env_vars,
            secrets=container_secrets if container_secrets else None
        )
        container.add_port_mappings(ecs.PortMapping(container_port=container_port))

        subnet_type_str = airbyte_cfg.get('subnet_type', 'PRIVATE_WITH_EGRESS').upper()
        subnet_type = getattr(ec2.SubnetType, subnet_type_str, ec2.SubnetType.PRIVATE_WITH_EGRESS)

        self.service = ecs.FargateService(
            self, f"{construct_id}AirbyteService",
            cluster=self.cluster,
            task_definition=task_def,
            desired_count=desired_count,
            security_groups=[airbyte_sg],
            vpc_subnets=ec2.SubnetSelection(subnet_type=subnet_type)
        )

        from aws_cdk import aws_elasticloadbalancingv2 as elbv2
        alb = elbv2.ApplicationLoadBalancer(
            self, f"{construct_id}AirbyteALB",
            vpc=vpc,
            internet_facing=True if subnet_type == ec2.SubnetType.PUBLIC else False,
            security_group=airbyte_sg
        )
        listener = alb.add_listener(
            f"{construct_id}AirbyteListener",
            port=80,
            open=True
        )
        health_path = airbyte_cfg.get('health_check_path', '/api/v1/health')
        healthy_codes = airbyte_cfg.get('health_check_codes', '200')
        listener.add_targets(
            f"{construct_id}AirbyteTarget",
            port=container_port,
            targets=[self.service],
            health_check=elbv2.HealthCheck(
                path=health_path,
                healthy_http_codes=healthy_codes
            )
        )

        # Restrict security group ingress to ALB or open to 0.0.0.0/0 for demo, but recommend locking down in prod
        allowed_cidr = airbyte_cfg.get('allowed_cidr', '0.0.0.0/0')
        airbyte_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(allowed_cidr),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP from ALB or allowed CIDR"
        )

        self.alb = alb

        # --- Outputs: ALB DNS, ECS Service Name, Log Group Name ---
        from aws_cdk import CfnOutput
        CfnOutput(self, f"{construct_id}AirbyteALBDns", value=alb.load_balancer_dns_name, export_name=f"{construct_id}-alb-dns")
        CfnOutput(self, f"{construct_id}AirbyteServiceName", value=self.service.service_name, export_name=f"{construct_id}-service-name")
        CfnOutput(self, f"{construct_id}AirbyteLogGroupName", value=log_group.log_group_name, export_name=f"{construct_id}-log-group")
