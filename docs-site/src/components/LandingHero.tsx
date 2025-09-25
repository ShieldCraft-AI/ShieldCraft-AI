import AwsBadge from './AwsBadge';
import styles from './LandingHero.module.css';

export default function LandingHero() {
    return (
        <header className={styles.heroRoot}>
            <div className={styles.backLayer} aria-hidden="true" />
            <div className={styles.heroInner}>
                <div className={styles.heroContent}>
                    <h1 className={styles.heroHeading}>Autonomous Cloud Security</h1>
                    <h2 className={styles.heroSubheading}>Predict. Prevent. Self‑Heal.</h2>
                    <p className={styles.heroLead}>
                        From raw AWS signals to autonomous, reversible action. ShieldCraft correlates telemetry, predicts blast radius, and applies guarded self-healing, misconfiguration and emerging threats are remediated before they become incidents.
                    </p>
                </div>
            </div>
        </header>
    );
}
