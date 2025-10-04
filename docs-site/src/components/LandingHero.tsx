import AwsBadge from './AwsBadge';
import styles from './LandingHero.module.css';

export default function LandingHero() {
    return (
        <header className={styles.heroRoot}>
            <div className={styles.backLayer} aria-hidden="true" />
            <div className={styles.heroInner}>
                <div className={styles.heroContent}>
                    <h1 className={styles.heroHeading}>Autonomous security for AWS</h1>
                    <h2 className={styles.heroSubheading}>Learn. Detect. Remediate. Benchmarked results you can defend.</h2>
                    <p className={styles.heroLead}>
                        Built on a security-optimized foundation model and further trained on your domain and past incidents, including simulated multi-stage attacks. Continuous detection drives policy-guarded automation. The agent applies compliant fixes at speed. Posture hardening is instant across accounts and regions, with all actions monitored and audited.
                    </p>
                </div>
            </div>
        </header>
    );
}
