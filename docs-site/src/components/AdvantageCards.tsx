import React from 'react';
import Link from '@docusaurus/Link';
import styles from './AdvantageCards.module.css';
import { useReveal } from './hooks/useReveal';

type Card = {
    id: 'remediation' | 'emulation' | 'intel';
    title: string;
    link: string;
    benefit: string;
    description: string;
    bullets: string[];
};

const cards: Card[] = [
    {
        id: 'remediation',
        title: '⚡️ Rapid, Auditable Remediation',
        link: '/automated-alert-triage',
        benefit: 'Accelerate Recovery',
        description: 'Identify root causes and implement governed, auditable, and reversible fixes within minutes, minimizing MTTR with signed audit hashes for every action.',
        bullets: [
            'Automated root-cause analysis',
            'Accelerated root-cause identification and remediation',
            'Governed rollout with signed audit hashes and rollback',
            'Compliance-ready audit trails for every autonomous action',
        ],
    },
    {
        id: 'emulation',
        title: '🧪 Continuous Model Validation',
        link: '/automated-attack-simulation',
        benefit: 'Stay Ahead of Adversaries',
        description: 'AI generates dynamic kill-chains tailored to your current posture and produces Model Assurance Evidence to feed MLOps and quality gates.',
        bullets: [
            'Tailored multi-stage attack scenarios for posture testing',
            'Model assurance evidence that drives retraining and QA gates',
            'Governed intelligence loop feeding continuous improvement',
        ],
    },
    {
        id: 'intel',
        title: '📊 FinOps & Risk Prioritization',
        link: '/threat-detection',
        benefit: 'Focus on Critical Threats',
        description: 'Prioritizes the critical few by integrating configuration drift, identity blast radius, and threat signals into a cost-aware action queue.',
        bullets: [
            'Exploitability-first prioritization with identity blast-radius',
            'Cost-aware action queue with owner and dollar-impact',
            'Noise reduction and operational focus for remediation teams',
        ],
    },
];

type Props = {
    heading?: string;
    subcopy?: string;
};

export default function AdvantageCards({ heading, subcopy }: Props) {
    useReveal();
    return (
        <section className={`${styles.cardsSection} ${styles.center} sc-reveal`}>
            <h2 className={styles.heading}>{heading ?? 'ShieldCraft AI, your Strategic Security Advantage'}</h2>
            {subcopy && <p className={styles.subcopy}>{subcopy}</p>}
            <div className={styles.cardsRow}>
                {cards.map((card) => (
                    <Link
                        to={card.link}
                        key={card.id}
                        className={`${styles.card} sc-reveal`}
                        style={{ textDecoration: 'none', display: 'flex' }}
                        aria-label={card.title}
                    >
                        <h3>{card.title}</h3>
                        <p>
                            <b>{card.benefit}</b> {card.description}
                        </p>
                        <ul className={styles.cardList} aria-label={`${card.title} key outcomes`}>
                            {card.bullets.map((line) => (
                                <li key={`${card.id}-${line}`}>{line}</li>
                            ))}
                        </ul>
                    </Link>
                ))}
            </div>
        </section>
    );
}
