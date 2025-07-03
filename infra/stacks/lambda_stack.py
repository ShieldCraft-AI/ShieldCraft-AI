
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_ec2 as ec2,
)
from constructs import Construct

class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.IVpc, config: dict, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        lambda_cfgs = config.get('lambda_', {}).get('functions', [])
        env = config.get('app', {}).get('env', 'dev')

        # Tagging for traceability and custom tags
        self.tags.set_tag("Project", "ShieldCraftAI")
        self.tags.set_tag("Environment", env)
        for k, v in config.get('lambda_', {}).get('tags', {}).items():
            self.tags.set_tag(k, v)

        from aws_cdk import RemovalPolicy, CfnOutput

        if not isinstance(lambda_cfgs, list):
            raise ValueError("Lambda functions config must be a list.")
        fn_names = set()
        self.functions = []
        for fn_cfg in lambda_cfgs:
            name = fn_cfg.get('name')
            runtime = fn_cfg.get('runtime', 'PYTHON_3_11')
            handler = fn_cfg.get('handler', 'index.handler')
            code_path = fn_cfg.get('code_path', f'lambda/{name}')
            environment = fn_cfg.get('environment', {})
            timeout = fn_cfg.get('timeout', 60)
            use_vpc = fn_cfg.get('vpc', True)
            if not name or not runtime or not handler or not code_path:
                raise ValueError(f"Lambda function config must include name, runtime, handler, and code_path. Got: {fn_cfg}")
            if name in fn_names:
                raise ValueError(f"Duplicate Lambda function name: {name}")
            fn_names.add(name)
            # Validate runtime
            if not hasattr(_lambda.Runtime, runtime):
                raise ValueError(f"Invalid Lambda runtime: {runtime}")
            # Validate environment variables
            if not isinstance(environment, dict):
                raise ValueError(f"Lambda environment must be a dict for function {name}")
            # Validate timeout
            if not isinstance(timeout, int):
                raise ValueError(f"Lambda timeout must be an int (seconds) for function {name}")
            # Create function
            from aws_cdk import Duration
            fn = _lambda.Function(
                self, name,
                runtime=getattr(_lambda.Runtime, runtime),
                handler=handler,
                code=_lambda.Code.from_asset(code_path),
                environment=environment,
                timeout=Duration.seconds(timeout),
                vpc=vpc if use_vpc else None
            )
            fn.apply_removal_policy(RemovalPolicy.DESTROY if env == 'dev' else RemovalPolicy.RETAIN)
            CfnOutput(self, f"{construct_id}Lambda{name}Name", value=fn.function_name, export_name=f"{construct_id}-lambda-{name}-name")
            CfnOutput(self, f"{construct_id}Lambda{name}Arn", value=fn.function_arn, export_name=f"{construct_id}-lambda-{name}-arn")
            self.functions.append(fn)
