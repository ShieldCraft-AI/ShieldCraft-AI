import React, { useEffect, useRef } from 'react';
import styles from './AwsServiceSelector.module.css';
import type { AwsService } from '../services';
import { FLAT_SERVICES, DEFAULT_SERVICE_ID } from '../services';

export type AwsServiceSelectorProps = {
    selected?: string;
    onSelect?: (id: string) => void;
    'aria-label'?: string;
};

export default function AwsServiceSelector({
    selected = DEFAULT_SERVICE_ID,
    onSelect,
    'aria-label': ariaLabel = 'AWS Services Selector',
}: AwsServiceSelectorProps): JSX.Element {
    const buttonsRef = useRef<Array<HTMLButtonElement | null>>([]);

    useEffect(() => {
        // ensure refs length matches services
        if (!buttonsRef.current || buttonsRef.current.length !== FLAT_SERVICES.length) {
            buttonsRef.current = Array(FLAT_SERVICES.length).fill(null);
        }
    }, []);

    const setActive = (id: string) => onSelect?.(id);

    const moveFocus = (idx: number) => {
        const n = FLAT_SERVICES.length;
        const normalized = (idx + n) % n;
        buttonsRef.current[normalized]?.focus();
        onSelect?.(FLAT_SERVICES[normalized].id);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>, index: number) => {
        switch (e.key) {
            case 'ArrowUp':
            case 'ArrowLeft':
                e.preventDefault();
                moveFocus(index - 1);
                break;
            case 'ArrowDown':
            case 'ArrowRight':
                e.preventDefault();
                moveFocus(index + 1);
                break;
            case 'Home':
                e.preventDefault();
                moveFocus(0);
                break;
            case 'End':
                e.preventDefault();
                moveFocus(FLAT_SERVICES.length - 1);
                break;
            case 'Enter':
            case ' ':
                e.preventDefault();
                setActive(FLAT_SERVICES[index].id);
                break;
            default:
                break;
        }
    };

    return (
        <div className={styles.selectorFrame} role="region" aria-label={ariaLabel}>
            <div className={styles.selector}>
                <div className={styles.serviceList} role="tablist" aria-orientation="vertical" aria-label="AWS service list">
                    {FLAT_SERVICES.map((svc, idx) => {
                        const isActive = svc.id === selected;
                        return (
                            <button
                                key={svc.id}
                                id={`svc-tab-${svc.id}`}
                                role="tab"
                                aria-selected={isActive}
                                aria-controls={`svc-${svc.id}`}
                                className={`${styles.serviceBtn} ${isActive ? styles.active : ''}`}
                                onClick={() => setActive(svc.id)}
                                onKeyDown={(e) => handleKeyDown(e as React.KeyboardEvent<HTMLButtonElement>, idx)}
                                ref={(el) => (buttonsRef.current[idx] = el)}
                                tabIndex={isActive ? 0 : -1}
                                type="button"
                                aria-label={svc.title}
                            >
                                <span className={styles.iconWrap} aria-hidden="true">
                                    <img src={svc.icon} alt="" width={20} height={20} className={styles.icon} loading="lazy" decoding="async" />
                                </span>

                                <span className={styles.meta}>
                                    <span className={styles.serviceTitle}>{svc.title}</span>
                                    <span className={styles.serviceSummary}>{svc.summary}</span>
                                </span>
                            </button>
                        );
                    })}
                </div>

                <div className={styles.right}>
                    <div id={`svc-${selected}`} role="tabpanel" aria-labelledby={`svc-tab-${selected}`} className={styles.detail}>
                        {(() => {
                            const svc = FLAT_SERVICES.find((s) => s.id === selected) ?? FLAT_SERVICES[0] as AwsService;
                            return (
                                <>
                                    <h3 className={styles.detailTitle}>{svc.title}</h3>
                                    <p className={styles.detailSummary}>{svc.summary}</p>

                                    <h4 className={styles.detailHeading}>How ShieldCraft uses {svc.title}</h4>
                                    <p className={styles.shieldUse}>{svc.shieldcraftUse}</p>

                                    {svc.details && (
                                        <>
                                            <h5 className={styles.detailHeading}>Details</h5>
                                            <p className={styles.detailsText}>{svc.details}</p>
                                        </>
                                    )}
                                </>
                            );
                        })()}
                    </div>
                </div>
            </div>
        </div>
    );
}
