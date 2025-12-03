import React from 'react';

export default function ScrollLeftColumn(): JSX.Element {
    const rows = new Array(12).fill(null).map((_, i) => (
        <article aria-label={`Layer ${i + 1}`} key={i} style={{
            position: 'relative',
            padding: '16px',
            marginBottom: 12,
            borderRadius: 10,
            background: 'linear-gradient(90deg, rgba(255,255,255,0.01), rgba(255,255,255,0.00))',
            border: '1px solid rgba(255,255,255,0.02)',
            scrollSnapAlign: 'start'
        }}>
            <strong style={{ fontSize: 14, color: '#c9e0ff' }}>Layer {i + 1}</strong>
            <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)', maxWidth: '52ch' }}>Concise description of layer functionality and SLA.</div>
        </article>
    ));

    return (
        <div style={{ paddingRight: 12, paddingLeft: 6 }}>
            <div style={{ fontSize: 12, color: 'var(--muted-1)', marginBottom: 8 }}>Use mouse or keyboard to scroll the layers.</div>
            <h3 style={{ marginTop: 0, marginBottom: 12, color: '#d6e9ff' }}>Architecture - scroll for layers</h3>
            {rows}
        </div>
    );
}
