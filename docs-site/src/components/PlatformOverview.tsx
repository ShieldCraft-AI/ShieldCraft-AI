import React from 'react';
import styles from './PlatformOverview.module.css';

const items = [
    { title: 'Data & Telemetry', desc: 'Ingest logs, flows, identities and SaaS signals across accounts and regions with governed pipelines.', icon: '/aws-icons/Arch_AWS-Glue-DataBrew_48.svg' },
    { title: 'Vector + Knowledge', desc: 'Curated knowledge base and embeddings that unify context across threats, assets, and policies for RAG.', icon: '/aws-icons/Arch_Amazon-OpenSearch-Service_48.svg' },
    { title: 'GenAI + Simulation', desc: 'Generative attack emulation, policy synthesis, and proactive detection tuned to your cloud.', icon: '/aws-icons/Arch_Amazon-SageMaker_48.svg' },
    { title: 'Remediation', desc: 'Guardrailed, event-driven actions via Lambda/Step Functions with full audit and rollbacks.', icon: '/aws-icons/Arch_AWS-Lambda_48.svg' },
];

export default function PlatformOverview() {
    return (
        <section className={styles.section}>
            <div className={styles.container}>
                <h2 className={styles.title}>The ShieldCraft Platform</h2>
                <p className={styles.subtitle}>Built on AWS. Designed for autonomy. Ready for enterprise.</p>
                <div className={styles.grid}>
                    {items.map(it => (
                        <div key={it.title} className={styles.card}>
                            <img src={it.icon} alt="" className={styles.icon} />
                            <h3 className={styles.cardTitle}>{it.title}</h3>
                            <p className={styles.cardDesc}>{it.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
