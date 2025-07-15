import React from 'react';
import styles from './CTASection.module.css';

export default function CTASection() {
    return (
        <section className={styles.ctaSection}>
            <h2 className={styles.center}>Ready to Transform Your Cloud Security?</h2>
            <div className={styles.ctaRow}>
                <a href="#get-started" className={styles.ctaButton}>GET STARTED WITH SHIELDCRAFT AI</a>
                <a href="/docs" className={styles.ctaButton} style={{ marginLeft: '2em' }}>EXPLORE ALL DOCUMENTATION</a>
            </div>
        </section>
    );
}
