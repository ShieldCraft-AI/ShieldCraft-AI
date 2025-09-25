import React from 'react';
import styles from './AdvantageCards.module.css';
import { useReveal } from './hooks/useReveal';

const cards = [
    {
        title: '⚡️  Autonomous Remediation',
        link: '/automated-alert-triage',
        benefit: 'Heal Faster',
        description: 'Root cause → reversible fix in minutes. Guardrailed automation drafts, validates and executes least‑privilege changes while preserving audit + rollback. Slash MTTR without surrendering control.'
    },
    {
        title: '🧪  Generative Attack Emulation',
        link: '/automated-attack-simulation',
        benefit: 'Anticipate Adversaries',
        description: 'AI composes evolving kill‑chains tailored to your current posture. Each simulated breach hardens configs, tunes detection and closes tomorrow’s gaps today.'
    },
    {
        title: '📊   Predictive Threat Intelligence',
        link: '/threat-detection',
        benefit: 'Prioritize What Matters',
        description: 'Exploitability scoring blends config drift, identity blast radius & global threat signals. Noise collapses into an ordered action queue that protects engineering focus.'
    }
];

export default function AdvantageCards() {
    useReveal();
    return (
        <section className={`${styles.cardsSection} sc-reveal`}>
            <h2 className={`${styles.center} sc-reveal`}>ShieldCraft AI, your Strategic Security Advantage</h2>
            <div className={styles.cardsRow}>
                {cards.map(card => (
                    <a
                        href={card.link}
                        key={card.title}
                        className={`${styles.card} sc-reveal`}
                        style={{ textDecoration: 'none', display: 'flex' }}
                    >
                        <h3>{card.title}</h3>
                        <p><b>{card.benefit}</b> {card.description}</p>
                        <ul className={styles.cardList} aria-label={`${card.title} key outcomes`}>
                            {card.title.includes('Remediation') && [
                                'Root-cause hypothesis generation',
                                'Guardrailed infra change execution',
                                'Rollback + audit trace baked in'
                            ].map(line => <li key={line}>{line}</li>)}
                            {card.title.includes('Attack Emulation') && [
                                'Adaptive multi-stage scenarios',
                                'Posture-driven gap surfacing',
                                'Feedback loop retrains scenarios'
                            ].map(line => <li key={line}>{line}</li>)}
                            {card.title.includes('Predictive Threat Intelligence') && [
                                'Exploitability > generic severity',
                                'Noise collapse → ordered queue',
                                'Identity blast-radius factoring'
                            ].map(line => <li key={line}>{line}</li>)}
                        </ul>
                    </a>
                ))}
            </div>
        </section>
    );
}
