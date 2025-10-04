import React, { useState, useEffect, useRef } from 'react';
import PortalLayout from '../components/PortalLayout';
import styles from './dashboard-simple.module.css';
import { usePortalMock } from '../context/PortalMockContext';

// Environment-specific base values for live animation
const getBaseMetrics = (env: 'dev' | 'staging' | 'prod') => {
    if (env === 'dev') {
        return {
            datalake: { used: 0.87, utilization: 43, growth: 1.2 },
            'api-latency': { p50: 145, p95: 312, errors: 0.08 },
            resources: {
                cpu: 42, memory: 55, storage: 28,
                netIn: 8, netOut: 11,
                diskRead: 6, diskWrite: 4,
                fsUsage: 35,
                load1m: 0.9, load5m: 0.7
            },
            'active-users': { current: 156, peak: 203, change: 8 },
            threats: { critical: 0, high: 1, medium: 5 },
            processing: { queue: 287, rate: 18, errors: 1 }
        };
    } else if (env === 'staging') {
        return {
            datalake: { used: 1.15, utilization: 57, growth: 1.8 },
            'api-latency': { p50: 132, p95: 295, errors: 0.04 },
            resources: {
                cpu: 58, memory: 64, storage: 38,
                netIn: 14, netOut: 17,
                diskRead: 9, diskWrite: 7,
                fsUsage: 52,
                load1m: 1.4, load5m: 1.2
            },
            'active-users': { current: 1423, peak: 1687, change: 10 },
            threats: { critical: 0, high: 2, medium: 8 },
            processing: { queue: 756, rate: 32, errors: 0 }
        };
    } else {
        // prod
        return {
            datalake: { used: 1.42, utilization: 71, growth: 2.4 },
            'api-latency': { p50: 124, p95: 287, errors: 0.02 },
            resources: {
                cpu: 65, memory: 70, storage: 45,
                netIn: 18, netOut: 22,
                diskRead: 12, diskWrite: 9,
                fsUsage: 61,
                load1m: 1.8, load5m: 1.4
            },
            'active-users': { current: 2847, peak: 3122, change: 12 },
            threats: { critical: 0, high: 3, medium: 12 },
            processing: { queue: 1234, rate: 45, errors: 0 }
        };
    }
};

// Utility functions for live updates
function randomVariation(base: number, range: number): number {
    return base + (Math.random() - 0.5) * range;
}

function clamp(value: number, min: number, max: number): number {
    return Math.max(min, Math.min(max, value));
}

