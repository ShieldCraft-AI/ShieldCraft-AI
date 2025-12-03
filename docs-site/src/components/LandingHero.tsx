import React from 'react';
import styles from './LandingHero.module.css';
import pageStyles from '../pages/index.module.css';
import PremiumButton from './ButtonPremium';
export default function LandingHero(): React.ReactElement {
    return (
        <section className={styles.hero}>
            <div className={styles.heroInner}>
                <h1 className={`${styles.title} ${styles.heroHeading}`}>Autonomous AI Security</h1>
                <p className={`${styles.subtitle} ${styles.heroSubheading}`}>
                    Govern and scale GenAI on AWS with deterministic, policy-guarded automation.
                </p>
                <div className={`${styles.buttonRow} ${styles.heroButtonRow}`}>
                    <PremiumButton className={pageStyles.scButtonPrimary}>Get Started</PremiumButton>
                    <PremiumButton variant="secondary" className={pageStyles.scButtonSecondary}>Documentation</PremiumButton>
                </div>
            </div>
        </section>
    );
}
