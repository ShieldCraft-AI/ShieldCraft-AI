import React, { useState } from 'react';
import styles from './DataFlowAnimation.module.css';

export type DataFlowAnimationProps = {
    id?: string;
    webmSrc: string; // path under /static
    mp4Src: string;  // path under /static
    width?: number | string;
    className?: string;
    alt?: string; // for accessibility description
    posterSrc?: string; // optional poster image
};

export default function DataFlowAnimation({ id = 'dataFlow1', webmSrc, mp4Src, width = 320, className, alt, posterSrc = '/img/logo.png' }: DataFlowAnimationProps) {
    const [failed, setFailed] = useState(false);
    const isDefaultLogo = posterSrc === '/img/logo.png';
    return (
        <div className={`${styles.wrap} ${className ?? ''}`.trim()}>
            {failed ? (
                <img
                    src={posterSrc}
                    alt={alt ?? 'Data flow'}
                    className={isDefaultLogo ? styles.logoPoster : styles.poster}
                />
            ) : (
                // eslint-disable-next-line jsx-a11y/media-has-caption
                <video
                    className={styles.video}
                    id={id}
                    width={typeof width === 'number' ? width : undefined}
                    style={typeof width === 'string' ? { width } : undefined}
                    loop
                    autoPlay
                    muted
                    playsInline
                    preload="auto"
                    aria-label={alt ?? 'Data flow animation'}
                    poster={isDefaultLogo ? undefined : posterSrc}
                    onError={() => setFailed(true)}
                >
                    <source src={webmSrc} type="video/webm" />
                    <source src={mp4Src} type="video/mp4" />
                </video>
            )}
        </div>
    );
}
