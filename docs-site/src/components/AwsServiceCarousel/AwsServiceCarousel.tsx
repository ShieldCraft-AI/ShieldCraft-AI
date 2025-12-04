import React, { useRef, useEffect } from 'react';
import styles from './AwsServiceCarousel.module.css';
import { SERVICE_GROUPS, FLAT_SERVICES } from '../services';
import type { AwsService } from '../services';

export type AwsServiceCarouselProps = {
    selected?: string;
    onSelect?: (id: string) => void;
};

export default function AwsServiceCarousel({
    selected,
    onSelect,
}: AwsServiceCarouselProps): JSX.Element {
    const cardRefs = useRef<Map<string, HTMLButtonElement>>(new Map());

    const handleKeyDown = (e: React.KeyboardEvent, service: AwsService, index: number) => {
        let targetIndex = index;

        switch (e.key) {
            case 'ArrowLeft':
                e.preventDefault();
                targetIndex = index > 0 ? index - 1 : FLAT_SERVICES.length - 1;
                break;
            case 'ArrowRight':
                e.preventDefault();
                targetIndex = index < FLAT_SERVICES.length - 1 ? index + 1 : 0;
                break;
            case 'Home':
                e.preventDefault();
                targetIndex = 0;
                break;
            case 'End':
                e.preventDefault();
                targetIndex = FLAT_SERVICES.length - 1;
                break;
            default:
                return;
        }

        const targetService = FLAT_SERVICES[targetIndex];
        onSelect?.(targetService.id);
        cardRefs.current.get(targetService.id)?.focus();
    };

    return (
        <div className={styles.gridContainer} role="region" aria-label="AWS Services">
            <div className={styles.gridHeader}>
                <h3 className={styles.gridTitle}>AWS Services</h3>
                <p className={styles.gridSubtitle}>Select a service to see implementation details</p>
            </div>

            <div
                className={styles.servicesGrid}
                role="tablist"
            >
                {FLAT_SERVICES.map((service, index) => {
                    const isSelected = service.id === selected;
                    return (
                        <button
                            key={service.id}
                            ref={(el) => {
                                if (el) cardRefs.current.set(service.id, el);
                            }}
                            role="tab"
                            aria-selected={isSelected}
                            aria-controls={`service-detail-${service.id}`}
                            id={`service-tab-${service.id}`}
                            tabIndex={isSelected ? 0 : -1}
                            className={`${styles.serviceCard} ${isSelected ? styles.selected : ''}`}
                            onClick={() => onSelect?.(service.id)}
                            onKeyDown={(e) => handleKeyDown(e, service, index)}
                            type="button"
                        >
                            <div className={styles.iconWrapper}>
                                <img
                                    src={service.icon}
                                    alt=""
                                    width={40}
                                    height={40}
                                    className={styles.icon}
                                    loading="lazy"
                                    decoding="async"
                                />
                            </div>
                            <span className={styles.cardTitle}>{service.title}</span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
