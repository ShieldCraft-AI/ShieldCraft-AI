import styles from './LandingHero.module.css';

export default function LandingHero() {
    return (
        <div className={styles.heroContainer}>
            <div className={styles.badgeRow}>
                <img src="https://img.shields.io/badge/AI%20Security-Shieldcraft%20AI-blueviolet?style=for-the-badge&logo=amazonaws&logoColor=white" alt="Shieldcraft AI" />
                <a href="https://github.com/Dee66/shieldcraft-ai/actions/workflows/ci.yml" className={styles.ciBadge}>
                    <img src="https://github.com/Dee66/shieldcraft-ai/actions/workflows/ci.yml/badge.svg" alt="CI Status" />
                </a>
            </div>
            <h1 className={styles.title}>
                <img
                    src="/img/favicon.ico"
                    alt="ShieldCraft AI Logo"
                    style={{ width: 36, height: 36, verticalAlign: 'middle', marginRight: 12, borderRadius: 8 }}
                />
                Autonomous Cloud Security
            </h1>
            <p className={styles.tagline}>
                Stop Reacting. Start Predicting.
            </p>
        </div>
    );
}
