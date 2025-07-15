import React from 'react';
import styles from './StrategicAdvantage.module.css';

export default function StrategicAdvantage() {
    return (
        <section className={styles.advantageSection}>
            <h2 className={styles.center}>Stop Reacting. Start Predicting.</h2>
            <p className={styles.center}>
                In today's relentless cloud landscape, traditional security is overwhelmed by AI-augmented attacks, zero-days, and subtle insider risks.
            </p>
            <p className={styles.center}>ShieldCraft AI transforms your enterprise security posture, empowering you to <b>anticipate, adapt, and autonomously defeat threats</b> with unmatched speed and precision.
            </p>
        </section>
    );
}
