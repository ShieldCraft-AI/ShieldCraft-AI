import React from 'react';
import styles from './FoundationSection.module.css';

export default function FoundationSection() {
    return (
        <section className={styles.foundationSection}>
            <h2 className={styles.center}>Engineered for the Enterprise. Built for the Cloud.</h2>
            <p className={styles.center}>
                ShieldCraft AI stands on a meticulously engineered, <b>enterprise-grade AWS and MLOps foundation</b>. This cloud-native architecture ensures unparalleled scalability, robust security, continuous innovation, and unwavering reliability for your most critical deployments. It's the resilient backbone empowering our AI to deliver precise, real-time security automation and insights.
            </p>
            <div className={styles.architectureRow}>
                <a href="#architecture" className={styles.architectureButton}>SEE FULL ARCHITECTURE DETAILS</a>
            </div>
        </section>
    );
}
