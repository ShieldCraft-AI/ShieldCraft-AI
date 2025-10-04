import React from 'react';
import styles from './card.module.css';

type KPI = { label: string; value: string; delta?: number };

type Props = {
    title: string;
    icon?: React.ReactNode;
    kpis?: KPI[];
    controls?: React.ReactNode;
    children: React.ReactNode;
    ariaLabel?: string;
    kpiCols?: number; // optional explicit number of KPI columns
    kpiNoWrap?: boolean; // force fixed 2-col layout without spanning
};

export default function CardShell({ title, icon, kpis, controls, children, ariaLabel, kpiCols, kpiNoWrap }: Props) {
    return (
        <section className={styles.card} aria-label={ariaLabel || title}>
            <header className={styles.header}>
                <div className={styles.titleRow}>
                    {icon}
                    <h3 className={styles.title}>{title}</h3>
                </div>
                {controls && <div className={styles.controls}>{controls}</div>}
            </header>

            {kpis && kpis.length > 0 && (
                <div
                    className={`${styles.kpiRow} ${kpiNoWrap ? styles.kpiNoWrap : ''}`}
                    style={kpiCols ? { gridTemplateColumns: `repeat(${kpiCols}, minmax(120px, 1fr))` } : undefined}
                >
                    {kpis.map((k) => (
                        <div key={k.label} className={styles.kpiItem}>
                            <div className={styles.kpiLabel}>{k.label}</div>
                            <div className={styles.kpiValue}>
                                {k.value}
                                {typeof k.delta === 'number' && (
                                    <span className={k.delta >= 0 ? styles.deltaUp : styles.deltaDown}>
                                        {k.delta >= 0 ? '▲' : '▼'} {Math.abs(k.delta).toFixed(1)}%
                                    </span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <div className={styles.chartRegion}>{children}</div>
        </section>
    );
}
