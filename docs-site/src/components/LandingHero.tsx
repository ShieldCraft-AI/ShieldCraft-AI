import AwsBadge from './AwsBadge';
import styles from './LandingHero.module.css';

export default function LandingHero() {
    return (
        <div className={styles.heroContainer} style={{ position: 'relative' }}>
            <AwsBadge />
            <div className={styles.heroBackground}></div>
            <div className={styles.heroContent}>
                <h1 className={styles.title}>
                    Autonomous Cloud Security
                </h1>
                <p className={styles.tagline}>
                    Stop Reacting. Start Predicting.
                </p>
            </div>
        </div>
    );
}
