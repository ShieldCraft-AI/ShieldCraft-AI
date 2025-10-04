import React from 'react';
import PortalLayout from '../components/PortalLayout';
import styles from './monitoring.module.css';
import GlobeHUD from '@site/src/components/dashboard/GlobeHUD';
import WorldMap from '@site/src/components/dashboard/WorldMap';
import dayjs from 'dayjs';
import { usePortalMock } from '../context/PortalMockContext';

function StatusPill({ status }: { status: 'healthy' | 'warning' | 'error' }) {
    return <span className={`${styles.statusPill} ${styles[status]}`}>{status.toUpperCase()}</span>;
}

function MonitoringContent() {
    const { env } = usePortalMock();
    // Real-time alerts (paced, looks live without looping too quickly)
    type Sev = 'CRIT' | 'WARN' | 'INFO';
    type Alert = { id: number; sev: Sev; msg: string; ts: string };
    const feedRef = React.useRef<HTMLDivElement | null>(null);
    const [paused, setPaused] = React.useState(false);
    const shouldAutoScrollRef = React.useRef(true); // Track if user wants auto-scroll
    const isScrollingProgrammaticallyRef = React.useRef(false); // Track if we're scrolling programmatically
    const lastAlertIdRef = React.useRef(0); // Track last alert ID to detect new alerts
    const [alerts, setAlerts] = React.useState<Alert[]>(() => {
        const seed: Array<[Sev, string]> = [
            ['CRIT', 'Suspicious lateral movement detected in VPC-east-1a'],
            ['WARN', 'Elevated P95 latency on /ingest endpoint (312ms)'],
            ['INFO', 'Auto-scaler added 2 pods to ingestion-workers'],
            ['WARN', 'High auth failure rate from IP 185.23.7.12 (geo: DE)'],
            ['INFO', 'GuardDuty anomaly score returned to baseline'],
            ['CRIT', 'Privileged token used from anomalous ASN (AS4134)'],
            ['INFO', 'Shard rebalance complete: topic=telemetry, partitions=64'],
            ['WARN', 'S3 PutObject errors > 2% in bucket sc-datalake-logs'],
            ['INFO', 'IAM AccessAnalyzer flagged unused admin policy'],
            ['WARN', 'Egress spike detected on subnet sn-08b3a1 (x3 stddev)'],
            ['CRIT', 'Multiple failed root MFA attempts within 60s window'],
            ['INFO', 'Remediation: disabled key KMS/ci-old expired'],
            ['WARN', 'Unusual DNS request volume to rare domain *.cn'],
            ['INFO', 'Threat intel feed synced (12 new IoCs, 2 expired)'],
            ['CRIT', 'RCE signature triggered on api-gateway stage prod'],
            ['INFO', 'Glue job ETL-dedupe succeeded (dur=3m12s)'],
            ['WARN', 'WAF challenge rate increased on /login (bot wave?)'],
            ['INFO', 'SQS redrive completed for dlq-processing-queue'],
            ['WARN', 'CloudTrail gap detected (late delivery 45s)'],
            ['INFO', 'Vector store compacted: segments=3, freed=1.2GB'],
        ];
        // Backfill ~24 items with current timestamps spaced 5s apart
        const now = dayjs();
        return Array.from({ length: 24 }, (_, i) => {
            const idx = (seed.length - 1 - (i % seed.length) + seed.length) % seed.length;
            const item = seed[idx];
            return {
                id: i + 1,
                sev: item[0],
                msg: item[1],
                ts: now.subtract((24 - i) * 5, 'second').format('HH:mm'),
            } as Alert;
        });
    });

    React.useEffect(() => {
        let id = alerts.length + 1;
        const pool: Array<[Sev, string]> = [
            ['WARN', 'Unusual sequence of STS:AssumeRole in account 4242'],
            ['INFO', 'Malicious IP 45.83.12.7 auto-blocked at edge'],
            ['CRIT', 'High-sev exfil pattern detected via DNS tunneling'],
            ['INFO', 'Patch window scheduled for bastion hosts (02:00Z)'],
            ['WARN', 'KMS decrypt errors spiked for service=data-ingest'],
            ['INFO', 'New detector: credential-stuffing v2 enabled'],
            ['WARN', 'Subnet sn-12efab near bandwidth saturation (85%)'],
            ['INFO', 'Policy updated: least-privilege enforced on ETL role'],
            ['CRIT', 'Multiple beacon-like callbacks to rare domains'],
            ['INFO', 'Remediation: Quarantined EC2 i-0a99b7e (suspicious)'],
        ];
        const tick = () => {
            if (paused) return; // do not append while paused
            const next = pool[Math.floor(Math.random() * pool.length)];
            const item: Alert = { id: id++, sev: next[0], msg: next[1], ts: dayjs().format('HH:mm') };
            lastAlertIdRef.current = item.id; // Update ref to trigger scroll
            setAlerts(prev => {
                const updated = [...prev, item];
                // keep last 60
                return updated.slice(Math.max(0, updated.length - 60));
            });

            // Auto-scroll immediately after adding alert (only if should auto-scroll)
            // Use requestAnimationFrame to ensure DOM has updated
            requestAnimationFrame(() => {
                if (shouldAutoScrollRef.current && feedRef.current) {
                    isScrollingProgrammaticallyRef.current = true;
                    feedRef.current.scrollTo({ top: feedRef.current.scrollHeight, behavior: 'instant' });
                    setTimeout(() => {
                        isScrollingProgrammaticallyRef.current = false;
                    }, 50);
                }
            });
        };
        // Real-time streaming: every 1–3s for authentic live feed feel
        let timer: number | undefined;
        const schedule = () => {
            const ms = 1000 + Math.floor(Math.random() * 2000);
            timer = window.setTimeout(() => { tick(); schedule(); }, ms);
        };
        schedule();
        return () => { if (timer) clearTimeout(timer); };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [paused]);

    // Track user scroll behavior to determine if they want auto-scroll
    const handleScroll = React.useCallback(() => {
        // Ignore scroll events triggered by our own programmatic scrolling
        if (isScrollingProgrammaticallyRef.current) return;

        const el = feedRef.current;
        if (!el) return;
        const isAtBottom = el.scrollHeight - el.scrollTop - el.clientHeight <= 1;
        shouldAutoScrollRef.current = isAtBottom;
    }, []);

    // Memoize mouse handlers to prevent re-creating on every render
    const handleMouseEnter = React.useCallback(() => setPaused(true), []);
    const handleMouseLeave = React.useCallback(() => setPaused(false), []);

    // Threat Summary live data (environment-specific initial values)
    const getThreatDataForEnv = (environment: 'dev' | 'staging' | 'prod') => {
        if (environment === 'dev') {
            return {
                level: 'Nominal' as 'Critical' | 'Elevated' | 'Nominal',
                detectionRate: 97.2,
                fpRate: 0.12,
                coverage: 85,
                critical: 0,
                high: 2,
                medium: 6,
                lastUpdate: dayjs().format('HH:mm:ss'),
            };
        } else if (environment === 'staging') {
            return {
                level: 'Nominal' as 'Critical' | 'Elevated' | 'Nominal',
                detectionRate: 98.1,
                fpRate: 0.09,
                coverage: 89,
                critical: 0,
                high: 4,
                medium: 11,
                lastUpdate: dayjs().format('HH:mm:ss'),
            };
        } else {
            return {
                level: 'Elevated' as 'Critical' | 'Elevated' | 'Nominal',
                detectionRate: 98.7,
                fpRate: 0.08,
                coverage: 92,
                critical: 2,
                high: 7,
                medium: 18,
                lastUpdate: dayjs().format('HH:mm:ss'),
            };
        }
    };

    const [threatData, setThreatData] = React.useState(() => getThreatDataForEnv(env));

    // Reset threat data when environment changes
    React.useEffect(() => {
        setThreatData(getThreatDataForEnv(env));
    }, [env]);

    React.useEffect(() => {
        // Update threat metrics every 12–18s
        const tick = () => {
            setThreatData(prev => {
                const crit = Math.max(0, prev.critical + (Math.random() > 0.7 ? (Math.random() > 0.5 ? 1 : -1) : 0));
                const high = Math.max(3, Math.min(12, prev.high + (Math.random() > 0.6 ? (Math.random() > 0.5 ? 1 : -1) : 0)));
                const med = Math.max(10, Math.min(25, prev.medium + Math.floor((Math.random() - 0.5) * 3)));
                const level = crit > 0 ? 'Critical' : high > 8 ? 'Elevated' : 'Nominal';
                return {
                    ...prev,
                    level,
                    critical: crit,
                    high,
                    medium: med,
                    detectionRate: Math.max(97, Math.min(99.5, prev.detectionRate + (Math.random() - 0.5) * 0.3)),
                    fpRate: Math.max(0.05, Math.min(0.15, prev.fpRate + (Math.random() - 0.5) * 0.02)),
                    coverage: Math.max(88, Math.min(95, prev.coverage + (Math.random() - 0.5) * 1)),
                    lastUpdate: dayjs().format('HH:mm:ss'),
                };
            });
        };
        const ms = 12000 + Math.floor(Math.random() * 6000);
        const timer = window.setInterval(tick, ms);
        return () => clearInterval(timer);
    }, []);

    // Compliance Score live data with history
    const [complianceData, setComplianceData] = React.useState(() => {
        const base = 87;
        return {
            current: base,
            history: Array.from({ length: 24 }, (_, i) => base + (Math.random() - 0.5) * 4),
            target: 95,
            lastUpdate: dayjs().format('HH:mm:ss'),
        };
    });

    React.useEffect(() => {
        // Update compliance every 10–15s
        const tick = () => {
            setComplianceData(prev => {
                const newVal = Math.max(82, Math.min(94, prev.current + (Math.random() - 0.5) * 2));
                const newHistory = [...prev.history.slice(1), newVal];
                return {
                    ...prev,
                    current: newVal,
                    history: newHistory,
                    lastUpdate: dayjs().format('HH:mm'),
                };
            });
        };
        const ms = 10000 + Math.floor(Math.random() * 5000);
        const timer = window.setInterval(tick, ms);
        return () => clearInterval(timer);
    }, []);

    // Security Posture live data
    const getPostureLevel = (score: number): { level: string; status: 'healthy' | 'warning' | 'error' } => {
        if (score >= 90) return { level: 'Fortified', status: 'healthy' };
        if (score >= 80) return { level: 'Secure', status: 'healthy' };
        if (score >= 70) return { level: 'Protected', status: 'warning' };
        if (score >= 60) return { level: 'At Risk', status: 'warning' };
        if (score >= 50) return { level: 'Vulnerable', status: 'error' };
        return { level: 'Critical', status: 'error' };
    };

    const [securityPosture, setSecurityPosture] = React.useState(() => {
        const base = 82;
        return {
            current: base,
            lastUpdate: dayjs().format('HH:mm:ss'),
        };
    });

    React.useEffect(() => {
        // Update security posture every 12–18s
        const tick = () => {
            setSecurityPosture(prev => {
                const newVal = Math.max(50, Math.min(95, prev.current + (Math.random() - 0.5) * 3));
                return {
                    current: newVal,
                    lastUpdate: dayjs().format('HH:mm'),
                };
            });
        };
        const ms = 12000 + Math.floor(Math.random() * 6000);
        const timer = window.setInterval(tick, ms);
        return () => clearInterval(timer);
    }, []);

    // Security Domains live data
    type DomainStatus = 'healthy' | 'warning' | 'error';
    type Domain = { name: string; status: DomainStatus; metric: string; metricLabel: string };
    const [domains, setDomains] = React.useState<Domain[]>([
        { name: 'Endpoint', status: 'healthy', metric: '98.2%', metricLabel: 'Coverage' },
        { name: 'Network', status: 'healthy', metric: '99.1%', metricLabel: 'Monitored' },
        { name: 'Identity', status: 'warning', metric: '3', metricLabel: 'Alerts' },
        { name: 'Email', status: 'healthy', metric: '99.8%', metricLabel: 'Scanned' },
        { name: 'SaaS', status: 'healthy', metric: '47', metricLabel: 'Apps' },
        { name: 'DLP', status: 'healthy', metric: '0', metricLabel: 'Incidents' },
    ]);

    React.useEffect(() => {
        // Update domains every 25–40s for realistic live updates
        const tick = () => {
            setDomains(prev => prev.map(d => {
                // Occasionally change status (rare, represents real issues)
                if (Math.random() > 0.92) {
                    const statuses: DomainStatus[] = ['healthy', 'healthy', 'healthy', 'warning'];
                    return { ...d, status: statuses[Math.floor(Math.random() * statuses.length)] };
                }

                // Update percentage-based metrics with slight drift
                if (d.metricLabel === 'Coverage' && Math.random() > 0.7) {
                    const current = parseFloat(d.metric);
                    const drift = (Math.random() - 0.5) * 0.3;
                    const newVal = Math.max(95, Math.min(99.9, current + drift));
                    return { ...d, metric: newVal.toFixed(1) + '%' };
                }

                if (d.metricLabel === 'Monitored' && Math.random() > 0.75) {
                    const current = parseFloat(d.metric);
                    const drift = (Math.random() - 0.5) * 0.2;
                    const newVal = Math.max(97, Math.min(99.9, current + drift));
                    return { ...d, metric: newVal.toFixed(1) + '%' };
                }

                if (d.metricLabel === 'Scanned' && Math.random() > 0.8) {
                    const current = parseFloat(d.metric);
                    const drift = (Math.random() - 0.5) * 0.15;
                    const newVal = Math.max(98, Math.min(99.9, current + drift));
                    return { ...d, metric: newVal.toFixed(1) + '%' };
                }

                // Update count-based metrics
                if (d.name === 'Identity' && Math.random() > 0.65) {
                    const alerts = Math.max(0, parseInt(d.metric) + (Math.random() > 0.5 ? 1 : -1));
                    return { ...d, metric: alerts.toString(), status: alerts > 5 ? 'warning' : 'healthy' };
                }

                if (d.name === 'DLP' && Math.random() > 0.7) {
                    const incidents = Math.max(0, parseInt(d.metric) + (Math.random() > 0.6 ? 1 : 0));
                    return { ...d, metric: incidents.toString(), status: incidents > 0 ? 'warning' : 'healthy' };
                }

                if (d.name === 'SaaS' && Math.random() > 0.85) {
                    const apps = Math.max(40, Math.min(55, parseInt(d.metric) + (Math.random() > 0.5 ? 1 : -1)));
                    return { ...d, metric: apps.toString() };
                }

                return d;
            }));
        };
        const ms = 25000 + Math.floor(Math.random() * 15000);
        const timer = window.setInterval(tick, ms);
        return () => clearInterval(timer);
    }, []);

    // World Incidents live data
    type IncidentSeverity = 'critical' | 'high' | 'medium';
    type Incident = { id: number; location: string; lat: number; lon: number; severity: IncidentSeverity; description: string; timestamp: string };
    const [incidents, setIncidents] = React.useState<Incident[]>(() => [
        { id: 1, location: 'US-East', lat: 40, lon: -75, severity: 'critical', description: 'DDoS attack detected: 2.4Gbps', timestamp: dayjs().subtract(5, 'minute').format('HH:mm') },
        { id: 2, location: 'EU-West', lat: 52, lon: 5, severity: 'high', description: 'Unauthorized access attempts: 847', timestamp: dayjs().subtract(12, 'minute').format('HH:mm') },
        { id: 3, location: 'AP-South', lat: 19, lon: 77, severity: 'medium', description: 'Anomalous traffic pattern detected', timestamp: dayjs().subtract(8, 'minute').format('HH:mm') },
        { id: 4, location: 'SA-East', lat: -23, lon: -46, severity: 'high', description: 'Credential stuffing: 1.2K attempts', timestamp: dayjs().subtract(3, 'minute').format('HH:mm') },
        { id: 5, location: 'AP-East', lat: 35, lon: 139, severity: 'medium', description: 'Elevated malware signatures', timestamp: dayjs().subtract(15, 'minute').format('HH:mm') },
    ]);
    const [hoveredIncident, setHoveredIncident] = React.useState<number | null>(null);

    React.useEffect(() => {
        // Update incidents every 15–25s
        const tick = () => {
            setIncidents(prev => {
                const descriptions = [
                    'DDoS attack detected',
                    'Unauthorized access attempts',
                    'SQL injection blocked',
                    'Credential stuffing attack',
                    'Anomalous traffic pattern',
                    'Malware signatures detected',
                    'Brute force login attempts',
                    'Zero-day exploit attempt',
                    'Data exfiltration blocked',
                    'Suspicious API usage'
                ];

                // Randomly add or remove incidents
                if (prev.length < 8 && Math.random() > 0.5) {
                    const locations = [
                        { location: 'US-West', lat: 37, lon: -122 },
                        { location: 'EU-North', lat: 59, lon: 18 },
                        { location: 'ME-Central', lat: 25, lon: 55 },
                        { location: 'AF-South', lat: -34, lon: 18 },
                        { location: 'AP-SE', lat: 1, lon: 103 },
                    ];
                    const loc = locations[Math.floor(Math.random() * locations.length)];
                    const severities: IncidentSeverity[] = ['critical', 'high', 'high', 'medium', 'medium'];
                    const desc = descriptions[Math.floor(Math.random() * descriptions.length)];
                    return [...prev, {
                        id: Date.now(),
                        ...loc,
                        severity: severities[Math.floor(Math.random() * severities.length)],
                        description: desc,
                        timestamp: dayjs().format('HH:mm'),
                    }];
                } else if (prev.length > 3 && Math.random() > 0.6) {
                    // Remove random incident
                    return prev.filter((_, i) => i !== Math.floor(Math.random() * prev.length));
                }
                return prev;
            });
        };
        const ms = 15000 + Math.floor(Math.random() * 10000);
        const timer = window.setInterval(tick, ms);
        return () => clearInterval(timer);
    }, []);

    // Defense Layers live data
    type LayerStatus = 'active' | 'partial' | 'offline';
    type DefenseLayer = { id: number; name: string; status: LayerStatus; coverage: number };
    const [defenseLayers, setDefenseLayers] = React.useState<DefenseLayer[]>([
        { id: 1, name: 'Perimeter', status: 'active', coverage: 98 },
        { id: 2, name: 'Network', status: 'active', coverage: 95 },
        { id: 3, name: 'Application', status: 'active', coverage: 92 },
        { id: 4, name: 'Data', status: 'partial', coverage: 87 },
        { id: 5, name: 'Endpoint', status: 'active', coverage: 94 },
        { id: 6, name: 'Identity', status: 'active', coverage: 96 },
    ]);
    const [hoveredLayer, setHoveredLayer] = React.useState<string | null>(null);

    React.useEffect(() => {
        // Update defense layers every 15–20s
        const tick = () => {
            setDefenseLayers(prev => prev.map(layer => {
                // Occasionally change status
                if (Math.random() > 0.9) {
                    const statuses: LayerStatus[] = ['active', 'active', 'active', 'partial'];
                    const newStatus = statuses[Math.floor(Math.random() * statuses.length)];
                    return {
                        ...layer,
                        status: newStatus,
                        coverage: newStatus === 'active' ? Math.min(98, layer.coverage + 2) : Math.max(85, layer.coverage - 3),
                    };
                }
                // Slight coverage drift
                if (Math.random() > 0.7) {
                    return {
                        ...layer,
                        coverage: Math.max(85, Math.min(98, layer.coverage + (Math.random() - 0.5) * 2)),
                    };
                }
                return layer;
            }));
        };
        const ms = 15000 + Math.floor(Math.random() * 5000);
        const timer = window.setInterval(tick, ms);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className={styles.container}>
            {/* Column 1: three rows */}
            <section className={`${styles.col} ${styles.colLeft}`} aria-label="Left column">
                <article className={styles.card} aria-label="Threat summary">
                    <header className={styles.cardHeader}>
                        <h3 className={styles.cardTitle}>Threat Summary</h3>
                        <StatusPill status={threatData.level === 'Critical' ? 'error' : threatData.level === 'Elevated' ? 'warning' : 'healthy'} />
                    </header>
                    <div className={styles.threatBanner}>
                        <span className="label">Threat Level</span>
                        <span className={`${styles.mono} value`}>{threatData.level.toUpperCase()}</span>
                    </div>
                    <div className={styles.threatKPIs}>
                        <div className={styles.threatKpi}>
                            <div className={styles.threatKpiLabel}>Detection</div>
                            <div className={`${styles.threatKpiValue} ${styles.mono}`}>{threatData.detectionRate.toFixed(1)}%</div>
                        </div>
                        <div className={styles.threatKpi}>
                            <div className={styles.threatKpiLabel}>False +</div>
                            <div className={`${styles.threatKpiValue} ${styles.mono}`}>{threatData.fpRate.toFixed(2)}%</div>
                        </div>
                        <div className={styles.threatKpi}>
                            <div className={styles.threatKpiLabel}>Coverage</div>
                            <div className={`${styles.threatKpiValue} ${styles.mono}`}>{Math.round(threatData.coverage)}%</div>
                        </div>
                    </div>
                    <div className={styles.severityRow}>
                        <span className={`${styles.sevChip} ${styles.sevCrit}`}><span className={styles.sevDot} /><span className={styles.mono}>{threatData.critical}</span> Critical</span>
                        <span className={`${styles.sevChip} ${styles.sevHigh}`}><span className={styles.sevDot} /><span className={styles.mono}>{threatData.high}</span> High</span>
                        <span className={`${styles.sevChip} ${styles.sevMed}`}><span className={styles.sevDot} /><span className={styles.mono}>{threatData.medium}</span> Medium</span>
                    </div>
                    <div className={styles.metaStrip}>
                        <span>Updated {threatData.lastUpdate}</span>
                        <span>24h window</span>
                    </div>
                </article>

                <article className={styles.card} aria-label="Security domains">
                    <header className={styles.cardHeader}>
                        <h3 className={styles.cardTitle}>Security Domains</h3>
                        <StatusPill status={domains.some(d => d.status === 'error') ? 'error' : domains.some(d => d.status === 'warning') ? 'warning' : 'healthy'} />
                    </header>
                    <div className={styles.domainsGrid}>
                        {domains.map((d) => (
                            <div key={d.name} className={`${styles.domainTile} ${styles[d.status]}`}>
                                <div className={styles.domainHeader}>
                                    <span className={styles.domainName}>{d.name}</span>
                                    <span className={`${styles.domainStatus} ${styles[d.status]}`}>{d.status === 'healthy' ? '✓' : d.status === 'warning' ? '⚠' : '✕'}</span>
                                </div>
                                <div>
                                    <div className={styles.threatKpiLabel}>{d.metricLabel}</div>
                                    <div className={`${styles.domainMetric} ${styles.mono}`}>{d.metric}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </article>
            </section>

            {/* Column 2: globe + compliance */}
            <section className={`${styles.col} ${styles.colCenter}`} aria-label="Center globe">
                <article className={styles.card}>
                    <div className={styles.globeWrap}>
                        <GlobeHUD className={styles.globe} />
                    </div>
                </article>

                <article className={styles.compliancePostureRow} aria-label="Compliance and Security">
                    {/* Compliance Rating - Left Half */}
                    <div className={styles.complianceHalf}>
                        <header className={styles.cardHeader}>
                            <h3>Compliance Rating</h3>
                            <StatusPill status={complianceData.current >= 90 ? 'healthy' : complianceData.current >= 85 ? 'warning' : 'error'} />
                        </header>
                        <div className={styles.complianceContainer}>
                            <div className={styles.complianceStats}>
                                <div className={styles.complianceValue}>
                                    <span className={`${styles.mono} ${styles.complianceNumber}`}>{Math.round(complianceData.current)}</span>
                                    <span className={styles.compliancePercent}>%</span>
                                </div>
                                <div className={styles.complianceTarget}>
                                    TARGET: {complianceData.target}%
                                </div>
                            </div>
                            <div className={styles.progressBarContainer}>
                                <div className={styles.progressBarBg}>
                                    <div
                                        className={styles.progressBarFill}
                                        style={{ width: `${complianceData.current}%` }}
                                    >
                                        <div className={styles.progressBarGlow}></div>
                                    </div>
                                    <div
                                        className={styles.progressBarTarget}
                                        style={{ left: `${complianceData.target}%` }}
                                    >
                                        <div className={styles.targetMarker}></div>
                                    </div>
                                </div>
                                <div className={styles.progressLabels}>
                                    <span className={styles.mono}>0%</span>
                                    <span className={styles.mono}>50%</span>
                                    <span className={styles.mono}>100%</span>
                                </div>
                            </div>
                            <div className={styles.metaStrip}>
                                <span>Updated {complianceData.lastUpdate}</span>
                                <span>Last 2h</span>
                            </div>
                        </div>
                    </div>

                    {/* Security Posture - Right Half */}
                    <div className={styles.postureHalf}>
                        <header className={styles.cardHeader}>
                            <h3>Security Posture</h3>
                            <StatusPill status={getPostureLevel(securityPosture.current).status} />
                        </header>
                        <div className={styles.complianceContainer}>
                            <div className={styles.complianceStats}>
                                <div className={styles.complianceValue}>
                                    <span className={`${styles.mono} ${styles.complianceNumber}`}>{Math.round(securityPosture.current)}</span>
                                    <span className={styles.compliancePercent}>%</span>
                                </div>
                                <div className={styles.postureLevel} data-status={getPostureLevel(securityPosture.current).status}>
                                    {getPostureLevel(securityPosture.current).level.toUpperCase()}
                                </div>
                            </div>
                            <div className={styles.progressBarContainer}>
                                <div className={styles.progressBarBg}>
                                    <div
                                        className={styles.progressBarFill}
                                        style={{ width: `${securityPosture.current}%` }}
                                        data-posture-status={getPostureLevel(securityPosture.current).status}
                                    >
                                        <div className={styles.progressBarGlow}></div>
                                    </div>
                                </div>
                                <div className={styles.progressLabels}>
                                    <span className={styles.mono}>0%</span>
                                    <span className={styles.mono}>50%</span>
                                    <span className={styles.mono}>100%</span>
                                </div>
                            </div>
                            <div className={styles.metaStrip}>
                                <span>Updated {securityPosture.lastUpdate}</span>
                                <span>Aggregate</span>
                            </div>
                        </div>
                    </div>
                </article>
            </section>

            {/* Column 3: three rows */}
            <section className={`${styles.col} ${styles.colRight}`} aria-label="Right column">
                <article className={styles.card} aria-label="World incidents">
                    <header className={styles.cardHeader}>
                        <h3 className={styles.cardTitle}>World Incidents</h3>
                        <StatusPill status={incidents.some(i => i.severity === 'critical') ? 'error' : incidents.some(i => i.severity === 'high') ? 'warning' : 'healthy'} />
                    </header>
                    <div className={styles.worldMini}>
                        <WorldMap
                            incidents={incidents}
                            width={400}
                            height={220}
                            hoveredIncident={hoveredIncident}
                            onIncidentHover={setHoveredIncident}
                        />
                    </div>
                </article>

                <article className={styles.card} aria-label="Real-time alerts feed">
                    <header className={styles.cardHeader}>
                        <h3 className={styles.cardTitle}>Real-time Alerts</h3>
                        <StatusPill status="error" />
                    </header>
                    <div
                        className={styles.logFeed}
                        ref={feedRef}
                        role="log"
                        aria-live="polite"
                        onMouseEnter={handleMouseEnter}
                        onMouseLeave={handleMouseLeave}
                        onScroll={handleScroll}
                    >
                        {alerts.map((a) => (
                            <div key={a.id} className={styles.logItem}>
                                <span className={`${styles.mono}`} style={{ color: 'var(--hud-text-dim)' }}>[{a.ts}]</span>
                                <span className={`${a.sev === 'CRIT' ? styles.sevCrit : a.sev === 'WARN' ? styles.sevWarn : styles.sevInfo} ${styles.mono}`}>[{a.sev}]</span>
                                <span>{a.msg}</span>
                            </div>
                        ))}
                    </div>
                </article>

                <article className={styles.card} aria-label="Defense layers">
                    <header className={styles.cardHeader}>
                        <h3 className={styles.cardTitle}>Defense Layers</h3>
                        <StatusPill status={defenseLayers.some(l => l.status === 'offline') ? 'error' : defenseLayers.some(l => l.status === 'partial') ? 'warning' : 'healthy'} />
                    </header>
                    <div className={styles.defenseTopology}>
                        <svg viewBox="0 0 240 200" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">
                            <defs>
                                <filter id="hexGlow">
                                    <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                                    <feMerge>
                                        <feMergeNode in="coloredBlur" />
                                        <feMergeNode in="SourceGraphic" />
                                    </feMerge>
                                </filter>
                            </defs>
                            {/* Center hex (core) */}
                            <g transform="translate(120, 100)" className={styles.defenseCore}>
                                <title>Core Security: Central threat intelligence and orchestration hub</title>
                                <polygon
                                    points="0,-26 22.5,-13 22.5,13 0,26 -22.5,13 -22.5,-13"
                                    fill="rgba(34,211,238,0.15)"
                                    stroke="var(--hud-accent)"
                                    strokeWidth="2.5"
                                    className={styles.defenseHex}
                                />
                                <text x="0" y="5" textAnchor="middle" fontSize="12" fill="var(--hud-accent)" fontWeight="700">CORE</text>
                            </g>
                            {/* Surrounding layer hexagons */}
                            {defenseLayers.map((layer, i) => {
                                const angle = (i / defenseLayers.length) * 2 * Math.PI - Math.PI / 2;
                                const radius = 70;
                                const x = 120 + radius * Math.cos(angle);
                                const y = 100 + radius * Math.sin(angle);
                                const statusColor = layer.status === 'active' ? 'var(--hud-ok)' : layer.status === 'partial' ? 'var(--hud-warn)' : 'var(--hud-crit)';

                                // Tooltip content for each layer
                                const tooltips: Record<string, string> = {
                                    'Perimeter': 'Edge protection: WAF, DDoS mitigation, and border gateway filtering',
                                    'Network': 'Traffic inspection: IDS/IPS, flow analysis, and microsegmentation',
                                    'Application': 'Runtime protection: RASP, API security, and input validation',
                                    'Data': 'Information security: Encryption, DLP, and access auditing',
                                    'Endpoint': 'Device security: EDR, anti-malware, and behavioral analysis',
                                    'Identity': 'Access control: MFA, zero trust, and privilege management'
                                };

                                return (
                                    <g
                                        key={layer.id}
                                        transform={`translate(${x}, ${y})`}
                                        className={styles.defenseLayer}
                                        onMouseEnter={() => setHoveredLayer(layer.name)}
                                        onMouseLeave={() => setHoveredLayer(null)}
                                    >
                                        <polygon
                                            points="0,-28 24,-14 24,14 0,28 -24,14 -24,-14"
                                            fill={layer.status === 'active' ? 'rgba(34,197,94,0.08)' : layer.status === 'partial' ? 'rgba(245,158,11,0.08)' : 'rgba(239,68,68,0.08)'}
                                            stroke={statusColor}
                                            strokeWidth="1.8"
                                            className={styles.defenseHex}
                                        />
                                        {/* Connection line to center */}
                                        <line x1="0" y1="0" x2={120 - x} y2={100 - y} stroke="rgba(148,163,184,0.15)" strokeWidth="0.8" strokeDasharray="3,2" />
                                        <text x="0" y="-10" textAnchor="middle" fontSize="6.5" fill={statusColor} fontWeight="600" letterSpacing="0.3">{layer.name.toUpperCase()}</text>
                                        <text x="0" y="7" textAnchor="middle" fontSize="13" fill={statusColor} fontWeight="700">{Math.round(layer.coverage)}%</text>
                                        <text x="0" y="16" textAnchor="middle" fontSize="6" fill="var(--hud-text-dim)" opacity="0.7">{layer.status.toUpperCase()}</text>
                                    </g>
                                );
                            })}
                        </svg>
                        {hoveredLayer && (
                            <div className={styles.defenseTooltip}>
                                {(() => {
                                    const tooltips: Record<string, string> = {
                                        'Perimeter': 'Edge protection: WAF, DDoS mitigation, and border gateway filtering',
                                        'Network': 'Traffic inspection: IDS/IPS, flow analysis, and microsegmentation',
                                        'Application': 'Runtime protection: RASP, API security, and input validation',
                                        'Data': 'Information security: Encryption, DLP, and access auditing',
                                        'Endpoint': 'Device security: EDR, anti-malware, and behavioral analysis',
                                        'Identity': 'Access control: MFA, zero trust, and privilege management'
                                    };
                                    return tooltips[hoveredLayer] || `${hoveredLayer} security layer`;
                                })()}
                            </div>
                        )}
                    </div>
                </article>
            </section>
        </div>
    );
}

export default function MonitoringPage() {
    return (
        <PortalLayout title="Monitoring" description="Mission-control monitoring view" showSearchBar={false} showEnvSelector={false}>
            <MonitoringContent />
        </PortalLayout>
    );
}
