import React from 'react';
import Link from '@docusaurus/Link';
import styles from './FullWidthFeature.module.css';

type Props = {
    eyebrow?: string;
    variant?: 'enterprise';
    heading: string;
    description?: string;
    primaryHref?: string;
    primaryLabel?: string;
    secondaryHref?: string;
    secondaryLabel?: string;
    id?: string;
    className?: string;
};

export default function FullWidthFeature({
    eyebrow,
    heading,
    description,
    primaryHref,
    primaryLabel,
    secondaryHref,
    secondaryLabel,
    id,
    className,
    variant,
}: Props) {
    const innerContent = (
        <>
            {eyebrow && <div className={styles.eyebrow}>{eyebrow}</div>}
            <h2 className={styles.heading}>{heading}</h2>
            {description && <p className={styles.desc}>{description}</p>}
            {(primaryHref || secondaryHref) && (
                <div className={styles.ctaRow}>
                    {primaryHref && primaryLabel && (
                        <Link to={primaryHref} className={styles.ctaPrimary}>{primaryLabel}</Link>
                    )}
                    {secondaryHref && secondaryLabel && (
                        <Link to={secondaryHref} className={styles.ctaGhost}>{secondaryLabel}</Link>
                    )}
                </div>
            )}
        </>
    );

    return (
        <section id={id} className={`${styles.band} ${className ?? ''}`.trim()}>
            <div className={styles.inner}>
                {variant === 'enterprise' ? (
                    <div className={styles.enterpriseCTA}>{innerContent}</div>
                ) : (
                    innerContent
                )}
            </div>
        </section>
    );
}
