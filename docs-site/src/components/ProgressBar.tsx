import React from 'react';

type ProgressBarProps = {
    value: number; // 0-100
    label?: string;
    height?: number; // px
    showLabel?: boolean;
};

export default function ProgressBar({ value, label = 'Progress', height = 18, showLabel = true }: ProgressBarProps) {
    const clamped = Math.max(0, Math.min(100, value));
    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, margin: '1rem 0' }}>
            {showLabel && (
                <div style={{ color: '#b3b3b3', fontWeight: 600 }}>{label}</div>
            )}
            <div
                role="progressbar"
                aria-valuenow={clamped}
                aria-valuemin={0}
                aria-valuemax={100}
                style={{
                    width: '60%',
                    background: '#222',
                    border: '1px solid #a5b4fc',
                    borderRadius: 10,
                    overflow: 'hidden',
                    height,
                    boxShadow: '0 2px 8px #222',
                }}
            >
                <div
                    style={{
                        width: `${clamped}%`,
                        height: '100%',
                        background: 'linear-gradient(90deg, #6366f1, #22d3ee)',
                    }}
                />
            </div>
            <div style={{ color: '#e0e0e0' }}>{clamped}% Complete</div>
        </div>
    );
}
