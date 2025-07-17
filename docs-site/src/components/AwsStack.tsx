import React, { useRef, useEffect } from 'react';
import styles from './AwsStack.module.css';

const awsStacks = [
    {
        name: 'SageMaker',
        icon: '/aws-icons/Arch_Amazon-SageMaker_48.svg',
        description: 'Predictive threat detection and generative attack emulation.',
        url: 'https://aws.amazon.com/sagemaker/',
        shieldcraftUsage: 'Powers our generative AI models for simulating sophisticated, multi-stage cyberattacks and predicting zero-day vulnerabilities.'
    },
    {
        name: 'MSK',
        icon: '/aws-icons/Arch_Amazon-Managed-Streaming-for-Apache-Kafka_48.svg',
        description: 'Real-time security data streaming.',
        url: 'https://aws.amazon.com/msk/',
        shieldcraftUsage: 'Acts as the central nervous system, ingesting and processing billions of security events in real-time from across the enterprise.'
    },
    {
        name: 'Lambda',
        icon: '/aws-icons/Arch_AWS-Lambda_48.svg',
        description: 'Event-driven, autonomous remediation.',
        url: 'https://aws.amazon.com/lambda/',
        shieldcraftUsage: 'Executes serverless functions for immediate, autonomous response actions, such as isolating compromised resources or patching vulnerabilities.'
    },
    {
        name: 'Glue',
        icon: '/aws-icons/Arch_AWS-Glue-DataBrew_48.svg',
        description: 'Governed, scalable data pipelines.',
        url: 'https://aws.amazon.com/glue/',
        shieldcraftUsage: 'Cleanses, transforms, and catalogs diverse security data, preparing it for analysis and model training in our secure data lake.'
    },
    {
        name: 'Lake Formation',
        icon: '/aws-icons/Arch_AWS-Lake-Formation_48.svg',
        description: 'Governed, scalable data pipelines.',
        url: 'https://aws.amazon.com/lake-formation/',
        shieldcraftUsage: 'Enforces fine-grained access control and governance over our centralized security data lake, ensuring data integrity and compliance.'
    },
    {
        name: 'OpenSearch',
        icon: '/aws-icons/Arch_Amazon-OpenSearch-Service_48.svg',
        description: 'Rapid, actionable analytics.',
        url: 'https://aws.amazon.com/opensearch-service/',
        shieldcraftUsage: 'Provides a high-speed query and visualization layer, enabling security analysts to hunt for threats and investigate incidents in seconds.'
    },
    {
        name: 'Secrets Manager',
        icon: '/aws-icons/Arch_AWS-Secrets-Manager_48.svg',
        description: 'Centralized, secure credential management.',
        url: 'https://aws.amazon.com/secrets-manager/',
        shieldcraftUsage: 'Securely stores and rotates all credentials, API keys, and secrets, eliminating hardcoded secrets and enforcing least privilege.'
    },
    {
        name: 'Step Functions',
        icon: '/aws-icons/Arch_AWS-Step-Functions_48.svg',
        description: 'Orchestrating complex workflows.',
        url: 'https://aws.amazon.com/step-functions/',
        shieldcraftUsage: 'Orchestrates complex, multi-step security workflows, from incident investigation and triage to automated remediation and reporting.'
    },
    {
        name: 'EventBridge',
        icon: '/aws-icons/Arch_Amazon-EventBridge_48.svg',
        description: 'Seamless, real-time integration.',
        url: 'https://aws.amazon.com/eventbridge/',
        shieldcraftUsage: 'Decouples our microservices, routing events between AWS services, custom applications, and SaaS integrations for a unified security posture.'
    },
    {
        name: 'Detective',
        icon: '/aws-icons/Arch_Amazon-Detective_48.svg',
        description: 'Deep, actionable threat investigations.',
        url: 'https://aws.amazon.com/detective/',
        shieldcraftUsage: 'Automatically analyzes and visualizes security data to help analysts conduct faster, more efficient incident investigations.'
    },
    {
        name: 'GuardDuty',
        icon: '/aws-icons/Arch_Amazon-GuardDuty_48.svg',
        description: 'Threat detection and monitoring.',
        url: 'https://aws.amazon.com/guardduty/',
        shieldcraftUsage: 'Provides intelligent threat detection across AWS accounts, workloads, and data, feeding high-fidelity alerts into our central event stream.'
    },
    {
        name: 'Security Hub',
        icon: '/aws-icons/Arch_AWS-Security-Hub_48.svg',
        description: 'Aggregated security findings.',
        url: 'https://aws.amazon.com/security-hub/',
        shieldcraftUsage: 'Aggregates and normalizes security findings from various AWS services and third-party tools into a single, prioritized view.'
    },
    {
        name: 'CloudWatch',
        icon: '/aws-icons/Arch_Amazon-CloudWatch_48.svg',
        description: 'Monitoring and observability.',
        url: 'https://aws.amazon.com/cloudwatch/',
        shieldcraftUsage: 'Delivers comprehensive observability, monitoring application performance, infrastructure health, and custom security metrics for proactive alerting.'
    },
    {
        name: 'Config',
        icon: '/aws-icons/Arch_AWS-Config_48.svg',
        description: 'Compliance and configuration management.',
        url: 'https://aws.amazon.com/config/',
        shieldcraftUsage: 'Continuously monitors and records AWS resource configurations, enabling automated compliance checks and drift detection.'
    },
    {
        name: 'CloudTrail',
        icon: '/aws-icons/Arch_AWS-CloudTrail_48.svg',
        description: 'Audit and governance.',
        url: 'https://aws.amazon.com/cloudtrail/',
        shieldcraftUsage: 'Logs all API activity across the AWS environment, providing a complete audit trail for governance, compliance, and forensic analysis.'
    },
    {
        name: 'Cost Explorer',
        icon: '/aws-icons/Arch_AWS-Cost-Explorer_48.svg',
        description: 'Cost management and optimization.',
        url: 'https://aws.amazon.com/aws-cost-management/aws-cost-explorer/',
        shieldcraftUsage: 'Monitors and optimizes the cost of our security operations, ensuring efficient use of resources without compromising protection.'
    },
    {
        name: 'IAM',
        icon: '/aws-icons/Arch_AWS-IAM-Identity-Center_48.svg',
        description: 'Centralized roles and least-privilege access.',
        url: 'https://aws.amazon.com/iam/',
        shieldcraftUsage: 'Manages all user identities and access permissions, enforcing least-privilege access and centralized policy control across the platform.'
    },
    {
        name: 'Aurora',
        icon: '/aws-icons/Arch_Amazon-Aurora_48.svg',
        description: 'High-performance, scalable database.',
        url: 'https://aws.amazon.com/rds/aurora/',
        shieldcraftUsage: 'Serves as our high-performance relational database for storing critical metadata, policies, and configuration information.'
    },
    {
        name: 'RDS',
        icon: '/aws-icons/Arch_Amazon-RDS_48.svg',
        description: 'Managed relational database service.',
        url: 'https://aws.amazon.com/rds/',
        shieldcraftUsage: 'Provides managed relational databases for specific application needs, ensuring operational excellence and security.'
    },
    {
        name: 'S3',
        icon: '/aws-icons/Arch_Amazon-S3-on-Outposts_48.svg',
        description: 'Scalable data lake and artifact storage.',
        url: 'https://aws.amazon.com/s3/',
        shieldcraftUsage: 'Forms the foundation of our secure data lake, providing durable, scalable, and cost-effective storage for raw and processed security data.'
    },
    {
        name: 'VPC',
        icon: '/aws-icons/Amazon-VPC.svg',
        description: 'Secure, isolated networking foundation.',
        url: 'https://aws.amazon.com/vpc/',
        shieldcraftUsage: 'Creates a secure, isolated network environment for all ShieldCraft AI resources, protecting them from external threats.'
    },
    {
        name: 'WAF',
        icon: '/aws-icons/Arch_AWS-WAF_48.svg',
        description: 'Web application firewall.',
        url: 'https://aws.amazon.com/waf/',
        shieldcraftUsage: 'Protects our web-facing applications and APIs from common web exploits and malicious bots at the edge.'
    }
];

