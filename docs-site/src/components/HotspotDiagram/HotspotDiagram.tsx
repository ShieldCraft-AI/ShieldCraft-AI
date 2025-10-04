import React, { useMemo, useState } from 'react';
import styles from './HotspotDiagram.module.css';
import HotspotDrawer from './HotspotDrawer';
import type { Capability, Env } from './types';
import { capabilities, defaultEnv } from './hotspotData';

export default function HotspotDiagram() {
    const [env, setEnv] = useState<Env>(defaultEnv);
    const [open, setOpen] = useState(false);
    const [selected, setSelected] = useState<Capability | undefined>(undefined);

    // Hotspot rects in exported SVG viewBox coordinates (-0.5 -0.5 901 185)
    const hotspots = useMemo(() => ([
        { id: 'node_ingestion', x: 0, y: 0, w: 180, h: 64 },
        { id: 'node_correlation', x: 240, y: 0, w: 180, h: 64 },
        { id: 'node_guardrails', x: 480, y: 0, w: 180, h: 64 },
        { id: 'node_actions', x: 720, y: 0, w: 180, h: 64 },
        { id: 'node_observability', x: 240, y: 120, w: 180, h: 64 },
    ]), []);

    const onHotspotClick = (id: string) => {
        const cap = capabilities.find(c => c.id === id);
        if (!cap) return;
        setSelected(cap);
        setOpen(true);
    };

    return (
        <div className={styles.root}>
            <div className={styles.toolbar}>
                <label>
                    Environment:
                    <select value={env} onChange={(e) => setEnv(e.target.value as Env)}>
                        <option value="dev">dev</option>
                        <option value="staging">staging</option>
                        <option value="prod">prod</option>
                    </select>
                </label>
            </div>
            <div className={styles.svgWrap}>
                <img src={require('@site/static/img/diagrams/interactive_hotspots.svg').default} alt="Interactive architecture" className={styles.baseImg} />
                <svg className={styles.overlaySvg} viewBox="-0.5 -0.5 901 185" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                    {hotspots.map(h => (
                        <rect
                            key={h.id}
                            className={styles.hotspot}
                            x={h.x}
                            y={h.y}
                            width={h.w}
                            height={h.h}
                            rx={8}
                            onClick={() => onHotspotClick(h.id)}
                        />
                    ))}
                </svg>
            </div>
            <HotspotDrawer open={open} onClose={() => setOpen(false)} capability={selected} env={env} />
        </div>
    );
}
