import React, { useEffect } from 'react';
import styles from './OutcomePillars.module.css';
import { useReveal } from './hooks/useReveal';

const pillars = [
    {
        k: 'autonomy',
        title: 'Autonomous Remediation',
        tagline: 'MTTR Compression',
        body: 'LLM + rules-driven playbooks propose and execute reversible actions with policy guardrails & auditability.',
        link: '/automated-alert-triage'
    },
    {
        k: 'simulation',
        title: 'Generative Attack Simulation',
        tagline: 'Proactive Hardening',
        body: 'Synthetic multi‑stage adversary paths surface latent control gaps before exploitation.',
        link: '/automated-attack-simulation'
    },
    {
        k: 'retrieval',
        title: 'Precision Retrieval & Context',
        tagline: 'Signal Density',
        body: 'Retrieval boundary + embeddings fuse findings, identities, assets & risk posture for high-fidelity prompts.',
        link: '/aws_stack_architecture#data-preparation--retrieval'
    },
    {
        k: 'governance',
        title: 'Governed Multi‑Account Data',
        tagline: 'Integrity & Traceability',
        body: 'Data contracts, tagging, encryption & lineage enable safe autonomy and model evaluation reproducibility.',
        link: '/aws_stack_architecture#governance--observability'
    }
];

export default function OutcomePillars() {
    useReveal();
    return (
        <section className={`${styles.pillarsSection}`} aria-labelledby="pillars-title">
            <h2 id="pillars-title" className={`${styles.pillarsTitle} sc-reveal`}>Strategic Outcome Pillars</h2>
            <p className={`${styles.pillarsSubtitle} sc-reveal`}>Core capability lanes that compound to deliver predictive + self-healing security posture.</p>
            <div className={styles.pillarsGrid}>
                {pillars.map(p => (
                    <a
                        href={p.link}
                        key={p.k}
                        className={`${styles.pillarCard} sc-reveal`}
                        aria-label={p.title}
                    >
                        <div className={styles.tagline}>{p.tagline}</div>
                        <h3>{p.title}</h3>
                        <div className={styles.pillarBody}>{p.body}</div>
                    </a>
                ))}
            </div>
        </section>
    );
}
