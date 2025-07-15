import React from 'react';
import Link from '@docusaurus/Link';
import styles from './LandingHero.module.css';

export default function LandingHero() {
    return (
        <div className={styles.heroContainer}>
            <div className={styles.badgeRow}>
                <img src="https://img.shields.io/badge/AI%20Security-Shieldcraft%20AI-blueviolet?style=for-the-badge&logo=amazonaws&logoColor=white" alt="Shieldcraft AI" />
                <a href="https://github.com/Dee66/shieldcraft-ai/actions/workflows/ci.yml" className={styles.ciBadge}>
                    <img src="https://github.com/Dee66/shieldcraft-ai/actions/workflows/ci.yml/badge.svg" alt="CI Status" />
                </a>
            </div>
            <h1 className={styles.title}>🛡️ Autonomous Cloud Security</h1>
            <p className={styles.subtitle}><em>From Reactive to Predictive: Proactive, Adaptive, Autonomous Cybersecurity for the Modern Enterprise.</em></p>
            <div className={styles.ctaRow}>
                <Link to="/intro" className={styles.ctaButton}>EXPLORE THE DOCS</Link>
            </div>
        </div>
    );
}
