import React, { useState } from 'react';
import styles from './PlatformArchitecture.module.css';
import AwsServiceSelector from '../AwsServiceSelector/AwsServiceSelector';
import DiagramPlaceholder from '../DiagramPlaceholder/DiagramPlaceholder';
import { FLAT_SERVICES } from '../services';

export default function PlatformArchitecture() {
    const [selected, setSelected] = useState(FLAT_SERVICES[0]?.id);

    const svc = FLAT_SERVICES.find((s) => s.id === selected) ?? null;

    return (
        <div
            data-arch-escape="true"
            style={{
                width: '100%',
                maxWidth: 'none',
                boxSizing: 'border-box',
                paddingLeft: 0,
                paddingRight: 0,
            }}
        >
            <div className={styles.archRoot}>
                <div className={styles.archGrid}>
                    <div className={styles.archLeft}>
                        <AwsServiceSelector selected={selected} onSelect={setSelected} />
                    </div>

                    <div className={styles.archRight}>
                        <section className={styles.blueprintPanel}>
                            <header className={styles.blueprintHeader}>
                                <span className={styles.badge}>Blueprint</span>
                                <p>Ingestion · Intelligence · Governed control</p>
                            </header>
                            <DiagramPlaceholder />
                        </section>

                        <section className={styles.implCard}>
                            <h4 className={styles.implTitle}>
                                {svc ? `How ShieldCraft uses ${svc.title}` : 'ShieldCraft Implementation'}
                            </h4>
                            <ul className={styles.implList}>
                                <li>{svc?.shieldcraftUse}</li>
                                {svc?.details && <li>{svc.details}</li>}
                            </ul>
                        </section>
                    </div>
                </div>
            </div>
        </div>
    );
}
