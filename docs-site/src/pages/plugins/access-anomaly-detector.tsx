import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import { useEffect, useMemo } from 'react';
import detailStyles from './plugin-detail.module.css';
import { getPluginById } from '@site/src/data/plugins/config';

const plugin = getPluginById('access-anomaly-detector');

if (!plugin) {
    throw new Error('Plugin configuration for access-anomaly-detector is missing.');
}

const PIPELINE_STAGES: Array<{ label: string; detail: string }> = [
    {
        label: 'Log ingestion + tokenisation',
        detail: 'Step Functions flow batches CloudTrail, Okta, and custom SaaS logs into Glue jobs that scrub secrets and prep entities for embedding.',
    },
    {
        label: 'Entity graph + risk scoring',
        detail: 'Named entities join with IAM identity centre data; graph edges track device posture, location, and approval lineage before an anomaly score ships.',
    },
    {
        label: 'Compliance export',
        detail: 'Detections publish into Security Hub + ServiceNow with justifications, reviewer links, and retention policies suited for audits.',
    },
];

const CONTROL_LIST: string[] = [
    'VPC-only inference path with cross-account IAM roles and customer-managed KMS keys.',
    'Secrets Manager backed rotation for API keys and embedding access tokens.',
    'Automated evidence bundle that snapshots enrichment context for every high-severity alert.',
];

const RESPONSE_RUNBOOKS: Array<{ heading: string; copy: string; bullets: string[] }> = [
    {
        heading: 'Containment channel',
        copy: 'EventBridge routes anomalies into Slack / Teams with just the evidence needed to accelerate approvals.',
        bullets: [
            'Dynamic access forms pre-populated with entity context and historic reviewer notes.',
            'Escalation policy integrates PagerDuty for privileged identity violations.',
        ],
    },
    {
        heading: 'Auditor workflow',
        copy: 'Exports package annotations, analyst decisions, and KMS audit logs into immutable S3 buckets.',
        bullets: [
            'Lifecycle policies ensure retention windows for SOX / GDPR compliance.',
            'QuickSight dashboards highlight anomaly trends for quarterly reviews.',
        ],
    },
];

const ANOMALY_POINTS: Array<{ label: string; baseline: number; detector: number }> = [
    { label: '00:00', baseline: 0.08, detector: 0.11 },
    { label: '01:00', baseline: 0.09, detector: 0.13 },
    { label: '02:00', baseline: 0.1, detector: 0.18 },
    { label: '03:00', baseline: 0.11, detector: 0.24 },
    { label: '04:00', baseline: 0.12, detector: 0.29 },
    { label: '05:00', baseline: 0.1, detector: 0.21 },
    { label: '06:00', baseline: 0.09, detector: 0.16 },
    { label: '07:00', baseline: 0.11, detector: 0.31 },
    { label: '08:00', baseline: 0.12, detector: 0.34 },
    { label: '09:00', baseline: 0.1, detector: 0.17 },
];

const ANOMALY_THRESHOLD = 0.25;

const DETECTION_METRICS: Array<{ label: string; value: string; detail: string }> = [
    { label: 'Precision @ alert', value: '93%', detail: 'Entity graph enrichment slashes false positives against privileged access spikes.' },
    { label: 'Mean time to contain', value: '7 min', detail: 'EventBridge-driven Slack/PagerDuty workflow pre-populates reviewers with context and policy lineage.' },
    { label: 'Evidence completeness', value: '100%', detail: 'Every alert packages IAM approvals, device posture, and KMS audit logs for quarterly reviews.' },
];

const DETECTION_AUTOMATIONS: string[] = [
    'Graph embeddings retrain nightly with drift diffs published to Security Hub before promotion.',
    'High-severity anomalies spawn immutable evidence bundles in KMS-encrypted buckets with lifecycle policies.',
    'Service Control Policy checks block IAM rollouts that lack regression results from the anomaly detector.',
];

