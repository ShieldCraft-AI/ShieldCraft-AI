import React, { useState, useCallback } from 'react';
import { useReveal } from './hooks/useReveal';
import styles from './ArchitectureLoop.module.css';

const steps = [
    { title: 'Collect', body: 'Telemetry + findings consolidated with schema + tagging.' },
    { title: 'Enrich', body: 'Correlate identities, assets, risk signals & cost context.' },
    { title: 'Vectorize', body: 'Chunk & embed salient artifacts behind retrieval contracts.' },
    { title: 'Retrieve', body: 'Context assembly (semantic + structured) for precise prompts.' },
    { title: 'Reason / Simulate', body: 'LLM + attack generation produce hypotheses + plans.' },
    { title: 'Remediate', body: 'Guardrailed playbooks execute + checkpoint state.' },
    { title: 'Validate / Learn', body: 'Benchmarks, drift & eval metrics feed continuous tuning.' },
];

export default function ArchitectureLoop() {
    const [active, setActive] = useState<number | null>(null);
    const [visited, setVisited] = useState<boolean[]>(() => Array(steps.length).fill(false));
    useReveal();

    const onSelect = useCallback((i: number) => {
        setActive(i);
        setVisited(prev => {
            if (prev[i]) return prev; // already marked
            const next = [...prev];
            next[i] = true;
            return next;
        });
    }, []);

    const onReset = useCallback(() => {
        setVisited(Array(steps.length).fill(false));
        setActive(null);
    }, []);

    // Split into two logical rows for readability (first 4, remaining 3)
    const firstRow = steps.slice(0, 4);
    const secondRow = steps.slice(4);

    return (
        <section className={`${styles.loopSection}`} aria-labelledby="arch-loop-title">
            <h2 id="arch-loop-title" className={`${styles.loopTitle} sc-reveal`}>Autonomous Security Loop</h2>
            <p className={`${styles.loopSubtitle} sc-reveal`}>Continuous improvement cycle powering predictive + self-healing capabilities.</p>
            <div className={styles.timelineWrapper}>
                <div className={styles.timelineRow}>
                    {firstRow.map((s, idx) => {
                        const i = idx; // absolute index same for first row
                        return (
                            <button
                                key={s.title}
                                type="button"
                                onClick={() => onSelect(i)}
                                className={
                                    [
                                        styles.stepCard,
                                        i === active ? styles.active : '',
                                        visited[i] && i !== active ? styles.visited : '',
                                        'sc-reveal'
                                    ].filter(Boolean).join(' ')
                                }
                                aria-pressed={i === active}
                                aria-label={`Step ${i + 1}: ${s.title}`}
                            >
                                <div className={styles.stepBadge}>{i + 1}</div>
                                <div className={styles.stepTitle}>{s.title}</div>
                                <div className={styles.stepBody}>{s.body}</div>
                            </button>
                        );
                    })}
                </div>
                <div className={styles.connector} aria-hidden="true" />
                <div className={styles.timelineRow}>
                    {secondRow.map((s, idx) => {
                        const i = idx + firstRow.length;
                        return (
                            <button
                                key={s.title}
                                type="button"
                                onClick={() => onSelect(i)}
                                className={
                                    [
                                        styles.stepCard,
                                        i === active ? styles.active : '',
                                        visited[i] && i !== active ? styles.visited : '',
                                        'sc-reveal'
                                    ].filter(Boolean).join(' ')
                                }
                                aria-pressed={i === active}
                                aria-label={`Step ${i + 1}: ${s.title}`}
                            >
                                <div className={styles.stepBadge}>{i + 1}</div>
                                <div className={styles.stepTitle}>{s.title}</div>
                                <div className={styles.stepBody}>{s.body}</div>
                            </button>
                        );
                    })}
                </div>
            </div>
            <div className={styles.loopDetailPanel} aria-live="polite">
                {active === null ? (
                    <div className={styles.detailInner}>
                        <h3 className={styles.detailTitle}>Explore the Autonomous Loop</h3>
                        <p className={styles.detailBody}>Select any stage to see how ShieldCraft moves from raw telemetry to validated remediation with continuous learning signals reinforcing the system.</p>
                        {visited.some(v => v) && !visited.every(v => v) && (
                            <p className={styles.detailHint}>You can step through the lifecycle in any order. Completed steps dim slightly select again to re-focus.</p>
                        )}
                    </div>
                ) : (
                    <div key={active} className={`${styles.detailInner} ${styles.detailActive}`}>
                        <h3 className={styles.detailTitle}>{steps[active].title}</h3>
                        <p className={styles.detailBody}>{steps[active].body}</p>
                        <p className={styles.detailHint}>Select another stage to follow the lifecycle, or shift focus to architecture layers above.</p>
                    </div>
                )}
                {visited.every(v => v) && (
                    <div className={styles.resetRow}>
                        <button type="button" onClick={onReset} className={styles.resetBtn} aria-label="Reset lifecycle exploration">Reset</button>
                    </div>
                )}
            </div>
        </section>
    );
}
