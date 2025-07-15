import React from 'react';
import styles from './AdvantageCards.module.css';

const cards = [
    {
        title: '⚡️ Autonomous Remediation',
        link: '/automated-alert-triage',
        benefit: 'Instant Healing.',
        description: 'Automatically analyze, generate, and execute AWS-native fixes within secure guardrails, slashing MTTR and minimizing breach impact. Your cloud heals itself.'
    },
    {
        title: '🧪 Generative Attack Emulation',
        link: '/automated-attack-simulation',
        benefit: 'Uncover Unknowns.',
        description: 'AI creates novel, polymorphic attack scenarios tailored to your environment, validating defenses against future zero-days and cultivating true adaptive resilience.'
    },
    {
        title: '📊 Predictive Threat Intelligence',
        link: '/threat-detection',
        benefit: 'Precise Prioritization.',
        description: 'Correlate your AWS posture with global threats to predict exploitable vulnerabilities, eliminating alert fatigue and focusing resources where they matter most.'
    }
];

export default function AdvantageCards() {
    return (
        <section className={styles.cardsSection}>
            <h2 className={styles.center}>ShieldCraft AI: Your Strategic Security Advantage</h2>
            <div className={styles.cardsRow}>
                {cards.map(card => (
                    <div className={styles.card} key={card.title}>
                        <h3>
                            <a href={card.link} style={{ color: '#a5b4fc', textDecoration: 'none' }}>{card.title}</a>
                        </h3>
                        <p><b>{card.benefit}</b> {card.description}</p>
                    </div>
                ))}
            </div>
        </section>
    );
}
