import React from 'react';
import styles from './DiagramPlaceholder.module.css';

export default function DiagramPlaceholder(): React.ReactElement {
    const stroke = 'var(--arch-diagram-stroke)';
    const label = 'var(--arch-diagram-label)';
    const layerStroke = 'var(--arch-layer-stroke)';
    const layerFill = 'var(--arch-layer-fill)';
    const nodeFill = 'var(--arch-diagram-node-fill)';
    const nodeStroke = 'var(--arch-diagram-node-stroke)';
    const accentSoft = 'var(--arch-diagram-accent-soft)';
    const nodeShadow = 'drop-shadow(0 8px 18px rgba(3, 5, 16, 0.36))';
    const layerHeight = 96;
    const labelOffset = 48;

    const layers = [
        { label: 'Ingestion & Governance', y: 20 },
        { label: 'GenAI & MLOps Core', y: 134 },
        { label: 'Remediation & Control', y: 248 },
    ].map(layer => ({ ...layer, labelY: layer.y + labelOffset }));

    const layerBase = { x: 60, width: 780, xStep: 48, widthStep: 92, labelX: 82, labelXStep: 48 };

    return (
        <div
            aria-hidden={false}
            role="img"
            tabIndex={0}
            aria-describedby="arch-narrative"
            aria-label="Architecture diagram showing ingestion, intelligence, and control layers"
            className={styles.diagramPanelInner}
        >
            <svg
                className={styles.diagramSvg}
                viewBox="40 0 820 340"
                width="100%"
                height="auto"
                preserveAspectRatio="xMidYMid meet"
                style={{ textRendering: 'geometricPrecision' }}
            >
                <defs>
                    <linearGradient id="gAccentSoft" x1="0" x2="1">
                        <stop offset="0" stopColor="var(--arch-diagram-accent)" stopOpacity="0.4" />
                        <stop offset="1" stopColor="var(--arch-diagram-accent)" stopOpacity="0.12" />
                    </linearGradient>
                    <filter id="soft" x="-20%" y="-40%" width="140%" height="140%" colorInterpolationFilters="sRGB">
                        <feGaussianBlur stdDeviation="6" result="b" />
                        <feComposite in="b" in2="SourceGraphic" operator="over" />
                    </filter>
                </defs>

                {layers.map((layer, index) => (
                    <React.Fragment key={layer.label}>
                        <rect
                            x={layerBase.x + index * layerBase.xStep}
                            y={layer.y}
                            rx="12"
                            ry="12"
                            width={layerBase.width - index * layerBase.widthStep}
                            height={layerHeight}
                            fill={layerFill}
                            stroke={layerStroke}
                            strokeWidth="1.3"
                        />
                        <text
                            x={layerBase.labelX + index * layerBase.labelXStep}
                            y={layer.labelY}
                            fill={label}
                            fontSize="15"
                            fontWeight="700"
                            letterSpacing="0.01em"
                            dominantBaseline="middle"
                            textRendering="geometricPrecision"
                        >
                            {layer.label}
                        </text>
                    </React.Fragment>
                ))}

                <ellipse
                    cx="450"
                    cy="182"
                    rx="200"
                    ry="32"
                    fill={accentSoft}
                    filter="url(#soft)"
                    opacity="0.95"
                    style={{ pointerEvents: 'none' }}
                />

                <g fill={nodeFill} stroke={nodeStroke} strokeWidth="1.15" style={{ filter: nodeShadow }}>
                    <circle cx="160" cy="80" r="10" />
                    <circle cx="300" cy="80" r="10" />
                    <circle cx="440" cy="80" r="10" />
                    <circle cx="580" cy="80" r="10" />
                    <circle cx="720" cy="80" r="10" />
                </g>

                <g fill={nodeFill} stroke={nodeStroke} strokeWidth="1.15" style={{ filter: nodeShadow }}>
                    <rect x="204" y="168" rx="6" ry="6" width="112" height="30" />
                    <rect x="384" y="168" rx="6" ry="6" width="112" height="30" />
                    <rect x="564" y="168" rx="6" ry="6" width="112" height="30" />
                </g>

                <g fill={nodeFill} stroke={nodeStroke} strokeWidth="1.15" style={{ filter: nodeShadow }}>
                    <circle cx="220" cy="272" r="10" />
                    <circle cx="360" cy="272" r="10" />
                    <circle cx="500" cy="272" r="10" />
                    <circle cx="640" cy="272" r="10" />
                </g>

                <g
                    stroke={stroke}
                    strokeWidth="0.95"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    vectorEffect="non-scaling-stroke"
                >
                    <line x1="160" y1="90" x2="260" y2="168" />
                    <line x1="300" y1="90" x2="260" y2="168" />
                    <line x1="440" y1="90" x2="440" y2="168" />
                    <line x1="580" y1="90" x2="620" y2="168" />
                    <line x1="720" y1="90" x2="620" y2="168" />

                    <line x1="260" y1="198" x2="220" y2="262" />
                    <line x1="440" y1="198" x2="360" y2="262" />
                    <line x1="440" y1="198" x2="500" y2="262" />
                    <line x1="620" y1="198" x2="500" y2="262" />
                    <line x1="620" y1="198" x2="640" y2="262" />
                </g>
            </svg>
        </div>
    );
}
