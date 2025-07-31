import { useEffect } from 'react';
import styles from './LandingHero.module.css';

export default function AwsBadge() {
    useEffect(() => {
        // Only load the script if the desktop badge is visible
        const mq = window.matchMedia('(min-width: 601px)');
        if (mq.matches && !document.getElementById('credly-embed-script')) {
            const script = document.createElement('script');
            script.id = 'credly-embed-script';
            script.src = '//cdn.credly.com/assets/utilities/embed.js';
            script.async = true;
            document.body.appendChild(script);
        }
    }, []);

    return (
        <div className={styles.awsBadgeContainer}>
            {/* Desktop: Credly embed */}
            <div className={styles.awsBadgeDesktop}>
                <div
                    data-iframe-width="150"
                    data-iframe-height="270"
                    data-share-badge-id="aece6ebf-489a-454c-a66a-0c34412574ea"
                    data-share-badge-host="https://www.credly.com"
                ></div>
            </div>
            {/* Mobile: Static thumbnail */}
            <a
                className={styles.awsBadgeMobile}
                href="https://www.credly.com/badges/aece6ebf-489a-454c-a66a-0c34412574ea/public_url"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="View AWS Certification Badge on Credly"
            >
                <img
                    src="/img/aif.png"
                    alt="AWS Certification Badge"
                    style={{ width: '64px', height: '64px', borderRadius: '8px', boxShadow: '0 2px 8px #23252633' }}
                />
            </a>
        </div>
    );
}
