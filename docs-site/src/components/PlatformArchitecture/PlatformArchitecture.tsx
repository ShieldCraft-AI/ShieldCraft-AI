import React, { useState } from 'react';
import styles from './PlatformArchitecture.module.css';
import AwsServiceSelector from '../AwsServiceSelector/AwsServiceSelector';
import { FLAT_SERVICES } from '../services';

// Service tag data with icons and descriptions
const SERVICE_INFO: Record<string, { icon: string; tooltip: string }> = {
    'GuardDuty': { icon: '/aws-icons/Arch_Amazon-GuardDuty_48.svg', tooltip: 'Intelligent threat detection - identifies malicious activity' },
    'EventBridge': { icon: '/aws-icons/Arch_Amazon-EventBridge_48.svg', tooltip: 'Event bus - routes and normalizes security alerts' },
    'S3': { icon: '/aws-icons/Arch_Amazon-Simple-Storage-Service_48.svg', tooltip: 'Object storage - archives immutable forensic evidence' },
    'OpenSearch': { icon: '/aws-icons/Arch_Amazon-OpenSearch-Service_48.svg', tooltip: 'Search & analytics - surfaces historical context' },
    'SageMaker': { icon: '/aws-icons/Arch_Amazon-SageMaker_48.svg', tooltip: 'ML platform - runs LLM risk analysis' },
    'Lambda': { icon: '/aws-icons/Arch_AWS-Lambda_48.svg', tooltip: 'Serverless compute - lightweight orchestration' },
    'Step Functions': { icon: '/aws-icons/Arch_AWS-Step-Functions_48.svg', tooltip: 'Workflow orchestration - executes remediation playbooks' },
    'IAM': { icon: '/aws-icons/Arch_AWS-Identity-and-Access-Management_48.svg', tooltip: 'Identity & access - enforces least privilege' },
    'CloudTrail': { icon: '/aws-icons/Arch_AWS-CloudTrail_48.svg', tooltip: 'Audit logging - records every action taken' },
    'Config': { icon: '/aws-icons/Arch_AWS-Config_48.svg', tooltip: 'Compliance validation - ensures policy adherence' },
};

