import AwsBadge from './AwsBadge';
import styles from './LandingHero.module.css';

export default function LandingHero() {
    return (
        <header className={styles.heroRoot}>
            <div className={styles.backLayer} aria-hidden="true" />
            <div className={styles.heroInner}>
                <div className={styles.heroContent}>
                    <h1 className={styles.heroHeading}>Autonomous AI Security: The Governed Control Plane for GenAI on AWS.</h1>
                    <h2 className={styles.heroSubheading}>Trust, Auditability, and Deterministic Control for enterprise AI operations.</h2>
                    <p className={styles.heroLead}>
                        Built on a security-optimized MLOps platform, ShieldCraft AI leverages a domain-trained foundation model to drive <strong>Policy-Guarded Automation</strong>. The platform enforces auditable and reversible fixes at speed, guaranteeing <strong>Instant Posture Hardening</strong> across accounts and regions.
                    </p>
                    <p className={styles.heroLead}>
                        ShieldCraft AI, your Strategic Security Advantage: <strong>Governed by MLOps, Delivered via CDK SDK.</strong>
                    </p>
                    <div className={styles.heroCTAs}>
                        <a className={styles.ctaPrimary} href="/architecture-overview">Review The MLOps Governance (The Proof)</a>
                        <a className={styles.ctaSecondary} href="/plugins">Explore The Full Product Suite</a>
                        <a className={styles.ctaGhost} href="/pricing">View Deterministic Pricing &amp; Tiers</a>
                    </div>
                </div>
            </div>
        </header>
    );
}
