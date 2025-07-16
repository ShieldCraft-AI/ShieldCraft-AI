import React from 'react';
import styles from './ResilienceSection.module.css';

export default function ResilienceSection() {
    return (
        <section className={styles.resilienceSection}>
            <div style={{ maxWidth: 980, margin: '0 auto' }}>
                <h2 className={styles.center} style={{ fontSize: '1.5em', color: '#a5b4fc', marginBottom: '0.7em' }}>
                    Unlock Unprecedented Security Resilience & Efficiency
                </h2>
                <ul className={styles.resilienceList} style={{ lineHeight: 1.7, fontSize: '1.13em', margin: '0 auto', maxWidth: 900, textAlign: 'left' }}>
                    <li><b>Elevate Efficiency:</b> Automate repetitive tasks, freeing security teams for high-value strategic initiatives.</li>
                    <li><b>Boost Resilience:</b> Continuously validate and improve your defenses against an evolving threat landscape.</li>
                    <li><b>Reduce Risk & Cost:</b> Minimize breach impact and optimize security spend through intelligent, automated operations.</li>
                    <li><b>Gain Proactive Insight:</b> Anticipate and neutralize threats before they materialize, shifting from reactive to strategic defense.</li>
                </ul>
            </div>
        </section>
    );
}
