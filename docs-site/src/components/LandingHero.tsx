import AwsBadge from './AwsBadge';
import styles from './LandingHero.module.css';

export default function LandingHero() {
    return (
        <div className={styles.heroContainer} style={{ position: 'relative' }}>
            <AwsBadge
                badges={[
                    {
                        id: 'aece6ebf-489a-454c-a66a-0c34412574ea',
                        url: 'https://www.credly.com/badges/aece6ebf-489a-454c-a66a-0c34412574ea/public_url',
                        mobileThumbSrc: '/img/aif.png',
                        alt: 'AWS Certified Solutions Architect – Associate',
                    },
                    {
                        id: 'effc7f36-41df-427d-ba8a-33e147a24f0d',
                        url: 'https://www.credly.com/badges/effc7f36-41df-427d-ba8a-33e147a24f0d/public_url',
                        mobileThumbSrc: '/img/saa.png',
                        alt: 'AWS Certification',
                    },
                ]}
            />
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
