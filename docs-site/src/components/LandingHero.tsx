import AwsBadge from './AwsBadge';
import styles from './LandingHero.module.css';

export default function LandingHero() {
    return (
        <header className={styles.heroRoot}>
            <div className={styles.backLayer} aria-hidden="true" />
            <div className={styles.heroInner}>
                <div className={styles.heroContent}>
                    <h1 className={styles.heroHeading}>Autonomous AI Security</h1>
                    <h2 className={styles.heroSubheading}>Govern and Scale GenAI on AWS.</h2>
                    <p className={styles.heroLead}>
                        Built on a security-optimized MLOps platform, ShieldCraft AI leverages a domain-trained foundation model to drive Policy-Guarded Automation. The platform enforces auditable and reversible fixes at speed, guaranteeing Instant Posture Hardening across accounts and regions.
                    </p>
                </div>
            </div>
        </header>
    );
}
