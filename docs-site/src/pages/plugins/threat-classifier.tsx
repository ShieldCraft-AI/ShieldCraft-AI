import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import { useEffect, useMemo } from 'react';
import styles from './threat-classifier.module.css';
import { getPluginById } from '@site/src/data/plugins/config';
import React from 'react';

type ChartPoint = {
    label: string;
    baseline: number;
    tuned: number;
    analysts: number;
};

type TimelineEvent = {
    phase: string;
    meta: string;
    detail: string;
};

type StatCard = {
    label: string;
    value: string;
    detail: string;
};

type InsightFeature = {
    label: string;
    headline: string;
    detail: string;
};

type Insight = {
    title: string;
    copy: string;
    features?: InsightFeature[];
};

const plugin = getPluginById('threat-classifier');

if (!plugin) {
    throw new Error('Plugin configuration for threat-classifier is missing.');
}

const STAT_CARDS: StatCard[] = [
    {
        label: 'Latency P95',
        value: '236 ms',
        detail: 'Measured across 4 VPC endpoints with concurrency guards and warm pool rotation.',
    },
    {
        label: 'Analyst override drop',
        value: '↓ 72%',
        detail: 'Overrides fell from 89/day to 25/day once the feedback loop landed in production.',
    },
    {
        label: 'SOC throughput lift',
        value: '× 3.4',
        detail: 'Triage runbooks close in a single pass with score explanations embedded in tickets.',
    },
];

const TIMELINE: TimelineEvent[] = [
    {
        phase: 'Shadow scoring launched',
        meta: 'Week 0',
        detail: 'Mirrors GuardDuty severity, emitting suppressed findings into Security Hub for analyst-only review.',
    },
    {
        phase: 'Feedback captured as data',
        meta: 'Week 2',
        detail: 'Analyst adjudications are streamed through EventBridge within 12 minutes to hydrate retraining windows.',
    },
    {
        phase: 'Drift alarm triggered',
        meta: 'Week 4',
        detail: 'RMSE threshold breach auto-quarantines stale enrichers and spins a SageMaker retrain in isolation.',
    },
    {
        phase: 'Blue/green promotion',
        meta: 'Week 6',
        detail: 'New weights graduate through canary accounts with immutable manifests and dual approval in CodePipeline.',
    },
    {
        phase: 'Explainability shipped to execs',
        meta: 'Week 8',
        detail: 'Regression deck narrates feature lift, override rate, and residual risk for security leadership.',
    },
];

const CHART_POINTS: ChartPoint[] = [
    { label: 'Sprint 0', baseline: 0.41, tuned: 0.52, analysts: 0.5 },
    { label: 'Sprint 1', baseline: 0.44, tuned: 0.58, analysts: 0.54 },
    { label: 'Sprint 2', baseline: 0.47, tuned: 0.63, analysts: 0.59 },
    { label: 'Sprint 3', baseline: 0.5, tuned: 0.69, analysts: 0.64 },
    { label: 'Sprint 4', baseline: 0.53, tuned: 0.74, analysts: 0.69 },
    { label: 'Sprint 5', baseline: 0.55, tuned: 0.78, analysts: 0.73 },
];

const INSIGHTS: Insight[] = [
    {
        title: 'Explainable triage, not black-box lifts',
        copy: 'Daily regression reports pair precision lift with override deltas so SOC leads can defend actions in incident postmortems before promoting new weights.',
        features: [
            {
                label: 'Top lift contributor',
                headline: '+18% from SaaS session linking',
                detail: 'Okta risk signals fused with GuardDuty findings suppressed MFA fatigue false positives during red-team spikes.',
            },
            {
                label: 'Counter-signal quarantined',
                headline: '-6% from stale asset tags',
                detail: 'Deprecated CMDB tags triggered auto-curation to quarantine the feature before it polluted the next retrain window.',
            },
        ],
    },
    {
        title: 'Promotion stays inside IaC guardrails',
        copy: 'Every retrain writes an immutable manifest to the registry; CodePipeline gates demand drift diffs plus approval before SageMaker endpoints flip to the new bundle.',
        features: [
            {
                label: 'Guardrail',
                headline: 'Manifest hash verification',
                detail: 'Deployment halts if the feature manifest hash diverges from the approved artifact, protecting downstream IaC rollbacks.',
            },
        ],
    },
    {
        title: 'Latency budgets stay predictable',
        copy: 'Concurrency windows and warm pool orchestration keep P95 under 250ms even as we blend SaaS enrichers, analyst overrides, and managed threat feeds.',
        features: [
            {
                label: 'Observation',
                headline: 'EventBridge fan-out throttling',
                detail: 'Adaptive concurrency halved queue spikes during chaos drills without dropping recall or breaking cost envelopes.',
            },
        ],
    },
];

