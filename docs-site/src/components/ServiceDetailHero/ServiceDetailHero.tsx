import React, { JSX } from 'react';
import styles from './ServiceDetailHero.module.css';
import type { AwsService } from '../services';

export type ServiceDetailHeroProps = {
    service: AwsService;
};

export default function ServiceDetailHero({ service }: ServiceDetailHeroProps): JSX.Element {
    return (
        <>
            {/* Empty spacer to match grid header height */}
            <div className={styles.headerSpacer} aria-hidden="true" />

            <div
                className={styles.hero}
                role="tabpanel"
                id={`service-detail-${service.id}`}
                aria-labelledby={`service-tab-${service.id}`}
            >
                <div className={styles.heroContent}>
                    <div className={styles.headerRow}>
                        <div className={styles.iconLarge}>
                            <img
                                src={service.icon}
                                alt=""
                                width={64}
                                height={64}
                                className={styles.iconImg}
                                loading="eager"
                            />
                        </div>
                        <div className={styles.headerText}>
                            <h3 className={styles.title}>{service.title}</h3>
                            <p className={styles.summary}>{service.summary}</p>
                        </div>
                    </div>

                    <div className={styles.detailsGrid}>
                        <div className={styles.detailSection}>
                            <h4 className={styles.detailHeading}>
                                <span className={styles.badge}>ShieldCraft Implementation</span>
                            </h4>
                            <div className={styles.detailContent}>
                                <p className={styles.usageText}>{service.shieldcraftUse}</p>
                                {service.details && (
                                    <p className={styles.detailsText}>{service.details}</p>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Decorative accent */}
                <div className={styles.accentGlow} aria-hidden="true" />
            </div>
        </>
    );
}
