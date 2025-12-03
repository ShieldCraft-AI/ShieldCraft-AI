import React from 'react';
import DiagramPlaceholder from './DiagramPlaceholder';
import styles from './PlatformArchitecture.module.css';
import { FLAT_SERVICES } from './services';

type PlatformArchitectureProps = {
    selectedServiceId?: string | null;
};

export default function PlatformArchitecture({ selectedServiceId }: PlatformArchitectureProps) {
    const svc = FLAT_SERVICES.find((s) => s.id === selectedServiceId) ?? null;

    return (
        <div className={styles.archGrid} aria-label="Platform architecture">

            <div className={styles.servicesColumn}>
                <div className={styles.diagramPanel}>
                    <div className={styles.diagramPanelHeader}>
                        <span className={styles.diagramBadge}>Blueprint</span>
                        <p>Ingestion · Intelligence · Governed control</p>
                    </div>
                    <DiagramPlaceholder />
                </div>
            </div>

            <div className={styles.detailColumn}>
                <div className={`implBlock scArchSectionSpacing ${styles.usageBlockEmbedded}`} aria-live="polite">
                    <div className={styles.usageHeading}>
                        {svc ? `How ShieldCraft uses ${svc.title}` : 'ShieldCraft Implementation'}
                    </div>

                    <ul className={styles.usageList}>
                        {svc ? (
                            <>
                                <li className={styles.usageItem}>{svc.shieldcraftUse}</li>
                                {svc.details && (
                                    <li className={styles.usageItem}>{svc.details}</li>
                                )}
                            </>
                        ) : (
                            <li className={styles.usageItem}>
                                Select an AWS service to view implementation details.
                            </li>
                        )}
                    </ul>
                </div>
            </div>
        </div>
    );
}
