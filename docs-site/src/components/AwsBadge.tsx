import React, { useEffect } from 'react';
import styles from './LandingHero.module.css';

type AwsBadgeItem = {
    id: string; // Credly badge ID
    url?: string; // Public URL to the badge; defaults to Credly URL built from id
    mobileThumbSrc?: string; // Optional mobile thumbnail path
    alt?: string; // Accessible label/alt
    width?: number; // Desktop iframe width (default 150)
    height?: number; // Desktop iframe height (default 270)
};

export default function AwsBadge({ badges }: { badges: AwsBadgeItem[] }) {
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

    const fallbackThumb = '/img/aif.png';

    return (
        <div className={styles.awsBadgeContainer}>
            {/* Desktop: Credly embeds (stacked) */}
            <div className={styles.awsBadgeDesktop}>
                {badges.map((b) => {
                    const width = String(b.width ?? 150);
                    const height = String(b.height ?? 270);
                    return (
                        <div
                            key={b.id}
                            data-iframe-width={width}
                            data-iframe-height={height}
                            data-share-badge-id={b.id}
                            data-share-badge-host="https://www.credly.com"
                            style={{ margin: '4px' }}
                        />
                    );
                })}
            </div>

            {/* Mobile: Row of static thumbnails linking to Credly */}
            <div className={styles.awsBadgeMobile} style={{ gap: 12 }}>
                {badges.map((b) => {
                    const url = b.url ?? `https://www.credly.com/badges/${b.id}/public_url`;
                    return (
                        <a
                            key={b.id}
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label={b.alt ?? 'View AWS Certification Badge on Credly'}
                            title={b.alt ?? 'AWS Certification Badge'}
                        >
                            <img
                                src={b.mobileThumbSrc || fallbackThumb}
                                alt={b.alt || 'AWS Certification Badge'}
                                style={{ width: '64px', height: '64px', borderRadius: '8px', boxShadow: '0 2px 8px #23252633' }}
                            />
                        </a>
                    );
                })}
            </div>
        </div>
    );
}
