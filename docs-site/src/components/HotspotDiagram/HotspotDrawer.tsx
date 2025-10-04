import React from 'react';
import styles from './HotspotDrawer.module.css';
import type { Capability, Env } from './types';

interface Props {
    open: boolean;
    onClose: () => void;
    capability?: Capability;
    env: Env;
}

export default function HotspotDrawer({ open, onClose, capability, env }: Props) {
    if (!open || !capability) return null;
    const svc = capability.recommendedByEnv[env];
    return (
        <aside className={styles.drawer} role="dialog" aria-labelledby="hotspot-title">
            <div className={styles.header}>
                <strong id="hotspot-title">{capability.title}</strong>
                <button className={styles.closeBtn} onClick={onClose} aria-label="Close">✕</button>
            </div>
            <div className={styles.content}>
                {capability.summary && <p>{capability.summary}</p>}
                <h4>Services ({env})</h4>
                <ul>
                    <li><strong>{svc.name}</strong>{svc.description ? ` - ${svc.description}` : ''}</li>
                </ul>
                {capability.alternatives && capability.alternatives.length > 0 && (
                    <>
                        <h4>Alternatives</h4>
                        <ul>
                            {capability.alternatives.map((alt, i) => (
                                <li key={i}><strong>{alt.service}</strong>: {alt.whenToChoose}</li>
                            ))}
                        </ul>
                    </>
                )}
                {capability.proofLinks && capability.proofLinks.length > 0 && (
                    <>
                        <h4>Proof</h4>
                        <ul>
                            {capability.proofLinks.map((p, i) => (
                                <li key={i}><a href={p.href}>{p.label}</a> ({p.kind})</li>
                            ))}
                        </ul>
                    </>
                )}
            </div>
        </aside>
    );
}
