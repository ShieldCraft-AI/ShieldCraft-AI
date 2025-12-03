import React from 'react';

/**
 * MotionLayer: lightweight pseudo-decorative layer that sits behind hero
 * No external libs. Pure CSS-based micro motion via inline SVG transforms.
 */
export default function MotionLayer(): JSX.Element {
    return (
        <div aria-hidden="true" style={{
            position: 'absolute',
            inset: 0,
            pointerEvents: 'none',
            zIndex: 0,
            overflow: 'hidden'
        }}>
            <svg width="100%" height="100%" style={{ position: 'absolute', right: '-10%', top: '-8%', opacity: 0.12 }}>
                <defs>
                    <linearGradient id="g1" x1="0" x2="1">
                        <stop offset="0" stopColor="#2dd4bf" stopOpacity="0.14" />
                        <stop offset="1" stopColor="#60a5fa" stopOpacity="0.08" />
                    </linearGradient>
                </defs>
                <circle cx="300" cy="120" r="220" fill="url(#g1)">
                    <animate attributeName="cx" dur="18s" values="300;340;300" repeatCount="indefinite" />
                </circle>
            </svg>
        </div>
    );
}
