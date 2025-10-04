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
        title: '⚡️ Rapid Autonomous Remediation',
        link: '/automated-alert-triage',
        benefit: 'Accelerate Recovery',
        description:
            'Identify root causes and implement reversible fixes within minutes. Guardrailed automation ensures secure, auditable, and reversible changes.',
        bullets: [
            'Automated root-cause analysis',
            'Secure infrastructure change execution',
            'Built-in rollback and audit trails',
        ],
    },
    {
        id: 'emulation',
        title: '🧪 Adaptive Attack Emulation',
        link: '/automated-attack-simulation',
        benefit: 'Stay Ahead of Adversaries',
        description:
            'AI generates dynamic kill-chains tailored to your security posture. Simulated breaches enhance configurations, refine detection, and preempt future vulnerabilities.',
        bullets: [
            'Dynamic multi-stage attack scenarios',
            'Gap analysis based on current posture',
            'Continuous improvement through feedback loops',
        ],
    },
    {
        id: 'intel',
        title: '📊 Actionable Threat Intelligence',
        link: '/threat-detection',
        benefit: 'Focus on Critical Threats',
        description:
            'Exploitability scoring integrates configuration drift, identity blast radius, and global threat signals. Reduces noise into a prioritized action queue, safeguarding engineering focus.',
        bullets: [
            'Exploitability over generic severity',
            'Noise reduction into actionable priorities',
            'Incorporates identity blast-radius analysis',
        ],
    },
];

export default function AdvantageCards() {
    useReveal();
    return (
        <section className={`${styles.cardsSection} ${styles.center} sc-reveal`}>
            <h2 className={styles.heading}>ShieldCraft AI, your Strategic Security Advantage</h2>
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
