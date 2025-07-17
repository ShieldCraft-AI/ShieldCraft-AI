import React, { useState, useEffect } from 'react';
import styles from './IconCarousel.module.css';

// This list would be dynamically generated in a real-world scenario
// For now, we'll use a static list based on the known icons.
const icons = [
    "Arch_Amazon-Aurora_48.svg",
    "Arch_Amazon-CloudWatch_48.svg",
    "Arch_Amazon-Detective_48.svg",
    "Arch_Amazon-EventBridge_48.svg",
    "Arch_Amazon-GuardDuty_48.svg",
    "Arch_Amazon-Managed-Streaming-for-Apache-Kafka_48.svg",
    "Arch_Amazon-OpenSearch-Service_48.svg",
    "Arch_Amazon-RDS_48.svg",
    "Arch_Amazon-S3-on-Outposts_48.svg",
    "Arch_Amazon-SageMaker_48.svg",
    "Amazon-VPC.svg",
    "Arch_AWS-CloudTrail_48.svg",
    "Arch_AWS-Config_48.svg",
    "Arch_AWS-Cost-Explorer_48.svg",
    "Arch_AWS-Glue-DataBrew_48.svg",
    "Arch_AWS-IAM-Identity-Center_48.svg",
    "Arch_AWS-Lake-Formation_48.svg",
    "Arch_AWS-Lambda_48.svg",
    "Arch_AWS-Secrets-Manager_48.svg",
    "Arch_AWS-Security-Hub_48.svg",
    "Arch_AWS-Step-Functions_48.svg",
    "Arch_AWS-WAF_48.svg"
];

const getServiceName = (filename) => {
    let name = filename.replace(/Arch_|_48\.svg|\.svg/g, '').replace(/_/g, ' ');
    // Remove all occurrences of 'Amazon' and 'AWS' globally, case-insensitive
    name = name.replace(/Amazon /gi, '').replace(/AWS /gi, '');
    // Also remove any remaining 'Amazon-' or 'AWS-' (with dash)
    name = name.replace(/Amazon-/gi, '').replace(/AWS-/gi, '');
    // Remove any leading/trailing whitespace
    name = name.trim();
    if (name.includes('Managed-Streaming-for-Apache-Kafka')) {
        return 'MSK';
    }
    if (name.includes('S3-on-Outposts')) {
        return 'S3';
    }
    if (name.includes('IAM-Identity-Center')) {
        return 'IAM';
    }
    if (name.toLowerCase().includes('opensearch')) {
        return 'OpenSearch';
    }
    return name;
};

const getServiceUrl = (filename) => {
    const service = getServiceName(filename).toLowerCase().replace(/\s+/g, '-');
    const serviceMap = {
        'managed-streaming-for-apache-kafka': 'msk',
        's3-on-outposts': 's3',
        'iam-identity-center': 'iam',
        'glue-databrew': 'glue',
        'cost-explorer': 'aws-cost-management/aws-cost-explorer',
        'opensearch-service': 'opensearch-service'
    };
    const mappedService = serviceMap[service] || service;
    return `https://aws.amazon.com/${mappedService}/`;
};

export default function IconCarousel() {
    return (
        <section className={styles.carouselSection}>
            <div className={styles.scroller}>
                <div className={styles.scrollerInner}>
                    {icons.map((icon, index) => (
                        <div key={index} className={styles.card}>
                            <a
                                href={getServiceUrl(icon)}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{ display: 'flex', alignItems: 'center', width: '100%', height: '100%', textDecoration: 'none' }}
                            >
                                <img
                                    src={`/aws-icons/${icon}`}
                                    alt={getServiceName(icon)}
                                    className={styles.icon}
                                />
                                <span className={styles.serviceName}>
                                    {getServiceName(icon)}
                                </span>
                            </a>
                        </div>
                    ))}
                    {/* Duplicate icons for seamless infinite loop */}
                    {icons.map((icon, index) => (
                        <div key={`dup-${index}`} className={styles.card} aria-hidden="true">
                            <a
                                href={getServiceUrl(icon)}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{ display: 'flex', alignItems: 'center', width: '100%', height: '100%', textDecoration: 'none' }}
                            >
                                <img
                                    src={`/aws-icons/${icon}`}
                                    alt={getServiceName(icon)}
                                    className={styles.icon}
                                />
                                <span className={styles.serviceName}>
                                    {getServiceName(icon)}
                                </span>
                            </a>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