export default function ThreatClassifierPage() {
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
        const margin = { top: 24, right: 32, bottom: 46, left: 64 };
        const minScore = 0.35;
        const maxScore = 0.82;
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;
        const xForIndex = (index: number) => {
            if (CHART_POINTS.length === 1) return margin.left + innerWidth / 2;
            return margin.left + (index / (CHART_POINTS.length - 1)) * innerWidth;
        };
        const yForValue = (value: number) => {
            const clamped = Math.min(Math.max(value, minScore), maxScore);
            const ratio = (clamped - minScore) / (maxScore - minScore);
            return height - margin.bottom - ratio * innerHeight;
        };

        const baselineCoords: Array<{ x: number; y: number }> = [];
        const tunedCoords: Array<{ x: number; y: number }> = [];
        const analystDots: Array<{ x: number; y: number; label: string }> = [];

        CHART_POINTS.forEach((point, index) => {
            const x = xForIndex(index);
            baselineCoords.push({ x, y: yForValue(point.baseline) });
            tunedCoords.push({ x, y: yForValue(point.tuned) });
            analystDots.push({ x, y: yForValue(point.analysts), label: point.label });
        });

        const coordsToPath = (coords: Array<{ x: number; y: number }>) => coords
            .map((coord, index) => `${index === 0 ? 'M' : 'L'}${coord.x},${coord.y}`)
            .join(' ');

        const baselinePath = coordsToPath(baselineCoords);
        const tunedPath = coordsToPath(tunedCoords);
        const areaCoords = [...tunedCoords, ...baselineCoords.slice().reverse()];
        const areaPath = areaCoords
            .map((coord, index) => `${index === 0 ? 'M' : 'L'}${coord.x},${coord.y}`)
            .join(' ') + ' Z';

        const axisTicks = CHART_POINTS.map((point, index) => ({
            x: xForIndex(index),
            label: point.label,
        }));

        const scoreTicks = [0.4, 0.5, 0.6, 0.7, 0.8].map(score => ({
            score,
            y: yForValue(score),
        }));

        return {
            width,
            height,
            margin,
            baselinePath,
            tunedPath,
            areaPath,
            analystDots,
            axisTicks,
            scoreTicks,
        };
    }, []);

    return (
        <Layout title="Threat-Classifier" description="Detailed regression view for the ShieldCraft AI Threat-Classifier accelerator.">
            <div className={styles.pageWrapper}>
                <div className={styles.inner}>
                    <section className={styles.hero}>
                        <div className={styles.breadcrumb}>
                            <Link to="/plugins">Plugins</Link>
                            <span aria-hidden>·</span>
                            <span>Threat-Classifier</span>
                        </div>
                        <span className={styles.taskBadge}>ML Task · {plugin.taskType}</span>
                        <h1 className={styles.heroTitle}>Threat-Classifier regression</h1>
                        <p className={styles.heroBlurb}>
                            Fuses GuardDuty, SaaS telemetry, and analyst feedback into an adaptive regression bundle. Scorecards publish directly into Security Hub and EventBridge so
                            incidents stay explainable and approvals remain immutable.
                        </p>
                        <div className={styles.heroMetaRow}>
                            <span className={styles.chip}>Threat intelligence regression</span>
                            <span className={styles.chip}>Latency SLA: 250ms P95</span>
                            <span className={styles.chip}>Auto-tuned retraining</span>
                        </div>
                        <div className={styles.heroMetaRow}>
                            {STAT_CARDS.map(card => (
                                <div key={card.label} className={styles.statCard}>
                                    <span className={styles.statLabel}>{card.label}</span>
                                    <span className={styles.statValue}>{card.value}</span>
                                    <span className={styles.statDetail}>{card.detail}</span>
                                </div>
                            ))}
                        </div>
                    </section>

                    <section className={styles.sectionGrid} aria-label="Regression performance and promotion timeline">
                        <div className={styles.diagramCard}>
                            <div className={styles.diagramHeader}>
                                <div>
                                    <div className={styles.diagramTitle}>Precision lift against analyst feedback</div>
                                    <p className={styles.diagramSubtitle}>
                                        Analyst adjudications land in under 15 minutes, keeping regression weights honest. Blue area shows lift over the legacy scoring model while dots track human feedback.
                                    </p>
                                </div>
                            </div>
                            <svg
                                className={styles.chartSvg}
                                viewBox={`0 0 ${chart.width} ${chart.height}`}
                                role="img"
                                aria-labelledby="threat-chart-title"
                            >
                                <title id="threat-chart-title">Threat-Classifier regression precision vs baseline</title>
                                <defs>
                                    <linearGradient id="threatLiftGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                        <stop offset="0%" stopColor="rgba(14, 165, 233, 0.35)" />
                                        <stop offset="100%" stopColor="rgba(59, 130, 246, 0.05)" />
                                    </linearGradient>
                                    <linearGradient id="threatLineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stopColor="#0ea5e9" />
                                        <stop offset="60%" stopColor="#6366f1" />
                                        <stop offset="95%" stopColor="#ef4444" />
                                    </linearGradient>
                                </defs>
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
                                <path d={chart.areaPath} fill="url(#threatLiftGradient)" opacity={0.7} />
                                <path d={chart.baselinePath} stroke="rgba(71, 85, 105, 0.65)" strokeWidth={2.2} strokeDasharray="6 6" fill="none" />
                                <path d={chart.tunedPath} stroke="url(#threatLineGradient)" strokeWidth={3} fill="none" />
                                {chart.analystDots.map(dot => (
                                    <circle key={`dot-${dot.label}`} cx={dot.x} cy={dot.y} r={5} fill="#38bdf8" />
                                ))}
                                {chart.axisTicks.map(tick => (
                                    <text key={`tick-${tick.label}`} x={tick.x} y={chart.height - chart.margin.bottom + 22} className={styles.axisLabel}>
                                        {tick.label}
                                    </text>
                                ))}
                                {chart.scoreTicks.map(tick => (
                                    <g key={`score-${tick.score}`}>
                                        <line
                                            x1={chart.margin.left - 6}
                                            y1={tick.y}
                                            x2={chart.width - chart.margin.right}
                                            y2={tick.y}
                                            stroke="rgba(148, 163, 184, 0.18)"
                                            strokeWidth={0.75}
                                        />
                                        <text x={chart.margin.left - 26} y={tick.y + 4} className={styles.axisLabel}>
                                            {tick.score.toFixed(2)}
                                        </text>
                                    </g>
                                ))}
                                <text x={(chart.width + chart.margin.left) / 2} y={chart.height - 6} className={styles.axisTitle}>
                                    Sprint cadence
                                </text>
                                <text
                                    x={chart.margin.left - 48}
                                    y={chart.margin.top - 8}
                                    className={styles.axisTitle}
                                    transform={`rotate(-90 ${chart.margin.left - 48},${chart.margin.top - 8})`}
                                >
                                    Precision (↑ better)
                                </text>
                            </svg>
                            <div className={styles.legend}>
                                <span className={styles.legendItem}>
                                    <span className={styles.legendSwatchPrimary} aria-hidden />
                                    <span>Adaptive regression lift</span>
                                </span>
                                <span className={styles.legendItem}>
                                    <span className={styles.legendSwatchSecondary} aria-hidden />
                                    <span>Legacy scoring envelope</span>
                                </span>
                                <span className={styles.legendItem}>
                                    <span className={styles.legendDot} aria-hidden />
                                    <span>Analyst override trend</span>
                                </span>
                            </div>
                        </div>
                        <div className={styles.timeline}>
                            {TIMELINE.map(event => (
                                <div key={event.phase} className={styles.timelineItem}>
                                    <span className={styles.timelineMarker} aria-hidden />
                                    <div>
                                        <span className={styles.timelineMeta}>{event.meta}</span>
                                        <div className={styles.timelineHeading}>{event.phase}</div>
                                        <div className={styles.timelineDetail}>{event.detail}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                    <section className={styles.insightsGrid} aria-label="Deployment insights">
                        {INSIGHTS.map(insight => (
                            <article key={insight.title} className={styles.insightCard}>
                                <h3 className={styles.insightTitle}>{insight.title}</h3>
                                <p className={styles.insightCopy}>{insight.copy}</p>
                                {insight.features?.length ? (
                                    <ul className={styles.featureList}>
                                        {insight.features.map(feature => (
                                            <li key={`${insight.title}-${feature.headline}`} className={styles.featureItem}>
                                                <span className={styles.featureLabel}>{feature.label}</span>
                                                <div className={styles.featureHeadline}>{feature.headline}</div>
                                                <div className={styles.featureDetail}>{feature.detail}</div>
                                            </li>
                                        ))}
                                    </ul>
                                ) : null}
                            </article>
                        ))}
                    </section>
                </div>
            </div>
        </Layout>
    );
}