export default function PlatformArchitecture({ showOnlyFlow, showOnlySelector }: { showOnlyFlow?: boolean; showOnlySelector?: boolean } = {}) {
    const [selected, setSelected] = useState(FLAT_SERVICES[0]?.id);
    const [hoveredService, setHoveredService] = useState<string | null>(null);

    const selectedService = FLAT_SERVICES.find((s) => s.id === selected) ?? FLAT_SERVICES[0];

    const renderServiceTag = (serviceName: string) => {
        const info = SERVICE_INFO[serviceName];
        const isHovered = hoveredService === serviceName;

        return (
            <button
                key={serviceName}
                className={`${styles.serviceTag} ${isHovered ? styles.serviceTagActive : ''}`}
                onMouseEnter={() => setHoveredService(serviceName)}
                onMouseLeave={() => setHoveredService(null)}
                onClick={() => {
                    // Find and select the matching service in the carousel
                    const matchingService = FLAT_SERVICES.find(s =>
                        s.title.includes(serviceName) || serviceName.includes(s.title.split(' ').pop() || '')
                    );
                    if (matchingService) {
                        setSelected(matchingService.id);
                        // Smooth scroll to detail panel
                        document.querySelector(`.${styles.detailColumn}`)?.scrollIntoView({
                            behavior: 'smooth',
                            block: 'nearest'
                        });
                    }
                }}
                aria-label={`Learn more about ${serviceName}`}
            >
                {info && (
                    <img
                        src={info.icon}
                        alt=""
                        width={16}
                        height={16}
                        className={styles.serviceIcon}
                    />
                )}
                <span>{serviceName}</span>
                {info && isHovered && (
                    <span className={styles.serviceTooltip}>
                        {info.tooltip}
                    </span>
                )}
            </button>
        );
    };

    return (
        <div className={styles.platformRoot}>
            {!showOnlyFlow && <AwsServiceSelector selected={selected} onSelect={(id) => setSelected(id as typeof selected)} />}

            {!showOnlySelector && (
                <section className={styles.flowSection}>
                    <div className={styles.flowHeader}>
                        <span className={styles.badge}>⚡ How It Works</span>
                        <h3 className={styles.flowTitle}>
                            From Threat Detection to Autonomous Action
                        </h3>
                        <p className={styles.flowSubtitle}>
                            Watch how ShieldCraft orchestrates 26 AWS services to correlate threats, analyze intent, and execute remediation—all in seconds, fully autonomous.
                        </p>
                    </div>

                    <div className={styles.flowSteps}>
                        <div className={styles.flowStep}>
                            <div className={styles.stepNumber}>
                                <span>1</span>
                            </div>
                            <div className={styles.stepContent}>
                                <div className={styles.stepHeader}>
                                    <h4 className={styles.stepTitle}>🔍 ShieldCraft Ingests Everything</h4>
                                    <span className={styles.stepTiming}>~200ms</span>
                                </div>
                                <p className={styles.stepDesc}>
                                    ShieldCraft ingests telemetry from GuardDuty, Security Hub, CloudTrail, VPC Flow Logs, and your SaaS tools, normalizing disparate signals into a unified security graph. While GuardDuty finds isolated anomalies, ShieldCraft correlates across identity, network, and endpoint data to surface real attack patterns.
                                </p>
                                <div className={styles.stepServices}>
                                    {renderServiceTag('GuardDuty')}
                                    {renderServiceTag('EventBridge')}
                                    {renderServiceTag('S3')}
                                </div>
                            </div>
                        </div>

                        <div className={styles.flowArrow}>
                            <div className={styles.arrowLine}></div>
                            <div className={styles.arrowIcon}>▼</div>
                        </div>

                        <div className={styles.flowStep}>
                            <div className={styles.stepNumber}>
                                <span>2</span>
                            </div>
                            <div className={styles.stepContent}>
                                <div className={styles.stepHeader}>
                                    <h4 className={styles.stepTitle}>🤖 GenAI Analyzes Intent & Impact</h4>
                                    <span className={styles.stepTiming}>~1.2s</span>
                                </div>
                                <p className={styles.stepDesc}>
                                    ShieldCraft's LLM (powered by SageMaker) analyzes your historical context via OpenSearch-understanding normal vs. suspicious for YOUR environment. It maps attack chains, predicts blast radius, and recommends remediation playbooks. GuardDuty flags events; ShieldCraft tells you what they MEAN and what to DO.
                                </p>
                                <div className={styles.stepServices}>
                                    {renderServiceTag('OpenSearch')}
                                    {renderServiceTag('SageMaker')}
                                    {renderServiceTag('Lambda')}
                                </div>
                            </div>
                        </div>

                        <div className={styles.flowArrow}>
                            <div className={styles.arrowLine}></div>
                            <div className={styles.arrowIcon}>▼</div>
                        </div>

                        <div className={styles.flowStep}>
                            <div className={styles.stepNumber}>
                                <span>3</span>
                            </div>
                            <div className={styles.stepContent}>
                                <div className={styles.stepHeader}>
                                    <h4 className={styles.stepTitle}>⚙️ Autonomous Remediation (No Human Required)</h4>
                                    <span className={styles.stepTiming}>~3.8s</span>
                                </div>
                                <p className={styles.stepDesc}>
                                    ShieldCraft executes the playbook autonomously: isolates compromised instances, revokes stolen credentials, snapshots forensic evidence, and updates security groups-all within seconds. Every action is governed by policy guardrails, logged by CloudTrail, and fully reversible. GuardDuty alerts; ShieldCraft acts.
                                </p>
                                <div className={styles.stepServices}>
                                    {renderServiceTag('Step Functions')}
                                    {renderServiceTag('IAM')}
                                    {renderServiceTag('CloudTrail')}
                                    {renderServiceTag('Config')}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className={styles.keyInsight}>
                        <div className={styles.insightIcon}>
                            <img src={selectedService.icon} alt="" width={48} height={48} />
                        </div>
                        <div className={styles.insightContent}>
                            <h4 className={styles.insightTitle}>💡 Why {selectedService.title}?</h4>
                            <p className={styles.insightText}>
                                {selectedService.shieldcraftUse}
                            </p>
                        </div>
                    </div>
                </section>
            )}
        </div>
    );
}
