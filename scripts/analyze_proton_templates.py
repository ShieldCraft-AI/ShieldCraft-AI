#!/usr/bin/env python3
"""
ShieldCraft AI Proton Template Analyzer

Acts as an intelligent "Glue Crawler" for Proton templates and environment configurations.
Discovers service relationships, cost implications, and capability mappings across
dev/staging/prod environments for architecture visualization.

Sage Architecture Insights:
- Templates define WHAT can be deployed
- Configs define HOW they're deployed per environment
- This script bridges the gap to create visualization-ready metadata
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# CloudFormation YAML loader to handle intrinsic functions
class CloudFormationLoader(yaml.SafeLoader):
    """Custom YAML loader that handles CloudFormation intrinsic functions"""

    def __init__(self, stream):
        super().__init__(stream)
        # Add constructors for CloudFormation intrinsic functions
        self.add_constructor("!Ref", self._ref_constructor)
        self.add_constructor("!GetAtt", self._getatt_constructor)
        self.add_constructor("!Sub", self._sub_constructor)
        self.add_constructor("!Join", self._join_constructor)
        self.add_constructor("!Select", self._select_constructor)
        self.add_constructor("!Split", self._split_constructor)
        self.add_constructor("!If", self._if_constructor)
        self.add_constructor("!Not", self._not_constructor)
        self.add_constructor("!Equals", self._equals_constructor)
        self.add_constructor("!And", self._and_constructor)
        self.add_constructor("!Or", self._or_constructor)
        self.add_constructor("!Base64", self._base64_constructor)
        self.add_constructor("!GetAZs", self._getazs_constructor)
        self.add_constructor("!ImportValue", self._importvalue_constructor)
        self.add_constructor("!FindInMap", self._findinmap_constructor)

    def _ref_constructor(self, loader, node):
        return {"Ref": loader.construct_scalar(node)}

    def _getatt_constructor(self, loader, node):
        if isinstance(node, yaml.ScalarNode):
            return {"Fn::GetAtt": loader.construct_scalar(node)}
        return {"Fn::GetAtt": loader.construct_sequence(node)}

    def _sub_constructor(self, loader, node):
        if isinstance(node, yaml.ScalarNode):
            return {"Fn::Sub": loader.construct_scalar(node)}
        return {"Fn::Sub": loader.construct_sequence(node)}

    def _join_constructor(self, loader, node):
        return {"Fn::Join": loader.construct_sequence(node)}

    def _select_constructor(self, loader, node):
        return {"Fn::Select": loader.construct_sequence(node)}

    def _split_constructor(self, loader, node):
        return {"Fn::Split": loader.construct_sequence(node)}

    def _if_constructor(self, loader, node):
        return {"Fn::If": loader.construct_sequence(node)}

    def _not_constructor(self, loader, node):
        return {"Fn::Not": loader.construct_sequence(node)}

    def _equals_constructor(self, loader, node):
        return {"Fn::Equals": loader.construct_sequence(node)}

    def _and_constructor(self, loader, node):
        return {"Fn::And": loader.construct_sequence(node)}

    def _or_constructor(self, loader, node):
        return {"Fn::Or": loader.construct_sequence(node)}

    def _base64_constructor(self, loader, node):
        return {"Fn::Base64": loader.construct_scalar(node)}

    def _getazs_constructor(self, loader, node):
        return {"Fn::GetAZs": loader.construct_scalar(node)}

    def _importvalue_constructor(self, loader, node):
        return {"Fn::ImportValue": loader.construct_scalar(node)}

    def _findinmap_constructor(self, loader, node):
        return {"Fn::FindInMap": loader.construct_sequence(node)}


@dataclass
class ServiceInstance:
    """Represents a service deployment in a specific environment"""

    service_name: str
    template_file: str
    environment: str
    mode: str  # e.g., 'external', 'managed', 'local', 'none'
    enabled: bool
    instance_config: Dict[str, Any]
    estimated_monthly_cost_usd: float
    capability_category: str
    aws_resources: List[str]
    dependencies: List[str]
    security_features: List[str]


@dataclass
class CapabilityMapping:
    """Maps business capabilities to AWS services across environments"""

    capability_id: str
    capability_name: str
    description: str
    category: (
        str  # 'ingestion', 'processing', 'storage', 'ml', 'security', 'orchestration'
    )
    environments: Dict[str, ServiceInstance]
    service_progression: Dict[str, str]  # env -> rationale for service choice
    cost_progression: Dict[str, float]  # env -> estimated cost
    active_services_by_env: Dict[str, List[str]]  # env -> [services contributing]
    per_service_costs_by_env: Dict[str, Dict[str, float]]  # env -> {service: cost}
    proof_links: List[Dict[str, str]]  # links to configs, tests, docs


@dataclass
class ArchitectureDiscovery:
    """Complete architecture discovery results"""

    capabilities: Dict[str, CapabilityMapping]
    service_matrix: Dict[str, Dict[str, ServiceInstance]]  # service -> env -> instance
    cost_analysis: Dict[str, Dict[str, float]]  # env -> service -> cost
    dependency_graph: Dict[str, List[str]]  # service -> [dependencies]
    security_posture: Dict[str, List[str]]  # env -> [security_features]
    template_inventory: Dict[str, Dict[str, Any]]  # template_name -> metadata


class ProtonTemplateAnalyzer:
    """Intelligent analyzer for Proton templates and environment configurations"""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.proton_dir = workspace_root / "proton"
        self.config_dir = workspace_root / "config"
        self.environments = ["dev", "staging", "prod"]

        # AWS service cost estimates (monthly USD, conservative estimates)
        self.cost_estimates = {
            "lambda": {"dev": 5, "staging": 25, "prod": 100},
            "s3": {"dev": 10, "staging": 50, "prod": 200},
            "msk": {"dev": 0, "staging": 300, "prod": 600},  # dev uses external
            "opensearch": {"dev": 0, "staging": 150, "prod": 500},  # dev disabled
            "sagemaker": {"dev": 0, "staging": 200, "prod": 800},  # dev local
            "glue": {"dev": 5, "staging": 25, "prod": 100},
            "stepfunctions": {"dev": 2, "staging": 10, "prod": 50},
            "eventbridge": {"dev": 1, "staging": 5, "prod": 25},
            "airbyte": {"dev": 0, "staging": 100, "prod": 300},
            "lakeformation": {"dev": 0, "staging": 5, "prod": 25},
            "iam": {"dev": 0, "staging": 0, "prod": 0},
            "networking": {"dev": 50, "staging": 100, "prod": 200},
            "security": {"dev": 10, "staging": 25, "prod": 100},
            "secrets_manager": {"dev": 2, "staging": 5, "prod": 15},
            "budget": {"dev": 0, "staging": 1, "prod": 5},
            "compliance": {"dev": 0, "staging": 10, "prod": 50},
            "controltower": {"dev": 0, "staging": 0, "prod": 100},
            "cloud_native_hardening": {"dev": 5, "staging": 15, "prod": 50},
            "dataquality": {"dev": 0, "staging": 15, "prod": 75},
            "attack_simulation": {"dev": 0, "staging": 25, "prod": 100},
        }

        # Hourly pricing reference (approximate, USD) for af-south-1-like pricing.
        # These are conservative estimates and intentionally rounded for modeling.
        self.pricing = {
            "msk_broker_hourly": {  # Kafka broker instance hourly (managed MSK rough equivalent)
                "kafka.m5.large": 0.25,
                "kafka.m5.xlarge": 0.50,
            },
            "opensearch_hourly": {
                "t3.small.search": 0.040,
                "m6g.large.search": 0.165,
                "r6g.large.search": 0.250,
            },
            "sagemaker_inference_hourly": {
                "ml.t3.medium": 0.058,
                "ml.m5.large": 0.115,
                "ml.m5.xlarge": 0.230,
                "ml.m5.2xlarge": 0.460,
            },
            "sagemaker_training_hourly": {
                "ml.t3.medium": 0.068,
                "ml.m5.large": 0.140,
                "ml.m5.xlarge": 0.280,
                "ml.m5.2xlarge": 0.560,
            },
            "storage_gb_month": {
                "gp3": 0.08,
                "s3_standard": 0.023,
                "s3_ia": 0.0125,
                "s3_glacier": 0.004,
            },
        }

        # Capability category mappings
        self.capability_categories = {
            "ingestion": ["eventbridge", "msk", "airbyte"],
            "processing": ["lambda", "glue", "stepfunctions"],
            "storage": ["s3", "opensearch"],
            "ml": ["sagemaker", "dataquality"],
            "security": [
                "iam",
                "security",
                "secrets_manager",
                "cloud_native_hardening",
                "attack_simulation",
            ],
            "orchestration": ["stepfunctions", "eventbridge"],
            "governance": ["lakeformation", "budget", "compliance", "controltower"],
            "networking": ["networking"],
        }

    def discover_architecture(self) -> ArchitectureDiscovery:
        """Main discovery method - parallel analysis of all components"""
        logger.info("🔍 Starting ShieldCraft AI architecture discovery...")

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Parallel discovery tasks
            futures = {
                executor.submit(self._discover_templates): "templates",
                executor.submit(self._load_all_configs): "configs",
                executor.submit(self._analyze_dependencies): "dependencies",
                executor.submit(self._analyze_security_posture): "security",
            }

            results = {}
            for future in as_completed(futures):
                task_name = futures[future]
                try:
                    results[task_name] = future.result()
                    logger.info("✅ Completed %s discovery", task_name)
                except Exception as e:  # noqa: BLE001
                    logger.error("❌ Failed %s discovery: %s", task_name, e)
                    results[task_name] = {}

        # Synthesize discoveries into capability mappings
        templates = results.get("templates", {})
        configs = results.get("configs", {})
        dependencies = results.get("dependencies", {})
        security = results.get("security", {})

        # Build service matrix: service -> env -> ServiceInstance
        service_matrix = self._build_service_matrix(templates, configs)

        # Create capability mappings from service matrix
        capabilities = self._build_capability_mappings(service_matrix)

        # Generate cost analysis
        cost_analysis = self._analyze_costs(service_matrix)

        discovery = ArchitectureDiscovery(
            capabilities=capabilities,
            service_matrix=service_matrix,
            cost_analysis=cost_analysis,
            dependency_graph=dependencies,
            security_posture=security,
            template_inventory=templates,
        )

        logger.info(
            "🎯 Discovery complete: %d capabilities, %d services",
            len(capabilities),
            len(service_matrix),
        )
        return discovery

    def _discover_templates(self) -> Dict[str, Dict[str, Any]]:
        """Discover and parse all Proton templates"""
        templates = {}

        for template_file in self.proton_dir.glob("*.yaml"):
            try:
                with open(template_file, encoding="utf-8") as f:
                    template_content = yaml.load(f, Loader=CloudFormationLoader)

                service_name = template_file.stem.replace(
                    "-service-template", ""
                ).replace("-environment-template", "")

                # Extract key metadata from template
                metadata = {
                    "file_path": str(template_file),
                    "description": template_content.get("Description", ""),
                    "parameters": template_content.get("Parameters", {}),
                    "resources": template_content.get("Resources", {}),
                    "outputs": template_content.get("Outputs", {}),
                    "aws_resources": self._extract_aws_resources(template_content),
                    "environment_aware": self._is_environment_aware(template_content),
                    "security_features": self._extract_security_features(
                        template_content
                    ),
                    "estimated_complexity": self._estimate_complexity(template_content),
                }

                templates[service_name] = metadata
                logger.debug("📄 Analyzed template: %s", service_name)

            except Exception as e:
                logger.warning("⚠️ Failed to parse %s: %s", template_file, e)

        return templates

    def _load_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load and parse all environment configurations"""
        configs = {}

        for env in self.environments:
            config_file = self.config_dir / f"{env}.yml"
            if config_file.exists():
                try:
                    with open(config_file, encoding="utf-8") as f:
                        configs[env] = yaml.safe_load(f)
                    logger.debug("📋 Loaded config: %s", env)
                except Exception as e:
                    logger.warning("⚠️ Failed to load %s: %s", config_file, e)
                    configs[env] = {}

        return configs

    def _build_service_matrix(
        self, templates: Dict, configs: Dict
    ) -> Dict[str, Dict[str, ServiceInstance]]:
        """Build service deployment matrix across environments"""
        service_matrix = defaultdict(dict)

        for service_name, template_meta in templates.items():
            for env in self.environments:
                config = configs.get(env, {})

                # Determine if service is enabled and how it's configured
                service_config = self._extract_service_config(service_name, env, config)

                if service_config:
                    instance = ServiceInstance(
                        service_name=service_name,
                        template_file=template_meta["file_path"],
                        environment=env,
                        mode=service_config.get("mode", "managed"),
                        enabled=service_config.get("enabled", True),
                        instance_config=service_config,
                        estimated_monthly_cost_usd=self._estimate_service_cost(
                            service_name, env, service_config
                        ),
                        capability_category=self._get_capability_category(service_name),
                        aws_resources=template_meta["aws_resources"],
                        dependencies=self._extract_dependencies(
                            service_name, service_config
                        ),
                        security_features=template_meta["security_features"],
                    )
                    service_matrix[service_name][env] = instance

        return dict(service_matrix)

    def _extract_service_config(
        self, service_name: str, _env: str, config: Dict
    ) -> Optional[Dict]:
        """Extract service-specific configuration from environment config"""
        # Handle different config key patterns
        config_keys = [
            service_name,
            service_name.replace("-", "_"),
            service_name.replace("_", "-"),
            f"{service_name}_service",
            service_name.rstrip("s"),  # singular form
        ]

        for key in config_keys:
            if key in config:
                service_config = config[key]
                if isinstance(service_config, dict):
                    return {
                        "enabled": service_config.get("enabled", True),
                        "mode": service_config.get("mode", "managed"),
                        **service_config,
                    }

        # Check for embedded configs (e.g., lambda_.functions)
        if service_name == "lambda" and "lambda_" in config:
            return {
                "enabled": bool(config["lambda_"].get("functions")),
                "mode": "managed",
                "functions": config["lambda_"].get("functions", []),
            }

        # Default enabled for core services
        core_services = ["s3", "iam", "networking", "security"]
        if service_name in core_services:
            return {"enabled": True, "mode": "managed"}

        return None

    def _build_capability_mappings(
        self, service_matrix: Dict
    ) -> Dict[str, CapabilityMapping]:
        """Build capability mappings from service matrix"""
        capabilities = {}

        # Define capability groupings
        capability_definitions = {
            "ingestion": {
                "name": "Data Ingestion & Event Streaming",
                "description": "Ingest security telemetry from multiple sources with reliable, scalable patterns",
                "services": ["eventbridge", "msk", "airbyte"],
                "category": "data-plane",
            },
            "processing": {
                "name": "Stream Processing & Transformation",
                "description": "Real-time processing of security events with intelligent correlation",
                "services": ["lambda", "glue", "stepfunctions"],
                "category": "data-plane",
            },
            "storage": {
                "name": "Data Lake & Search Analytics",
                "description": "Governed data lake with fast search and analytics capabilities",
                "services": ["s3", "opensearch", "lakeformation"],
                "category": "data-plane",
            },
            "ml": {
                "name": "AI/ML Risk Scoring & Models",
                "description": "ML-powered threat detection and automated risk scoring",
                "services": ["sagemaker", "dataquality"],
                "category": "actions",
            },
            "orchestration": {
                "name": "Workflow Orchestration",
                "description": "Coordinated multi-step security workflows with error handling",
                "services": ["stepfunctions", "eventbridge"],
                "category": "actions",
            },
            "security": {
                "name": "Security & Identity Governance",
                "description": "Zero-trust security posture with comprehensive identity management",
                "services": [
                    "iam",
                    "security",
                    "secrets_manager",
                    "cloud_native_hardening",
                ],
                "category": "guardrails",
            },
            "governance": {
                "name": "Compliance & Cost Governance",
                "description": "Automated compliance checking with proactive cost management",
                "services": ["compliance", "budget", "controltower"],
                "category": "guardrails",
            },
            "observability": {
                "name": "Monitoring & Attack Simulation",
                "description": "Comprehensive observability with proactive threat simulation",
                "services": ["attack_simulation", "cloud_native_hardening"],
                "category": "observability",
            },
        }

        for cap_id, cap_def in capability_definitions.items():
            environments = {}
            service_progression = {}
            cost_progression = {}
            active_services_by_env = {}
            per_service_costs_by_env: Dict[str, Dict[str, float]] = {}

            # Find best service for each environment
            for env in self.environments:
                best_service = None
                best_rationale = ""
                total_cost = 0

                active_for_env = []
                env_costs: Dict[str, float] = {}
                for service_name in cap_def["services"]:
                    if (
                        service_name in service_matrix
                        and env in service_matrix[service_name]
                    ):
                        instance = service_matrix[service_name][env]
                        # Only consider services that are truly active (exclude none/local/external modes)
                        if instance.enabled and instance.mode not in {
                            "none",
                            "local",
                            "external",
                        }:
                            active_for_env.append(service_name)
                            env_costs[service_name] = float(
                                instance.estimated_monthly_cost_usd or 0.0
                            )
                            if not best_service:
                                best_service = instance
                                best_rationale = self._get_service_rationale(
                                    service_name, env, instance.mode
                                )
                            total_cost += instance.estimated_monthly_cost_usd

                if best_service:
                    environments[env] = best_service
                    service_progression[env] = best_rationale
                    cost_progression[env] = total_cost
                    active_services_by_env[env] = active_for_env
                    per_service_costs_by_env[env] = env_costs

            # Generate proof links
            proof_links = self._generate_proof_links(cap_id, cap_def["services"])

            capability = CapabilityMapping(
                capability_id=cap_id,
                capability_name=cap_def["name"],
                description=cap_def["description"],
                category=cap_def["category"],
                environments=environments,
                service_progression=service_progression,
                cost_progression=cost_progression,
                active_services_by_env=active_services_by_env,
                per_service_costs_by_env=per_service_costs_by_env,
                proof_links=proof_links,
            )

            capabilities[cap_id] = capability

        return capabilities

    def _analyze_costs(self, service_matrix: Dict) -> Dict[str, Dict[str, float]]:
        """Analyze costs across services and environments"""
        cost_analysis = defaultdict(dict)

        for service_name, environments in service_matrix.items():
            for env, instance in environments.items():
                if service_name not in cost_analysis:
                    cost_analysis[service_name] = {}
                cost_analysis[service_name][env] = instance.estimated_monthly_cost_usd

        return dict(cost_analysis)

    def _get_service_rationale(self, service: str, env: str, mode: str) -> str:
        """Generate rationale for service choice in environment"""
        rationales = {
            ("msk", "dev", "external"): "External Kafka for cost-free development",
            ("msk", "staging", "managed"): "Managed MSK for production-like testing",
            ("msk", "prod", "managed"): "Fully managed MSK with multi-AZ reliability",
            ("opensearch", "dev", "none"): "Disabled to minimize dev costs",
            (
                "opensearch",
                "staging",
                "managed",
            ): "Managed OpenSearch for search analytics",
            (
                "opensearch",
                "prod",
                "managed",
            ): "Production OpenSearch with enhanced instance types",
            ("sagemaker", "dev", "local"): "Local models for cost-free development",
            (
                "sagemaker",
                "staging",
                "managed",
            ): "Managed SageMaker for model validation",
            ("sagemaker", "prod", "managed"): "Production SageMaker with auto-scaling",
        }

        key = (service, env, mode)
        return rationales.get(key, f"{mode.title()} deployment for {env} environment")

    def _generate_proof_links(
        self, capability_id: str, services: List[str]
    ) -> List[Dict[str, str]]:
        """Generate proof links for capability claims"""
        links = []

        # Config proof links
        for env in self.environments:
            links.append(
                {
                    "label": f"{env.title()} Configuration",
                    "href": f"/config/{env}.yml",
                    "kind": "code",
                }
            )

        # Template proof links
        for service in services:
            template_file = f"/proton/{service}-service-template.yaml"
            if (self.workspace_root / template_file.lstrip("/")).exists():
                links.append(
                    {
                        "label": f"{service.title()} Template",
                        "href": template_file,
                        "kind": "code",
                    }
                )

        # Test proof links (if they exist)
        test_patterns = [
            f"/tests/test_{capability_id}.py",
            f"/tests/integration/test_{capability_id}_integration.py",
        ]

        for pattern in test_patterns:
            if (self.workspace_root / pattern.lstrip("/")).exists():
                links.append(
                    {
                        "label": f"{capability_id.title()} Tests",
                        "href": pattern,
                        "kind": "test",
                    }
                )

        return links

    def _extract_aws_resources(self, template: Dict) -> List[str]:
        """Extract AWS resource types from CloudFormation template"""
        resources = template.get("Resources", {})
        return [res.get("Type", "") for res in resources.values() if "Type" in res]

    def _extract_security_features(self, template: Dict) -> List[str]:
        """Extract security features from template"""
        features = []
        content_str = yaml.dump(template).lower()

        security_indicators = [
            ("encryption", "encryption"),
            ("iam", "iam_roles"),
            ("vpc", "vpc_networking"),
            ("ssl", "ssl_tls"),
            ("kms", "kms_encryption"),
            ("secret", "secrets_management"),
            ("policy", "iam_policies"),
            ("security", "security_groups"),
        ]

        for indicator, feature in security_indicators:
            if indicator in content_str:
                features.append(feature)

        return features

    def _is_environment_aware(self, template: Dict) -> bool:
        """Check if template supports environment-specific deployment"""
        params = template.get("Parameters", {})
        return "EnvironmentName" in params or "Environment" in params

    def _estimate_complexity(self, template: Dict) -> str:
        """Estimate template complexity based on resources and parameters"""
        resources = len(template.get("Resources", {}))
        parameters = len(template.get("Parameters", {}))

        if resources <= 3 and parameters <= 5:
            return "low"
        elif resources <= 8 and parameters <= 12:
            return "medium"
        else:
            return "high"

    def _get_capability_category(self, service_name: str) -> str:
        """Get capability category for service"""
        for category, services in self.capability_categories.items():
            if service_name in services:
                return category
        return "other"

    def _estimate_service_cost(
        self, service_name: str, env: str, config: Dict
    ) -> float:
        """Estimate monthly cost for service in environment"""
        mode = config.get("mode", "managed")
        # Free/disabled modes
        if mode in {"none", "local", "external"}:
            return 0.0

        # Specialized calculators per service where we have more detail
        try:
            if service_name == "msk":
                return self._estimate_msk_cost(env, config)
            if service_name == "opensearch":
                return self._estimate_opensearch_cost(env, config)
            if service_name == "sagemaker":
                return self._estimate_sagemaker_cost(env, config)
            if service_name == "s3":
                return self._estimate_s3_cost(env, config)
            if service_name == "airbyte":
                return self._estimate_airbyte_cost(env, config)
            if service_name == "glue":
                return self._estimate_glue_cost(env, config)
        except Exception:
            # Fall back to base estimates if any parsing fails
            pass

        # Default back to coarse estimates
        base_cost = self.cost_estimates.get(
            service_name, {"dev": 0, "staging": 10, "prod": 50}
        )
        multipliers = {"dev": 0.5, "staging": 1.0, "prod": 2.0}
        return base_cost.get(env, 0) * multipliers.get(env, 1.0)

    # ---- Cost calculators ----
    def _monthly_from_hourly(self, hourly: float, hours: int = 730) -> float:
        return round(hourly * hours, 2)

    def _estimate_msk_cost(self, env: str, config: Dict) -> float:
        cluster = (config or {}).get("cluster", {})
        itype = cluster.get("instance_type", "kafka.m5.large")
        nodes = int(cluster.get("number_of_broker_nodes", 3) or 3)
        hourly = self.pricing["msk_broker_hourly"].get(itype, 0.25)
        # Assume MSK includes broker infra; ignore storage/throughput for now
        base = self._monthly_from_hourly(hourly) * nodes
        # Environment multiplier to reflect prod hardening/overheads
        env_mult = {"dev": 0.0, "staging": 1.0, "prod": 1.8}
        return round(base * env_mult.get(env, 1.0), 2)

    def _estimate_opensearch_cost(self, env: str, config: Dict) -> float:
        if config.get("mode") == "none":
            return 0.0
        domain = (config or {}).get("domain", {})
        cluster_cfg = domain.get("cluster_config", {})
        itype = cluster_cfg.get("instanceType", "t3.small.search")
        count = int(cluster_cfg.get("instanceCount", 2) or 2)
        hourly = self.pricing["opensearch_hourly"].get(itype, 0.12)
        compute = self._monthly_from_hourly(hourly) * count
        # EBS storage cost per node
        ebs = domain.get("ebs_options", {})
        vol_size = int(ebs.get("volumeSize", 20) or 20)
        gp3_cost = self.pricing["storage_gb_month"]["gp3"] * vol_size * count
        base = compute + gp3_cost
        env_mult = {"dev": 0.0, "staging": 1.0, "prod": 1.7}
        return round(base * env_mult.get(env, 1.0), 2)

    def _estimate_sagemaker_cost(self, env: str, config: Dict) -> float:
        # Inference endpoint assumed always-on for managed; training is bursty hours
        inference_type = config.get("inference_instance_type", "ml.m5.large")
        training_type = config.get("training_instance_type", "ml.m5.large")
        autoscale = bool(config.get("endpoint_auto_scaling", False))
        multi_az = bool(config.get("multi_az_deployment", False))
        data_capture = bool(config.get("data_capture_enabled", False))

        inf_hourly = self.pricing["sagemaker_inference_hourly"].get(
            inference_type, 0.115
        )
        trn_hourly = self.pricing["sagemaker_training_hourly"].get(training_type, 0.14)

        # Hours assumption per env
        train_hours = {"dev": 0, "staging": 20, "prod": 60}.get(env, 0)
        # Always-on inference hours
        inf_instances = 1
        if autoscale and env == "prod":
            inf_instances = 2
        # Multi-AZ doubles endpoints for HA
        if multi_az and env == "prod":
            inf_instances *= 2

        inference_cost = self._monthly_from_hourly(inf_hourly) * (
            inf_instances if config.get("mode") == "managed" else 0
        )
        training_cost = round(trn_hourly * train_hours, 2)

        # Optional add-ons (data capture/model monitoring): coarse monthly adds
        addons = 0.0
        if data_capture and env == "prod":
            addons += 100.0

        return round(inference_cost + training_cost + addons, 2)

    def _estimate_s3_cost(self, env: str, config: Dict) -> float:
        buckets = (config or {}).get("buckets", [])
        count = len(buckets) if isinstance(buckets, list) else 1
        # Coarse baseline that assumes moderate storage and request volumes per bucket
        per_bucket = {"dev": 3.0, "staging": 12.0, "prod": 35.0}
        return round(per_bucket.get(env, 5.0) * max(1, count), 2)

    def _estimate_airbyte_cost(self, env: str, config: Dict) -> float:
        mode = config.get("mode", "ecs_managed")
        if mode == "ecs_scale_to_zero":
            return 0.0
        tasks = (
            int(config.get("min_task_count", 1)) + int(config.get("max_task_count", 1))
        ) / 2
        # Coarse monthly per-task baseline
        per_task = {"staging": 60.0, "prod": 90.0}
        return round(per_task.get(env, 30.0) * max(1, tasks), 2)

    def _estimate_glue_cost(self, env: str, config: Dict) -> float:
        base = self.cost_estimates.get(
            "glue", {"dev": 5, "staging": 25, "prod": 100}
        ).get(env, 0)
        dq_enabled = bool(config.get("enable_data_quality", False))
        if dq_enabled:
            base += {"dev": 0, "staging": 20, "prod": 80}.get(env, 0)
        # No environment multipliers; already embedded above
        return float(base)

    def _extract_dependencies(self, service_name: str, config: Dict) -> List[str]:
        """Extract service dependencies from configuration"""
        dependencies = []

        # Common dependency patterns
        if "vpc" in str(config).lower():
            dependencies.append("networking")
        if "secret" in str(config).lower():
            dependencies.append("secrets_manager")
        if "s3" in str(config).lower():
            dependencies.append("s3")
        if "iam" in str(config).lower() or "role" in str(config).lower():
            dependencies.append("iam")

        return dependencies

    def _analyze_dependencies(self) -> Dict[str, List[str]]:
        """Analyze service dependencies across templates"""
        # Simplified dependency analysis - can be enhanced
        return {
            "msk": ["networking", "iam"],
            "opensearch": ["networking", "iam"],
            "lambda": ["iam", "networking"],
            "sagemaker": ["iam", "s3"],
            "glue": ["iam", "s3"],
            "stepfunctions": ["iam", "lambda"],
        }

    def _analyze_security_posture(self) -> Dict[str, List[str]]:
        """Analyze security features by environment"""
        return {
            "dev": ["encryption_at_rest", "iam_roles", "vpc_isolation"],
            "staging": [
                "encryption_at_rest",
                "encryption_in_transit",
                "iam_roles",
                "vpc_isolation",
                "cloudwatch_monitoring",
            ],
            "prod": [
                "encryption_at_rest",
                "encryption_in_transit",
                "iam_roles",
                "vpc_isolation",
                "cloudwatch_monitoring",
                "config_rules",
                "guardduty",
            ],
        }

    def save_discovery(self, discovery: ArchitectureDiscovery, output_path: Path):
        """Save discovery results to JSON for consumption by UI components"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert dataclasses to dicts for JSON serialization
        serializable_discovery = {
            "capabilities": {k: asdict(v) for k, v in discovery.capabilities.items()},
            "service_matrix": {
                service: {env: asdict(instance) for env, instance in envs.items()}
                for service, envs in discovery.service_matrix.items()
            },
            "cost_analysis": discovery.cost_analysis,
            "dependency_graph": discovery.dependency_graph,
            "security_posture": discovery.security_posture,
            "template_inventory": discovery.template_inventory,
            "generation_metadata": {
                "timestamp": "2025-10-02T00:00:00Z",
                "version": "1.0.0",
                "total_capabilities": len(discovery.capabilities),
                "total_services": len(discovery.service_matrix),
                "environments": self.environments,
            },
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(serializable_discovery, f, indent=2, default=str)

        logger.info("💾 Saved discovery to %s", output_path)


def main():
    """Main execution function"""
    workspace_root = Path(__file__).parent.parent
    analyzer = ProtonTemplateAnalyzer(workspace_root)

    # Discover architecture
    discovery = analyzer.discover_architecture()

    # Save results for UI consumption
    output_dir = workspace_root / "docs-site" / "static" / "data"
    analyzer.save_discovery(discovery, output_dir / "architecture_discovery.json")

    # Print summary for immediate feedback
    print("\n🎯 ShieldCraft AI Architecture Discovery Summary")
    print("=" * 50)
    print(f"📋 Capabilities Discovered: {len(discovery.capabilities)}")
    print(f"🔧 Services Analyzed: {len(discovery.service_matrix)}")
    print("💰 Total Cost Analysis:")

    for env in ["dev", "staging", "prod"]:
        total_cost = sum(
            instance.estimated_monthly_cost_usd
            for service_envs in discovery.service_matrix.values()
            for env_name, instance in service_envs.items()
            if env_name == env
        )
        print(f"   {env.upper()}: ~${total_cost:.0f} / month")

    print("\n📁 Results saved to: docs-site/static/data/architecture_discovery.json")
    print("✅ Ready for interactive visualization!")


if __name__ == "__main__":
    main()