export default function AccessAnomalyDetectorPage() {
    useEffect(() => {
        if (typeof document === 'undefined') return () => undefined;
        document.body.classList.add('aurora-surface');
        return () => {
            document.body.classList.remove('aurora-surface');
        };
    }, []);

    const chart = useMemo(() => {
        const width = 560;
        const height = 280;
        const margin = { top: 28, right: 32, bottom: 48, left: 64 };
        const allValues = [...ANOMALY_POINTS.flatMap(point => [point.baseline, point.detector]), ANOMALY_THRESHOLD];
        const minValue = Math.max(Math.min(...allValues) - 0.05, 0);
        const maxValue = Math.min(Math.max(...allValues) + 0.08, 1);
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        const xForIndex = (index: number) => {
            if (ANOMALY_POINTS.length === 1) {
                return margin.left + innerWidth / 2;
            }
            return margin.left + (index / (ANOMALY_POINTS.length - 1)) * innerWidth;
        };

        const yForValue = (value: number) => {
            const ratio = (value - minValue) / (maxValue - minValue);
            return height - margin.bottom - ratio * innerHeight;
        };

        const coordsToPath = (coords: Array<{ x: number; y: number }>) => coords
            .map((coord, index) => `${index === 0 ? 'M' : 'L'}${coord.x},${coord.y}`)
            .join(' ');

        const baselineCoords: Array<{ x: number; y: number }> = [];
        const detectorCoords: Array<{ x: number; y: number }> = [];

        ANOMALY_POINTS.forEach((point, index) => {
            const x = xForIndex(index);
            baselineCoords.push({ x, y: yForValue(point.baseline) });
            detectorCoords.push({ x, y: yForValue(point.detector) });
        });

        const riskAreaCoords = [...detectorCoords, ...baselineCoords.slice().reverse()];
        const riskAreaPath = `${coordsToPath(riskAreaCoords)} Z`;
        const baselinePath = coordsToPath(baselineCoords);
        const detectorPath = coordsToPath(detectorCoords);

        const axisTicks = ANOMALY_POINTS.map((point, index) => ({ x: xForIndex(index), label: point.label }));
        const tickCount = 5;
        const valueTicks = Array.from({ length: tickCount }, (_, idx) => {
            const value = minValue + ((maxValue - minValue) / (tickCount - 1)) * idx;
            return { value, y: yForValue(value) };
        });

        return {
            width,
            height,
            margin,
            riskAreaPath,
            baselinePath,
            detectorPath,
            axisTicks,
            valueTicks,
            baselineDots: ANOMALY_POINTS.map((point, index) => ({ label: point.label, x: baselineCoords[index].x, y: baselineCoords[index].y })),
            detectorDots: ANOMALY_POINTS.map((point, index) => ({ label: point.label, x: detectorCoords[index].x, y: detectorCoords[index].y, score: point.detector })),
            thresholdY: yForValue(ANOMALY_THRESHOLD),
        };
    }, []);

    return (
        <Layout title={plugin.name} description={plugin.tagline}>
            <div className={detailStyles.pageWrapper}>
                <div className={detailStyles.inner}>
                    <section className={detailStyles.hero} data-tone={plugin.tone}>
                        <div className={detailStyles.breadcrumbs}>
                            <Link to="/plugins">Plugins</Link>
                            <span aria-hidden>·</span>
                            <span>{plugin.name}</span>
                        </div>
                        <span className={detailStyles.heroTaskBadge} data-tone={plugin.tone}>ML Task · {plugin.taskType}</span>
                        <h1 className={detailStyles.heroTitle}>{plugin.name} reference implementation</h1>
                        <p className={detailStyles.heroTagline}>{plugin.tagline}</p>
                        <div className={detailStyles.chipRow}>
                            {plugin.chips.map(chip => (
                                chip.href ? (
                                    <Link key={chip.label} to={chip.href} className={detailStyles.chip} data-tone={chip.tone}>
                                        {chip.label}
                                    </Link>
                                ) : (
                                    <span key={chip.label} className={detailStyles.chip} data-tone={chip.tone}>
                                        {chip.label}
                                    </span>
                                )
                            ))}
                        </div>
                        <div className={detailStyles.heroMetaRow}>
                            <div className={detailStyles.heroPrice}>
                                <span className={detailStyles.heroPriceLabel}>Platform fee</span>
                                <span className={detailStyles.heroPriceValue}>{plugin.price}</span>
                            </div>
                        </div>
                        <div className={detailStyles.statGrid}>
                            {plugin.stats.map(stat => (
                                <div key={stat.label} className={detailStyles.statCard}>
                                    <span className={detailStyles.statLabel}>{stat.label}</span>
                                    <span className={detailStyles.statValue}>{stat.value}</span>
                                    <span className={detailStyles.statDetail}>{stat.detail}</span>
                                </div>
                            ))}
                        </div>
                    </section>

                    <section className={detailStyles.visualSection} aria-label="Entity anomaly telemetry and guardrails">
                        <article className={`${detailStyles.contentCard} ${detailStyles.vizCard}`} data-tone={plugin.tone}>
                            <div className={detailStyles.vizHeader}>
                                <h2 className={detailStyles.vizTitle}>Anomaly score vs. entity baseline</h2>
                                <p className={detailStyles.vizSubtitle}>
                                    Named-entity recognition and graph context surface risky access spikes. You can show interviewers how anomaly scores stay explainable against learned baselines and alert thresholds.
                                </p>
                            </div>
                            <svg
                                className={detailStyles.chartSvg}
                                viewBox={`0 0 ${chart.width} ${chart.height}`}
                                role="img"
                                aria-labelledby="anomaly-score-chart"
                            >
                                <title id="anomaly-score-chart">Anomaly detector score versus entity baseline and alert threshold</title>
                                <defs>
                                    <linearGradient id="anomalyRiskGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                        <stop offset="0%" stopColor="rgba(249, 115, 22, 0.28)" />
                                        <stop offset="100%" stopColor="rgba(234, 179, 8, 0.08)" />
                                    </linearGradient>
                                </defs>
                                <path d={chart.riskAreaPath} fill="url(#anomalyRiskGradient)" opacity={0.92} />
                                <path d={chart.detectorPath} fill="none" strokeWidth={3} strokeLinecap="round" style={{ stroke: 'var(--viz-line-primary)' }} />
                                <path d={chart.baselinePath} fill="none" strokeWidth={2.4} strokeDasharray="6 4" strokeLinecap="round" style={{ stroke: 'var(--viz-line-secondary)' }} />
                                {chart.detectorDots.map(dot => (
                                    <circle
                                        key={`detector-${dot.label}`}
                                        cx={dot.x}
                                        cy={dot.y}
                                        r={dot.score >= ANOMALY_THRESHOLD ? 6 : 4.2}
                                        fill={dot.score >= ANOMALY_THRESHOLD ? '#f97316' : '#fb923c'}
                                        stroke="#7f1d1d"
                                        strokeWidth={dot.score >= ANOMALY_THRESHOLD ? 1.8 : 1.2}
                                    />
                                ))}
                                {chart.baselineDots.map(dot => (
                                    <circle key={`baseline-${dot.label}`} cx={dot.x} cy={dot.y} r={3.6} fill="#fde68a" stroke="#b45309" strokeWidth={0.8} />
                                ))}
                                <line
                                    x1={chart.margin.left}
                                    y1={chart.thresholdY}
                                    x2={chart.width - chart.margin.right}
                                    y2={chart.thresholdY}
                                    strokeDasharray="8 6"
                                    strokeWidth={2}
                                    style={{ stroke: 'var(--viz-line-dashed)' }}
                                />
                                <text
                                    x={chart.width - chart.margin.right + 4}
                                    y={chart.thresholdY - 8}
                                    className={detailStyles.chartAxisLabel}
                                    textAnchor="start"
                                >
                                    Alert threshold 0.25
                                </text>
                                <line
                                    x1={chart.margin.left}
                                    y1={chart.height - chart.margin.bottom}
                                    x2={chart.width - chart.margin.right}
                                    y2={chart.height - chart.margin.bottom}
                                    stroke="rgba(148, 163, 184, 0.45)"
                                    strokeWidth={1}
                                />
                                <line
                                    x1={chart.margin.left}
                                    y1={chart.margin.top}
                                    x2={chart.margin.left}
                                    y2={chart.height - chart.margin.bottom}
                                    stroke="rgba(148, 163, 184, 0.35)"
                                    strokeWidth={1}
                                />
                                {chart.axisTicks.map(tick => (
                                    <text key={`tick-${tick.label}`} x={tick.x} y={chart.height - chart.margin.bottom + 22} className={detailStyles.chartAxisLabel}>
                                        {tick.label}
                                    </text>
                                ))}
                                {chart.valueTicks.map(tick => (
                                    <g key={`value-${tick.value.toFixed(2)}`}>
                                        <line
                                            x1={chart.margin.left - 6}
                                            y1={tick.y}
                                            x2={chart.width - chart.margin.right}
                                            y2={tick.y}
                                            stroke="rgba(148, 163, 184, 0.18)"
                                            strokeWidth={0.75}
                                        />
                                        <text x={chart.margin.left - 32} y={tick.y + 4} className={detailStyles.chartAxisLabel} textAnchor="end">
                                            {tick.value.toFixed(2)}
                                        </text>
                                    </g>
                                ))}
                                <text x={(chart.width + chart.margin.left) / 2} y={chart.height - 8} className={detailStyles.chartAxisTitle}>
                                    Observation window (hour)
                                </text>
                                <text
                                    x={chart.margin.left - 48}
                                    y={chart.margin.top - 10}
                                    className={detailStyles.chartAxisTitle}
                                    transform={`rotate(-90 ${chart.margin.left - 48},${chart.margin.top - 10})`}
                                >
                                    Risk score
                                </text>
                            </svg>
                            <div className={detailStyles.chartLegend}>
                                <span className={detailStyles.chartLegendItem}>
                                    <span className={detailStyles.chartLegendSwatch} aria-hidden />
                                    <span>Entity risk delta</span>
                                </span>
                                <span className={detailStyles.chartLegendItem}>
                                    <span className={detailStyles.chartLegendLine} aria-hidden />
                                    <span>Anomaly score</span>
                                </span>
                                <span className={detailStyles.chartLegendItem}>
                                    <span className={detailStyles.chartLegendLine} data-variant="secondary" aria-hidden />
                                    <span>Behavior baseline</span>
                                </span>
                                <span className={detailStyles.chartLegendItem}>
                                    <span className={detailStyles.chartLegendLine} data-variant="dashed" aria-hidden />
                                    <span>Alert threshold</span>
                                </span>
                            </div>
                        </article>
                        <article className={detailStyles.contentCard} data-tone={plugin.tone}>
                            <h2>Detection fidelity dashboard</h2>
                            <p>
                                Highlight precision, containment, and evidence rigor so hiring managers see how the NER + anomaly stack behaves in the real world.
                            </p>
                            <ul className={detailStyles.metricList}>
                                {DETECTION_METRICS.map(metric => (
                                    <li key={metric.label} className={detailStyles.metricItem}>
                                        <span className={detailStyles.metricLabel}>{metric.label}</span>
                                        <span className={detailStyles.metricValue}>{metric.value}</span>
                                        <span className={detailStyles.metricDetail}>{metric.detail}</span>
                                    </li>
                                ))}
                            </ul>
                            <h3>Automation hooks</h3>
                            <ul className={detailStyles.bulletList}>
                                {DETECTION_AUTOMATIONS.map(item => (
                                    <li key={item}>{item}</li>
                                ))}
                            </ul>
                        </article>
                    </section>

                    <section className={detailStyles.contentGrid}>
                        <article className={detailStyles.contentCard}>
                            <h2>Anomaly pipeline lifecycle</h2>
                            <p>From log ingestion through entity graphing and risk scoring, every stage is observable and locked behind your security baseline.</p>
                            <ul className={detailStyles.bulletList}>
                                {PIPELINE_STAGES.map(stage => (
                                    <li key={stage.label}>
                                        <strong>{stage.label}.</strong> {stage.detail}
                                    </li>
                                ))}
                            </ul>
                        </article>
                        <article className={detailStyles.contentCard}>
                            <h2>Security & compliance guardrails</h2>
                            <p>Identity and access insights are only valuable if the pipeline itself stays compliant.</p>
                            <ul className={detailStyles.bulletList}>
                                {CONTROL_LIST.map(item => (
                                    <li key={item}>{item}</li>
                                ))}
                            </ul>
                        </article>
                        <article className={detailStyles.contentCard}>
                            <h2>Response & evidence playbooks</h2>
                            {RESPONSE_RUNBOOKS.map(runbook => (
                                <div key={runbook.heading}>
                                    <h3>{runbook.heading}</h3>
                                    <p>{runbook.copy}</p>
                                    <ul className={detailStyles.bulletList}>
                                        {runbook.bullets.map(bullet => (
                                            <li key={`${runbook.heading}-${bullet}`}>{bullet}</li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </article>
                    </section>

                    <section className={detailStyles.contentCard}>
                        <h2>Artifacts delivered</h2>
                        <ul className={detailStyles.bulletList}>
                            {plugin.bullets.map(point => (
                                <li key={point}>{point}</li>
                            ))}
                        </ul>
                    </section>
                </div>
            </div>
        </Layout>
    );
}