export default function AwsStack() {
    const rowRef = useRef<HTMLDivElement>(null);
    const isHorizontallyScrolling = useRef(false);
    const scrollTimeout = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        const row = rowRef.current;
        if (row) {
            const handleWheel = (e: WheelEvent) => {
                // Clear any existing timeout to reset the timer on new scroll events
                if (scrollTimeout.current) {
                    clearTimeout(scrollTimeout.current);
                }

                const target = e.target as HTMLElement;
                const isOverCard = !!target.closest(`.${styles.carouselCardLink}`);

                // If the user scrolls over a card, engage horizontal scroll mode
                if (isOverCard) {
                    isHorizontallyScrolling.current = true;
                }

                // If in horizontal scroll mode, hijack the scroll
                if (isHorizontallyScrolling.current) {
                    if (e.deltaY === 0) return;
                    e.preventDefault();
                    row.scrollLeft += e.deltaY;
                }

                // After the user stops scrolling, the timeout will reset the mode
                scrollTimeout.current = setTimeout(() => {
                    isHorizontallyScrolling.current = false;
                }, 200); // 200ms delay before vertical scroll is re-enabled
            };

            row.addEventListener('wheel', handleWheel, { passive: false });

            return () => {
                row.removeEventListener('wheel', handleWheel);
                if (scrollTimeout.current) {
                    clearTimeout(scrollTimeout.current);
                }
            };
        }
    }, []);

    return (
        <section className={styles.carouselSection}>
            <h2 className={styles.carouselTitle}>AWS Stack</h2>
            <div className={styles.carouselRow} ref={rowRef}>
                {awsStacks.map(stack => (
                    <a href={stack.url} target="_blank" rel="noopener noreferrer" className={styles.carouselCardLink} key={stack.name}>
                        <div className={styles.carouselCard}>
                            <img src={stack.icon} alt={stack.name + ' icon'} className={styles.carouselIcon} />
                            <div className={styles.carouselName}>{stack.name}</div>
                            <div className={styles.carouselDesc}>{stack.description}</div>
                            <hr className={styles.cardDivider} />
                            <div className={styles.shieldcraftUsage}>{stack.shieldcraftUsage}</div>
                        </div>
                    </a>
                ))}
            </div>
        </section>
    );
}
