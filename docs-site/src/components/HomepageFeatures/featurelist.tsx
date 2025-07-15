import type { FeatureCard } from './featureCard';

const FeatureList: FeatureCard[] = [
    {
        title: 'Proactive, Adaptive, Autonomous Security',
        Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
        description: (
            <>
                ShieldCraft AI empowers enterprises to counter modern threats like AI-augmented attacks and subtle insider risks with speed, precision, and efficiency.<br />
                <b>Next-Gen Cloud Cybersecurity</b>: Autonomous remediation, generative attack emulation, and predictive threat intelligence.
            </>
        ),
    },
    {
        title: 'Enterprise-Grade MLOps & AWS Foundation',
        Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
        description: (
            <>
                Built on a scalable, secure cloud-native architecture leveraging AWS services and MLOps best practices.<br />
                <b>Key Technologies</b>:&nbsp;
                <a href="https://aws.amazon.com/bedrock/" style={{ color: '#a5b4fc' }}>Amazon Bedrock</a>,&nbsp;
                <a href="https://aws.amazon.com/sagemaker/" style={{ color: '#a5b4fc' }}>SageMaker</a>,&nbsp;
                <a href="https://aws.amazon.com/opensearch-service/" style={{ color: '#a5b4fc' }}>OpenSearch</a>,&nbsp;
                <a href="https://aws.amazon.com/msk/" style={{ color: '#a5b4fc' }}>MSK</a>,&nbsp;
                <a href="https://aws.amazon.com/kinesis/" style={{ color: '#a5b4fc' }}>Kinesis</a>,&nbsp;
                <a href="https://airbyte.com/" style={{ color: '#a5b4fc' }}>Airbyte</a>,&nbsp;
                <a href="https://aws.amazon.com/s3/" style={{ color: '#a5b4fc' }}>S3</a>,&nbsp;
                <a href="https://aws.amazon.com/lake-formation/" style={{ color: '#a5b4fc' }}>Lake Formation</a>,&nbsp;
                <a href="https://aws.amazon.com/glue/" style={{ color: '#a5b4fc' }}>Glue</a>,&nbsp;
                <a href="https://aws.amazon.com/eks/" style={{ color: '#a5b4fc' }}>EKS</a>,&nbsp;
                <a href="https://aws.amazon.com/ecs/" style={{ color: '#a5b4fc' }}>ECS</a>,&nbsp;
                <a href="https://aws.amazon.com/lambda/" style={{ color: '#a5b4fc' }}>Lambda</a>,&nbsp;
                <a href="https://aws.amazon.com/step-functions/" style={{ color: '#a5b4fc' }}>Step Functions</a>,&nbsp;
                <a href="https://aws.amazon.com/cdk/" style={{ color: '#a5b4fc' }}>CDK</a>,&nbsp;
                <a href="https://www.terraform.io/" style={{ color: '#a5b4fc' }}>Terraform</a>,&nbsp;
                <a href="https://python-poetry.org/" style={{ color: '#a5b4fc' }}>Poetry</a>,&nbsp;
                <a href="https://aws.amazon.com/guardduty/" style={{ color: '#a5b4fc' }}>GuardDuty</a>,&nbsp;
                <a href="https://aws.amazon.com/security-hub/" style={{ color: '#a5b4fc' }}>Security Hub</a>,&nbsp;
                <a href="https://aws.amazon.com/config/" style={{ color: '#a5b4fc' }}>Config</a>,&nbsp;
                <a href="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html" style={{ color: '#a5b4fc' }}>CloudTrail</a>,&nbsp;
                <a href="https://aws.amazon.com/vpc/" style={{ color: '#a5b4fc' }}>VPC</a>,&nbsp;
                <a href="https://aws.amazon.com/waf/" style={{ color: '#a5b4fc' }}>WAF</a>,&nbsp;
                <a href="https://aws.amazon.com/cloudwatch/" style={{ color: '#a5b4fc' }}>CloudWatch</a>,&nbsp;
                <a href="https://aws.amazon.com/x-ray/" style={{ color: '#a5b4fc' }}>X-Ray</a>,&nbsp;
                <a href="https://prometheus.io/" style={{ color: '#a5b4fc' }}>Prometheus</a>,&nbsp;
                <a href="https://grafana.com/" style={{ color: '#a5b4fc' }}>Grafana</a>,&nbsp;
                <a href="https://sentry.io/welcome/" style={{ color: '#a5b4fc' }}>Sentry</a>,&nbsp;
                <a href="https://www.openpolicyagent.org/" style={{ color: '#a5b4fc' }}>OPA</a>,&nbsp;
                <a href="https://aws.amazon.com/aws-cost-management/aws-cost-explorer/" style={{ color: '#a5b4fc' }}>Cost Explorer</a>,&nbsp;
                <a href="https://docusaurus.io/" style={{ color: '#a5b4fc' }}>Docusaurus</a>,&nbsp;
                <a href="https://jupyter.org/" style={{ color: '#a5b4fc' }}>Jupyter</a>.
            </>
        ),
    },
    {
        title: 'Transformative Value & Innovations',
        Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
        description: (
            <>
                <ul style={{ textAlign: 'left' }}>
                    <li><b>Autonomous Remediation & Self-Healing:</b> Intelligent agents analyze risks and execute AWS-native fixes, reducing MTTR and breach impact.</li>
                    <li><b>Generative Attack Emulation:</b> Polymorphic attack scenarios tailored to your cloud, uncovering unknown unknowns and validating defenses.</li>
                    <li><b>Predictive Threat Intelligence:</b> Correlates AWS posture with global threat data to prioritize vulnerabilities and prevent breaches.</li>
                    <li><b>Operational Efficiency:</b> Automates repetitive tasks, boosts resilience, reduces risk and cost, and enables proactive insight.</li>
                </ul>
            </>
        ),
    },
];

export default FeatureList;