function formatNumber(num: number, decimals: number = 0): string {
    return num.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// Live metrics with domain cadences plus retained history (no perpetual animation)
interface Histories {
    latencyP95: number[];
    activeUsers: number[];
    queue: number[];
    cpu: number[];
    threatsTotal: number[];
    netIn: number[];
    netOut: number[];
    diskRead: number[];
    diskWrite: number[];
    fsUsage: number[];
    load1m: number[];
}
interface LastChanged { threats: number; latency: number; resources: number; processing: number; users: number; datalake: number }
function useLiveMetrics(env: 'dev' | 'staging' | 'prod') {
    const baseMetrics = getBaseMetrics(env);
    const [metrics, setMetrics] = useState(baseMetrics);
    const targetRef = useRef(baseMetrics);
    const [histories, setHistories] = useState<Histories>({
        latencyP95: Array.from({ length: 12 }, () => baseMetrics['api-latency'].p95), // seed 1 minute @5s
        activeUsers: Array.from({ length: 12 }, () => baseMetrics['active-users'].current),
        queue: Array.from({ length: 12 }, () => baseMetrics.processing.queue),
        cpu: Array.from({ length: 12 }, () => baseMetrics.resources.cpu),
        threatsTotal: Array.from({ length: 12 }, () => baseMetrics.threats.critical + baseMetrics.threats.high + baseMetrics.threats.medium),
        netIn: Array.from({ length: 12 }, () => baseMetrics.resources.netIn),
        netOut: Array.from({ length: 12 }, () => baseMetrics.resources.netOut),
        diskRead: Array.from({ length: 12 }, () => baseMetrics.resources.diskRead),
        diskWrite: Array.from({ length: 12 }, () => baseMetrics.resources.diskWrite),
        fsUsage: Array.from({ length: 12 }, () => baseMetrics.resources.fsUsage),
        load1m: Array.from({ length: 12 }, () => baseMetrics.resources.load1m)
    });
    const lastChangedRef = useRef<LastChanged>({ threats: Date.now(), latency: Date.now(), resources: Date.now(), processing: Date.now(), users: Date.now(), datalake: Date.now() });
    const prevThreatsRef = useRef(baseMetrics.threats);

    // Reset when environment changes
    useEffect(() => {
        const newBase = getBaseMetrics(env);
        setMetrics(newBase);
        targetRef.current = newBase;
        prevThreatsRef.current = newBase.threats;
    }, [env]);
    const pushHistory = (key: keyof Histories, value: number, max = 60) => {
        setHistories(prev => {
            const newHist = { ...prev };
            const arr = [...newHist[key]];
            arr.push(value);
            if (arr.length > max) arr.splice(0, arr.length - max);
            newHist[key] = arr;
            return newHist;
        });
    };

    useEffect(() => {
        // Load histories from sessionStorage if present
        try {
            if (typeof window !== 'undefined') {
                const raw = sessionStorage.getItem('sc_histories_v1');
                if (raw) {
                    const parsed = JSON.parse(raw);
                    const newHist = { ...histories };
                    Object.keys(newHist).forEach((k) => {
                        if (Array.isArray((parsed as any)[k])) {
                            (newHist as any)[k] = (parsed as any)[k];
                        }
                    });
                    setHistories(newHist);
                }
            }
        } catch { /* ignore */ }

        const fastMode = typeof window !== 'undefined' && (new URLSearchParams(window.location.search).get('fast') === '1' || localStorage.getItem('sc-fast-demo') === '1');
        const timers: number[] = [];
        const every = (ms: number, fn: () => void) => { fn(); timers.push(window.setInterval(fn, ms)); };
        const setAndRecord = () => {
            // Ensure integer-only for count metrics & percentages rounded sensibly
            const snapshot = { ...targetRef.current } as typeof baseMetrics;
            snapshot.threats = {
                critical: Math.round(snapshot.threats.critical),
                high: Math.round(snapshot.threats.high),
                medium: Math.round(snapshot.threats.medium)
            };
            snapshot.processing = {
                queue: Math.round(snapshot.processing.queue),
                rate: Math.round(snapshot.processing.rate),
                errors: Math.round(snapshot.processing.errors)
            };
            snapshot['active-users'] = {
                current: Math.round(snapshot['active-users'].current),
                peak: Math.round(snapshot['active-users'].peak),
                change: snapshot['active-users'].change
            };
            setMetrics(snapshot);
            pushHistory('latencyP95', snapshot['api-latency'].p95);
            pushHistory('activeUsers', snapshot['active-users'].current);
            pushHistory('queue', snapshot.processing.queue);
            pushHistory('cpu', snapshot.resources.cpu);
            pushHistory('threatsTotal', snapshot.threats.critical + snapshot.threats.high + snapshot.threats.medium);
            pushHistory('netIn', snapshot.resources.netIn);
            pushHistory('netOut', snapshot.resources.netOut);
            pushHistory('diskRead', snapshot.resources.diskRead);
            pushHistory('diskWrite', snapshot.resources.diskWrite);
            pushHistory('fsUsage', snapshot.resources.fsUsage);
            pushHistory('load1m', snapshot.resources.load1m);
        };

        // Fast group (5s) for visibly changing but not jittery metrics
        every(fastMode ? 3000 : 5000, () => {
            const cur = targetRef.current;
            targetRef.current = {
                ...cur,
                'api-latency': {
                    p50: clamp(randomVariation(cur['api-latency'].p50, 1.2), 120, 128),
                    p95: clamp(randomVariation(cur['api-latency'].p95, 2.5), 282, 292),
                    errors: clamp(randomVariation(cur['api-latency'].errors, 0.0008), 0.018, 0.026)
                },
                resources: {
                    cpu: clamp(randomVariation(cur.resources.cpu, 2.5), 60, 70),
                    memory: cur.resources.memory,
                    storage: cur.resources.storage,
                    netIn: clamp(randomVariation(cur.resources.netIn, 3.5), 10, 30),
                    netOut: clamp(randomVariation(cur.resources.netOut, 3.5), 12, 34),
                    diskRead: clamp(randomVariation(cur.resources.diskRead, 2.8), 6, 18),
                    diskWrite: clamp(randomVariation(cur.resources.diskWrite, 2.8), 4, 16),
                    fsUsage: cur.resources.fsUsage,
                    load1m: clamp(randomVariation(cur.resources.load1m, 0.15), 1.0, 2.5)
                },
                processing: {
                    queue: clamp(randomVariation(cur.processing.queue, 10), 1210, 1255),
                    rate: clamp(randomVariation(cur.processing.rate, 0.8), 44, 47),
                    errors: cur.processing.errors // rare change
                },
                'active-users': {
                    current: clamp(randomVariation(cur['active-users'].current, 10), 2830, 2870),
                    peak: cur['active-users'].peak,
                    change: clamp(randomVariation(cur['active-users'].change, 0.05), 11, 13)
                }
            } as typeof baseMetrics;
            lastChangedRef.current.latency = Date.now();
            lastChangedRef.current.resources = Date.now();
            lastChangedRef.current.processing = Date.now();
            lastChangedRef.current.users = Date.now();
            setAndRecord();
        });

        // Medium cadence (15s) threats & memory
        every(fastMode ? 8000 : 15000, () => {
            const cur = targetRef.current;
            const burst = Math.random() < 0.04;
            const nextThreats = {
                critical: clamp(Math.round(randomVariation(cur.threats.critical, burst ? 1 : 0.2)), 0, 2),
                high: clamp(Math.round(randomVariation(cur.threats.high, burst ? 1.2 : 0.3)), 2, 5),
                medium: clamp(Math.round(randomVariation(cur.threats.medium, burst ? 2 : 0.4)), 10, 15)
            };
            // detect change and record timestamp
            const prev = prevThreatsRef.current;
            if (nextThreats.critical !== prev.critical || nextThreats.high !== prev.high || nextThreats.medium !== prev.medium) {
                lastChangedRef.current.threats = Date.now();
                prevThreatsRef.current = nextThreats;
            }
            targetRef.current = {
                ...cur,
                threats: nextThreats,
                resources: {
                    cpu: cur.resources.cpu,
                    memory: clamp(randomVariation(cur.resources.memory, 0.5), 68, 72),
                    storage: cur.resources.storage,
                    netIn: cur.resources.netIn,
                    netOut: cur.resources.netOut,
                    diskRead: cur.resources.diskRead,
                    diskWrite: cur.resources.diskWrite,
                    fsUsage: clamp(randomVariation(cur.resources.fsUsage, 0.4), 58, 64),
                    load1m: cur.resources.load1m
                }
            } as typeof baseMetrics;
            setAndRecord();
        });

        // Slow cadence (60s) datalake & storage & peak users
        every(fastMode ? 15000 : 60000, () => {
            const cur = targetRef.current;
            const newPeak = Math.max(cur['active-users'].peak, cur['active-users'].current);
            targetRef.current = {
                ...cur,
                datalake: {
                    used: clamp(randomVariation(cur.datalake.used, 0.004), 1.40, 1.45),
                    utilization: clamp(randomVariation(cur.datalake.utilization, 0.25), 70, 72),
                    growth: clamp(randomVariation(cur.datalake.growth, 0.03), 2.3, 2.6)
                },
                resources: {
                    cpu: cur.resources.cpu,
                    memory: cur.resources.memory,
                    storage: clamp(randomVariation(cur.resources.storage, 0.15), 44, 46),
                    netIn: cur.resources.netIn,
                    netOut: cur.resources.netOut,
                    diskRead: cur.resources.diskRead,
                    diskWrite: cur.resources.diskWrite,
                    fsUsage: cur.resources.fsUsage,
                    load1m: clamp(randomVariation(cur.resources.load1m, 0.1), 1.0, 2.5)
                },
                'active-users': { ...cur['active-users'], peak: newPeak }
            } as typeof baseMetrics;
            lastChangedRef.current.datalake = Date.now();
            setAndRecord();
        });

        return () => timers.forEach(clearInterval);
    }, []);

    // Persist histories to sessionStorage whenever they change
    useEffect(() => {
        try {
            if (typeof window !== 'undefined') {
                sessionStorage.setItem('sc_histories_v1', JSON.stringify(histories));
            }
        } catch { /* ignore */ }
    }, [histories]);

    return { metrics, histories, lastChanged: lastChangedRef.current };
}

// Card definitions for dashboard layout
const cardDefinitions = [
    { id: 'datalake', title: 'Data Lake', chartType: 'donut', status: 'healthy' },
    { id: 'api-latency', title: 'API Latency', chartType: 'line', status: 'healthy' },
    { id: 'resources', title: 'Resource Usage', chartType: 'resources', status: 'healthy' },
    { id: 'active-users', title: 'Active Users', chartType: 'area', status: 'healthy' },
    { id: 'threats', title: 'Threat Analysis', chartType: 'heatmap', status: 'healthy' },
    { id: 'processing', title: 'Processing Pipeline', chartType: 'bar', status: 'healthy' }
];

// Helper to build smooth sparkline path from array
function buildPath(values: number[], w: number, h: number) {
    if (!values.length) return '';
    const max = Math.max(...values);
    const min = Math.min(...values);
    const span = max - min || 1;
    const step = w / (values.length - 1);
    return values.map((v, i) => `${i === 0 ? 'M' : 'L'}${i * step},${h - ((v - min) / span) * h}`).join(' ');
}

// No generic streaming hook needed now; histories managed centrally

// Simple chart placeholders with live data + motion polish
function formatAgo(ts: number) {
    const s = Math.max(0, Math.floor((Date.now() - ts) / 1000));
    if (s < 60) return `${s}s ago`;
    const m = Math.floor(s / 60);
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    return `${h}h ago`;
}

function ChartPlaceholder({ type, title, liveData, histories, lastChanged }: { type: string; title: string; liveData: any; histories: Histories; lastChanged: LastChanged }) {
    const latencySeries = type === 'line' ? histories.latencyP95 : undefined;
    const usersSeries = type === 'area' ? histories.activeUsers : undefined;
    const processingSeries = type === 'bar' ? histories.queue : undefined;
    const getChartContent = () => {
        switch (type) {
            case 'donut':
                const utilization = liveData?.utilization || 71;
                const used = liveData?.used || 1.42;
                const growth = liveData?.growth || 2.4;
                return (
                    <div className={styles.progressChart}>
                        <div className={styles.datalakeStats}>
                            <div className={styles.datalakeValue}>
                                <span className={`${styles.datalakeNumber} ${styles.mono}`}>{utilization.toFixed(2)}</span>
                                <span className={styles.datalakePercent}>%</span>
                            </div>
                            <div className={styles.datalakeInfo}>
                                <div className={styles.datalakeStat}>
                                    <span className={styles.datalakeStatLabel}>Used:</span>
                                    <span className={`${styles.datalakeStatValue} ${styles.mono}`}>{used.toFixed(2)} TB</span>
                                </div>
                                <div className={styles.datalakeStat}>
                                    <span className={styles.datalakeStatLabel}>Growth:</span>
                                    <span className={`${styles.datalakeStatValue} ${styles.mono}`}>+{growth.toFixed(1)}%</span>
                                </div>
                            </div>
                        </div>
                        <div className={styles.progressBarBg}>
                            <div className={styles.progressBarFill} style={{ width: `${utilization}%` }}>
                                <div className={styles.progressBarGlow} />
                            </div>
                        </div>
                    </div>
                );
            case 'line':
                return (
                    <div className={styles.lineChart}>
                        <svg viewBox="0 0 300 120" className={styles.chartSvg} preserveAspectRatio="none">
                            {(() => {
                                const vals = latencySeries || [];
                                const max = Math.max(...vals), min = Math.min(...vals); const span = max - min || 1;
                                const slo = 300; // ms
                                const yFor = (v: number) => 110 - ((v - min) / span) * 110;
                                // gridlines
                                const gridYs = [0.2, 0.4, 0.6, 0.8].map(f => 110 * f);
                                return (
                                    <>
                                        {gridYs.map((gy, i) => (
                                            <line key={i} x1={0} x2={300} y1={gy} y2={gy} stroke="#334155" strokeOpacity={0.35} strokeWidth={0.6} />
                                        ))}
                                        <path d={buildPath(vals, 300, 110)} fill="none" stroke={vals[vals.length - 1] > slo ? '#f59e0b' : '#38bdf8'} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
                                        <line x1={0} x2={300} y1={yFor(slo)} y2={yFor(slo)} stroke="#ef4444" strokeDasharray="3 3" strokeWidth={0.8} />
                                        {/* axis ticks */}
                                        {[0, 0.5, 1].map((f, i) => {
                                            const v = min + f * (span);
                                            const y = 110 - f * 110;
                                            return <text key={`t${i}`} x={2} y={y - 2} className={`${styles.axisText} ${styles.mono}`}>{Math.round(v)}ms</text>
                                        })}
                                    </>
                                );
                            })()}
                            {latencySeries && latencySeries.length > 1 && (() => {
                                const vals = latencySeries;
                                const max = Math.max(...vals), min = Math.min(...vals); const span = max - min || 1;
                                const latest = vals[vals.length - 1];
                                const x = 300; // right edge
                                const y = 110 - ((latest - min) / span) * 110;
                                return <circle r={4} fill="#38bdf8" cx={x} cy={y} />;
                            })()}
                        </svg>
                        <div className={styles.legend}>
                            <span className={styles.legendItem} style={{ color: '#38bdf8' }}><span className={`${styles.legendSwatch}`}></span>P95</span>
                            <span className={styles.legendItem} style={{ color: '#ef4444' }}><span className={`${styles.legendSwatch} ${styles.dashed}`}></span>SLO 300ms</span>
                        </div>
                        <div className={styles.updatedBadge} aria-label="Last updated">Updated {formatAgo(lastChanged.latency)}</div>
                    </div>
                );
            case 'resources':
                const cpu = Math.round(liveData?.cpu ?? 65);
                const memory = Math.round(liveData?.memory ?? 70);
                const fsUsage = Math.round(liveData?.fsUsage ?? 61);
                const load1m = (liveData?.load1m ?? 1.6).toFixed(2);
                const netIn = (liveData?.netIn ?? 18).toFixed(1);
                const netOut = (liveData?.netOut ?? 22).toFixed(1);
                const diskRead = (liveData?.diskRead ?? 12).toFixed(1);
                const diskWrite = (liveData?.diskWrite ?? 9).toFixed(1);
                return (
                    <div className={styles.resourcesChart}>
                        <div className={styles.resourcesRow}>
                            <div className={styles.gauge}>
                                <div className={styles.gaugeLabel}>CPU</div>
                                <div className={`${styles.gaugeValue} ${styles.mono}`} title={`Updated ${formatAgo(lastChanged.resources)}`}>{cpu}%</div>
                            </div>
                            <div className={styles.gauge}>
                                <div className={styles.gaugeLabel}>RAM</div>
                                <div className={`${styles.gaugeValue} ${styles.mono}`}>{memory}%</div>
                            </div>
                            <div className={styles.gauge}>
                                <div className={styles.gaugeLabel}>FS</div>
                                <div className={`${styles.gaugeValue} ${styles.mono}`}>{fsUsage}%</div>
                            </div>
                            <div className={styles.gauge}>
                                <div className={styles.gaugeLabel}>Load</div>
                                <div className={`${styles.gaugeValue} ${styles.mono}`}>{load1m}</div>
                            </div>
                        </div>
                        <div className={styles.miniGrid}>
                            <div className={styles.miniTile}>
                                <div className={styles.miniLabel}>Net In</div>
                                <div className={`${styles.miniValue} ${styles.mono}`}>{netIn} MB/s</div>
                            </div>
                            <div className={styles.miniTile}>
                                <div className={styles.miniLabel}>Net Out</div>
                                <div className={`${styles.miniValue} ${styles.mono}`}>{netOut} MB/s</div>
                            </div>
                            <div className={styles.miniTile}>
                                <div className={styles.miniLabel}>Disk Read</div>
                                <div className={`${styles.miniValue} ${styles.mono}`}>{diskRead} MB/s</div>
                            </div>
                            <div className={styles.miniTile}>
                                <div className={styles.miniLabel}>Disk Write</div>
                                <div className={`${styles.miniValue} ${styles.mono}`}>{diskWrite} MB/s</div>
                            </div>
                        </div>
                        <svg viewBox="0 0 300 60" className={styles.chartSvg} preserveAspectRatio="none" aria-label={`Updated ${formatAgo(lastChanged.resources)}`}>
                            {(() => {
                                const vals = histories.cpu;
                                const max = Math.max(...vals), min = Math.min(...vals); const span = (max - min) || 1;
                                const yFor = (v: number) => 50 - ((v - min) / span) * 50;
                                const thr = 80; // CPU threshold
                                return (
                                    <>
                                        <path d={buildPath(vals, 300, 50)} fill="none" stroke="#22d3ee" strokeWidth={1.5} />
                                        <line x1={0} x2={300} y1={yFor(thr)} y2={yFor(thr)} stroke="#f59e0b" strokeDasharray="4 3" strokeWidth={0.8} />
                                    </>
                                );
                            })()}
                        </svg>
                        <div className={styles.legend}>
                            <span className={styles.legendItem} style={{ color: '#22d3ee' }}><span className={styles.legendSwatch}></span>CPU</span>
                            <span className={styles.legendItem} style={{ color: '#f59e0b' }}><span className={`${styles.legendSwatch} ${styles.dashed}`}></span>80% Threshold</span>
                        </div>
                    </div>
                );
            case 'area':
                return (
                    <div className={styles.areaChart}>
                        <svg viewBox="0 0 300 120" className={styles.chartSvg} preserveAspectRatio="none">
                            <defs>
                                <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                    <stop offset="0%" stopColor="#60a5fa" stopOpacity="0.30" />
                                    <stop offset="100%" stopColor="#60a5fa" stopOpacity="0" />
                                </linearGradient>
                            </defs>
                            {(() => {
                                const vals = usersSeries || [];
                                const max = Math.max(...vals), min = Math.min(...vals); const span = max - min || 1;
                                const gridYs = [0.2, 0.4, 0.6, 0.8].map(f => 100 * f);
                                return (
                                    <>
                                        {gridYs.map((gy, i) => (
                                            <line key={i} x1={0} x2={300} y1={gy} y2={gy} stroke="#334155" strokeOpacity={0.35} strokeWidth={0.6} />
                                        ))}
                                        {/* axis ticks */}
                                        {[0, 0.5, 1].map((f, i) => {
                                            const v = Math.round(min + f * (span));
                                            const y = 100 - f * 100;
                                            return <text key={`tu${i}`} x={2} y={y - 2} className={`${styles.axisText} ${styles.mono}`}>{v}</text>
                                        })}
                                    </>
                                );
                            })()}
                            <path
                                d={(() => {
                                    const p = buildPath(usersSeries || [], 300, 100);
                                    if (!p) return '';
                                    return `${p} L300,120 L0,120 Z`;
                                })()}
                                fill="url(#areaGradient)" stroke="#60a5fa" strokeWidth={2}
                            />
                            {usersSeries && usersSeries.length > 1 && (() => {
                                const vals = usersSeries;
                                const max = Math.max(...vals), min = Math.min(...vals); const span = max - min || 1;
                                const latest = vals[vals.length - 1];
                                const x = 300; const y = 100 - ((latest - min) / span) * 100;
                                return <circle r={4} fill="#60a5fa" cx={x} cy={y} />;
                            })()}
                        </svg>
                        <div className={styles.legend}>
                            <span className={styles.legendItem} style={{ color: '#60a5fa' }}><span className={styles.legendSwatch}></span>Users</span>
                        </div>
                        <div className={styles.updatedBadge}>Updated {formatAgo(lastChanged.users)}</div>
                    </div>
                );
            case 'heatmap':
                const totalThreats = liveData.critical + liveData.high + liveData.medium;
                const sevRows = [
                    { label: 'Critical', value: liveData.critical, color: '#ef4444' },
                    { label: 'High', value: liveData.high, color: '#f59e0b' },
                    { label: 'Medium', value: liveData.medium, color: '#22d3ee' }
                ];
                return (
                    <div className={styles.threatBars}>
                        <div className={styles.threatTotal}>Total: {totalThreats} • Updated {formatAgo(lastChanged.threats)}</div>
                        {sevRows.map(r => {
                            const pct = totalThreats ? (r.value / totalThreats) * 100 : 0;
                            return (
                                <div key={r.label} className={styles.threatRow} title={`Last change: ${new Date(lastChanged.threats).toLocaleString()}`}>
                                    <span className={styles.threatLabel}>{r.label}</span>
                                    <div className={styles.threatBarTrack}>
                                        <div className={styles.threatBarFill} style={{ width: `${pct}%`, background: r.color }} />
                                    </div>
                                    <span className={styles.threatValue}>{r.value}</span>
                                    <span className={styles.threatPct}>({pct.toFixed(0)}%)</span>
                                </div>
                            );
                        })}
                        <svg viewBox="0 0 300 60" className={styles.chartSvg} preserveAspectRatio="none">
                            {(() => {
                                const vals = histories.threatsTotal;
                                const max = Math.max(...vals), min = Math.min(...vals); const span = (max - min) || 1;
                                const baseline = vals.reduce((a, b) => a + b, 0) / (vals.length || 1);
                                const threshold = Math.max(5, Math.round(baseline + 2));
                                const yFor = (v: number) => 50 - ((v - min) / span) * 50;
                                return (
                                    <>
                                        <path d={buildPath(vals, 300, 50)} fill="none" stroke="#f59e0b" strokeWidth={1.5} />
                                        <line x1={0} x2={300} y1={yFor(baseline)} y2={yFor(baseline)} stroke="#64748b" strokeDasharray="4 4" strokeWidth={0.8} />
                                        <line x1={0} x2={300} y1={yFor(threshold)} y2={yFor(threshold)} stroke="#ef4444" strokeDasharray="2 3" strokeWidth={0.8} />
                                        {/* axis ticks */}
                                        {[0, 0.5, 1].map((f, i) => {
                                            const v = Math.round(min + f * (span));
                                            const y = 50 - f * 50;
                                            return <text key={`tt${i}`} x={2} y={y - 2} className={`${styles.axisText} ${styles.mono}`}>{v}</text>
                                        })}
                                    </>
                                );
                            })()}
                        </svg>
                        <div className={styles.legend}>
                            <span className={styles.legendItem} style={{ color: '#f59e0b' }}><span className={styles.legendSwatch}></span>Total</span>
                            <span className={styles.legendItem} style={{ color: '#64748b' }}><span className={`${styles.legendSwatch} ${styles.dashed}`}></span>Baseline</span>
                            <span className={styles.legendItem} style={{ color: '#ef4444' }}><span className={`${styles.legendSwatch} ${styles.dashed}`}></span>Threshold</span>
                        </div>
                    </div>
                );
            case 'bar':
                return (
                    <div className={styles.barChart}>
                        <svg viewBox="0 0 300 120" className={styles.chartSvg} preserveAspectRatio="none">
                            {(() => {
                                const arr = processingSeries || [];
                                // Use a fixed sensible max (like 1500) or 1.3x the data max for realistic scaling
                                const dataMax = Math.max(...arr);
                                const max = Math.max(1500, dataMax * 1.3);
                                const left = 24, right = 6, top = 10, bottom = 10;
                                const chartW = 300 - left - right;
                                const chartH = 110 - top;
                                // Threshold line at 1300 (80% of 1500 max)
                                const threshold = 1300;
                                return (
                                    <>
                                        {/* gridlines */}
                                        {[0.2, 0.4, 0.6, 0.8].map((f, i) => {
                                            const gy = top + chartH * f;
                                            return <line key={`g${i}`} x1={left} x2={left + chartW} y1={gy} y2={gy} stroke="#334155" strokeOpacity={0.35} strokeWidth={0.6} />
                                        })}
                                        {/* threshold line */}
                                        <line
                                            x1={left}
                                            x2={left + chartW}
                                            y1={top + chartH - (threshold / max) * chartH}
                                            y2={top + chartH - (threshold / max) * chartH}
                                            stroke="#f59e0b"
                                            strokeDasharray="4 3"
                                            strokeWidth={0.8}
                                        />
                                        {/* bars */}
                                        {arr.map((val, i) => {
                                            const barAreaW = chartW / (arr.length);
                                            const w = Math.max(6, barAreaW * 0.6);
                                            const x = left + i * barAreaW + (barAreaW - w) / 2;
                                            const h = Math.max(2, (val / max) * (chartH - bottom));
                                            const y = top + chartH - h;
                                            // Color based on threshold
                                            const color = val > threshold ? '#f59e0b' : '#60a5fa';
                                            return <rect key={i} x={x} y={y} width={w} height={h} rx={1.5} fill={color} opacity={0.85} />;
                                        })}
                                        {/* axis ticks */}
                                        {[0, 0.5, 1].map((f, i) => {
                                            const v = Math.round(max * f);
                                            const y = top + (1 - f) * chartH;
                                            return <text key={`tb${i}`} x={2} y={y - 2} className={`${styles.axisText} ${styles.mono}`}>{v}</text>
                                        })}
                                    </>
                                );
                            })()}
                        </svg>
                        <div className={styles.legend}>
                            <span className={styles.legendItem} style={{ color: '#60a5fa' }}><span className={styles.legendSwatch}></span>Queue Depth</span>
                            <span className={styles.legendItem} style={{ color: '#f59e0b' }}><span className={`${styles.legendSwatch} ${styles.dashed}`}></span>Threshold 1300</span>
                        </div>
                        <div className={styles.updatedBadge}>Updated {formatAgo(lastChanged.processing)}</div>
                    </div>
                );
            default:
                return (
                    <div className={styles.defaultChart}>
                        <div className={styles.chartPlaceholder}>
                            📊 {title} Chart
                        </div>
                    </div>
                );
        }
    };

    return <div className={styles.chartContainer}>{getChartContent()}</div>;
}

function DashboardCard({ card, liveMetrics, histories, lastChanged }: { card: any; liveMetrics: any; histories: Histories; lastChanged: LastChanged }) {
    const getLiveMetrics = () => {
        const data = liveMetrics[card.id];
        switch (card.id) {
            case 'datalake':
                return [
                    { label: 'Used', value: `${data.used.toFixed(2)} TB` },
                    { label: 'Utilization', value: `${Math.round(data.utilization)}%` },
                    { label: 'Growth', value: `+${data.growth.toFixed(1)}%` }
                ];
            case 'api-latency':
                return [
                    { label: 'P50', value: `${Math.round(data.p50)}ms` },
                    { label: 'P95', value: `${Math.round(data.p95)}ms` },
                    { label: 'Errors', value: `${data.errors.toFixed(2)}%` }
                ];
            case 'resources':
                return [
                    { label: 'CPU', value: `${Math.round(data.cpu)}%` },
                    { label: 'Memory', value: `${Math.round(data.memory)}%` },
                    { label: 'Storage', value: `${Math.round(data.storage)}%` }
                ];
            case 'active-users':
                return [
                    { label: 'Current', value: formatNumber(data.current) },
                    { label: 'Peak', value: formatNumber(data.peak) },
                    { label: '24h Change', value: `+${Math.round(data.change)}%` }
                ];
            case 'threats':
                return [
                    { label: 'Critical', value: data.critical.toString() },
                    { label: 'High', value: data.high.toString() },
                    { label: 'Medium', value: data.medium.toString() }
                ];
            case 'processing':
                return [
                    { label: 'Queue', value: formatNumber(data.queue) },
                    { label: 'Rate', value: `${data.rate}/min` },
                    { label: 'Errors', value: data.errors.toString() }
                ];
            default:
                return card.metrics;
        }
    };

    const liveMetricValues = getLiveMetrics();
    const liveData = liveMetrics[card.id];

    const status = (() => {
        if (card.id === 'threats') {
            const t = liveMetrics.threats;
            if (t.critical > 0) return 'error';
            if (t.high > 0) return 'warning';
            return 'healthy';
        }
        return card.status || 'healthy';
    })();

    const cardStatusClass = status === 'error' ? styles['cardStatus-error'] : status === 'warning' ? styles['cardStatus-warning'] : styles['cardStatus-healthy'];
    return (
        <div className={`${styles.card} ${cardStatusClass}`}>
            <div className={styles.cardHeader}>
                <h3 className={styles.cardTitle}>{card.title}</h3>
                <div className={`${styles.statusPill} ${styles[status]}`} title={card.id === 'threats' ? `Threat level: ${status}` : undefined}>{status.toUpperCase()}</div>
            </div>

            <div className={styles.metrics}>
                {liveMetricValues.map((metric) => (
                    <div key={metric.label} className={styles.metric}>
                        <div className={styles.metricLabel}>{metric.label}</div>
                        <div className={`${styles.metricValue} ${styles.mono}`}>{metric.value}</div>
                    </div>
                ))}
            </div>

            <ChartPlaceholder type={card.chartType} title={card.title} liveData={liveData} histories={histories} lastChanged={lastChanged} />
        </div>
    );
}

function DashboardContent() {
    const { env } = usePortalMock();
    const { metrics: liveMetrics, histories, lastChanged } = useLiveMetrics(env);

    return (
        <div className={styles.dashboard}>
            <header className={styles.kpiStrip} aria-label="Key performance indicators">
                <div className={styles.kpiItem}>
                    <div className={styles.kpiLabel}>
                        <span>Active Users</span>
                        <div className={styles.kpiDeltaPositive}>+{Math.round(liveMetrics['active-users'].change)}%</div>
                    </div>
                    <div className={`${styles.kpiValue} ${styles.mono}`}>{formatNumber(liveMetrics['active-users'].current)}</div>
                </div>
                <div className={styles.kpiItem}>
                    <div className={styles.kpiLabel}>
                        <span>API P95</span>
                        <div className={styles.kpiDeltaNeutral}>SLA 350ms</div>
                    </div>
                    <div className={`${styles.kpiValue} ${styles.mono}`}>{Math.round(liveMetrics['api-latency'].p95)}ms</div>
                </div>
                <div className={styles.kpiItem}>
                    <div className={styles.kpiLabel}>
                        <span>Threats (High+)</span>
                        <div className={styles.kpiDeltaWarn}>{liveMetrics.threats.critical > 0 ? 'Action' : 'Nominal'}</div>
                    </div>
                    <div className={`${styles.kpiValue} ${styles.mono}`}>{liveMetrics.threats.high + liveMetrics.threats.critical}</div>
                </div>
                <div className={styles.kpiItem}>
                    <div className={styles.kpiLabel}>
                        <span>Queue Depth</span>
                        <div className={styles.kpiDeltaNeutral}>Pipeline</div>
                    </div>
                    <div className={`${styles.kpiValue} ${styles.mono}`}>{formatNumber(liveMetrics.processing.queue)}</div>
                </div>
                <div className={styles.kpiItem}>
                    <div className={styles.kpiLabel}>
                        <span>DL Utilization</span>
                        <div className={styles.kpiDeltaPositive}>Growth {liveMetrics.datalake.growth.toFixed(1)}%</div>
                    </div>
                    <div className={`${styles.kpiValue} ${styles.mono}`}>{Math.round(liveMetrics.datalake.utilization)}%</div>
                </div>
            </header>
            <div className={styles.dashboardGrid}>
                {cardDefinitions.map((card) => (
                    <DashboardCard key={card.id} card={card} liveMetrics={liveMetrics} histories={histories} lastChanged={lastChanged} />
                ))}
            </div>
        </div>
    );
}

const Dashboard = () => {
    return (
        <PortalLayout title="Dashboard" description="ShieldCraft AI Dashboard" showSearchBar={false} showEnvSelector={false}>
            <DashboardContent />
        </PortalLayout>
    );
};

export default Dashboard;
