import type { ReactNode } from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
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
        <b>Key Technologies</b>: Amazon Bedrock, SageMaker, OpenSearch, MSK, Kinesis, Airbyte, S3, Lake Formation, Glue, EKS, ECS, Lambda, Step Functions, CDK, Terraform, Poetry, pre-commit, GuardDuty, Security Hub, Config, CloudTrail, VPC, WAF, CloudWatch, X-Ray, Prometheus, Grafana, Sentry, OPA, Cost Explorer, Docusaurus, Jupyter.
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

function Feature({ title, Svg, description }: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
