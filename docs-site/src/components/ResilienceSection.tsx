import React from 'react';
import styles from './ResilienceSection.module.css';

export default function ResilienceSection() {
    const points = [
        {
            title: 'Streamline Operations',
            description: 'Leverage automation to eliminate inefficiencies and empower your security teams.'
        },
        {
            title: 'Fortify Defenses',
            description: 'Adapt and strengthen your security posture against emerging threats with continuous validation.'
        },
        {
            title: 'Optimize Investments',
            description: 'Maximize ROI by aligning security spend with intelligent, risk-based prioritization.'
        },
        {
            title: 'Stay Ahead',
            description: 'Transition to a proactive defense strategy, neutralizing threats before they escalate.'
        }
    ];

    return (
        <section className={styles.resilienceSection}>
            <div style={{ maxWidth: 980, margin: '0 auto', textAlign: 'center' }}>
                <h2 className={styles.center} style={{ fontSize: '2.5em', color: 'var(--sc-primary)', marginBottom: '1em' }}>
                    Elevate Security Resilience and Operational Excellence
                </h2>
                <div className={styles.infographicContainer}>
                    {points.map((point, index) => (
                        <div key={index} className={styles.infographicItem}>
                            <div className={styles.infographicIcon}>🔒</div>
                            <h3>{point.title}</h3>
                            <p>{point.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
