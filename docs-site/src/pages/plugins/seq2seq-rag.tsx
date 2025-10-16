import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import { useEffect, useMemo } from 'react';
import RAGLatencyChart from '@site/src/theme/components/RAGLatencyChart';
import detailStyles from './plugin-detail.module.css';
import { getPluginById } from '@site/src/data/plugins/config';
import React from 'react';

const plugin = getPluginById('seq2seq-rag');

if (!plugin) {
    throw new Error('Plugin configuration for seq2seq-rag is missing.');
}

const DISCOVERY_STEPS: Array<{ title: string; detail: string }> = [
    {
        title: 'Corpus audit + embeddings split',
        detail: 'Vectorizes governed corpora into hot, warm, and cold shards so sub-300ms latency targets hold during peak exec usage.',
    },
    {
        title: 'Prompt choreography',
        detail: 'Retrieval stage, synthesis stage, and compliance stage prompts live in versioned bundles with Git-backed approvals.',
    },
    {
        title: 'Latency envelopes + observability',
        detail: 'CloudWatch + X-Ray tracing surfaces inference bottlenecks while SageMaker endpoints autoscale inside pre-warmed capacity pools.',
    },
];

const GUARDRAILS: string[] = [
    'PII and trade-secret classifiers inspect prompts and completions before any token streams back to the requestor.',
    'Query budget caps keep GPU burst usage deterministic and route overflow through a cached summariser instead of failing the request outright.',
    'Audit trail exports capture every retrieval source with hash-aligned citations to satisfy legal and compliance reviews.',
];

const DELIVERY_PODS: Array<{ heading: string; copy: string; bullets: string[] }> = [
    {
        heading: 'Enablement sprint',
        copy: 'Cut over to curated embeddings, wire up GuardDuty/Lake Formation governance, and tune warm-path caches.',
        bullets: [
            'Shadow index stands up with pgvector + Bedrock Titan embeddings for golden questions.',
            'Cross-account IAM roles validated against Security Hub findings before production access.',
        ],
    },
    {
        heading: 'Reliability sprint',
        copy: 'Chaos drills across burst traffic ensure retrieval fallback logic and streaming guardrails degrade gracefully.',
        bullets: [
            'Synthetic traffic from Locust drives concurrency spikes while error budgets are tracked in Grafana.',
            'Bedrock model gateway canary tests keep track of inference latency before exec showcases.',
        ],
    },
];

// Replace with executive-focused latency envelope points (optimized vs uncached)
const LATENCY_POINTS: Array<{ phase: string; optimized: number; uncached: number }> = [
    { phase: 'Shadow', optimized: 228, uncached: 312 },
    { phase: 'Pilot', optimized: 255, uncached: 396 },
    { phase: 'Exec Q&A', optimized: 271, uncached: 480 },
    { phase: 'Launch', optimized: 298, uncached: 650 },
];

const LATENCY_SLO = 300;

const RAG_METRICS: Array<{ label: string; value: string; detail: string }> = [
    { label: 'Citation Efficacy', value: '96%', detail: 'Responses with inline, hash-aligned source references, vital for compliance and dispute resolution.' },
    { label: 'Compliance Pass Rate', value: '99.2%', detail: 'Prompts and completions cleared through Bedrock and the custom ShieldCraft Policy Lattice.' },
    { label: 'Warm-Path Efficiency', value: '82% Cache Hit', detail: "High-priority requests served under the P95 contract via domain-sharded retrieval (direct FinOps correlation)." },
];

const OPERATIONS_HOOKS: string[] = [
    'Latency budgets traced per Step Functions stage with alarmed spans when retrieval or prompt assembly drifts >12%.',
    'Adversarial prompt suites replay hourly; regressions quarantine the prompt bundle before it reaches production questions.',
    'Vector index promotions require Git-approved manifest diffs plus automated RAG regression results pinned in CodeCatalyst.',
];

export default function Seq2SeqRagPage() {
    useEffect(() => {
        if (typeof document === 'undefined') return () => undefined;
        document.body.classList.add('aurora-surface');
        return () => {
            document.body.classList.remove('aurora-surface');
        };
    }, []);

    // Chart rendering moved to RAGLatencyChart component below; remove local chart memo.

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
                        <span className={detailStyles.heroTaskBadge} data-tone={plugin.tone}>Domain Focus · Seq2Seq / Generative AI</span>
                        <h1 className={detailStyles.heroTitle}>Seq2Seq Answer Architect: Auditable AI Governance Accelerator 🛡️</h1>
                        <p className={detailStyles.heroTagline}>
                            The Retrieval-Augmented Generation (RAG) platform purpose-built for <strong>auditable executive decision support</strong>. Delivers evidence synthesis with a <strong>Guaranteed P95 Performance Contract (&lt;300ms)</strong> and mandatory governance across all retrieval and inference paths.
                        </p>
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
                                <span className={detailStyles.heroPriceLabel}>Platform Fee</span>
                                <span className={detailStyles.heroPriceValue}>$3,800/mo + usage credits</span>
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

                    <section className={detailStyles.visualSection} aria-label="RAG latency and guardrails">
                        <article className={`${detailStyles.contentCard} ${detailStyles.vizCard}`} data-tone={plugin.tone}>
                            <div className={detailStyles.vizHeader}>
                                <h2 className={detailStyles.vizTitle}>RAG MLOps Performance Contract</h2>
                                <p className={detailStyles.vizSubtitle}>
                                    Warm-path caching keeps Retrieval-Augmented answers reliably <strong>below the P95 SLO</strong>. The visible <strong>Uncached Fallback</strong> path provides a quantitative measure of ShieldCraft's value add.
                                </p>
                            </div>
                            <RAGLatencyChart
                                sloLimit={LATENCY_SLO}
                                data={LATENCY_POINTS}
                            />
                            <div className={detailStyles.chartLegend}>
                                <span className={detailStyles.chartLegendItem}>
                                    <span className={detailStyles.chartLegendSwatch} aria-hidden />
                                    <span>Optimized P95 (warm-path)</span>
                                </span>
                                <span className={detailStyles.chartLegendItem}>
                                    <span className={detailStyles.chartLegendLine} data-variant="secondary" aria-hidden />
                                    <span>Uncached fallbacks</span>
                                </span>
                                <span className={detailStyles.chartLegendItem}>
                                    <span className={detailStyles.chartLegendLine} data-variant="dashed" aria-hidden />
                                    <span>300ms P95 SLO (hard guardrail)</span>
                                </span>
                            </div>
                        </article>
                        <article className={detailStyles.contentCard} data-tone={plugin.tone}>
                            <h2>RAG operations scorecard</h2>
                            <p>
                                Treat retrieval-augmented generation as an observable service. Measure citations, latency, and guardrails with production discipline.
                            </p>
                            <ul className={detailStyles.metricList}>
                                {RAG_METRICS.map(metric => (
                                    <li key={metric.label} className={detailStyles.metricItem}>
                                        <span className={detailStyles.metricLabel}>{metric.label}</span>
                                        <span className={detailStyles.metricValue}>{metric.value}</span>
                                        <span className={detailStyles.metricDetail}>{metric.detail}</span>
                                    </li>
                                ))}
                            </ul>
                            <h3>Operational hooks</h3>
                            <ul className={detailStyles.bulletList}>
                                {OPERATIONS_HOOKS.map(item => (
                                    <li key={item}>{item}</li>
                                ))}
                            </ul>
                        </article>
                    </section>

                    <section className={detailStyles.contentGrid}>
                        <article className={detailStyles.contentCard}>
                            <h2>Discovery & orchestration</h2>
                            <p>
                                Map where knowledge actually lives, then codify retrieval orchestration so Bedrock stays predictable under exec questioning and analyst follow-ups.
                            </p>
                            <ul className={detailStyles.bulletList}>
                                {DISCOVERY_STEPS.map(step => (
                                    <li key={step.title}>
                                        <strong>{step.title}.</strong> {step.detail}
                                    </li>
                                ))}
                            </ul>
                        </article>
                        <article className={detailStyles.contentCard}>
                            <h2>Guardrails that ship with day zero</h2>
                            <p>Confidence scoring, prompt hygiene, and compliance sign-off are part of the base build rather than a backlog item.</p>
                            <ul className={detailStyles.bulletList}>
                                {GUARDRAILS.map(item => (
                                    <li key={item}>{item}</li>
                                ))}
                            </ul>
                        </article>
                        <article className={detailStyles.contentCard}>
                            <h2>Delivery cadence</h2>
                            {DELIVERY_PODS.map(pod => (
                                <div key={pod.heading}>
                                    <h3>{pod.heading}</h3>
                                    <p>{pod.copy}</p>
                                    <ul className={detailStyles.bulletList}>
                                        {pod.bullets.map(bullet => (
                                            <li key={`${pod.heading}-${bullet}`}>{bullet}</li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </article>
                    </section>

                    <section className={detailStyles.contentCard}>
                        <h2>What stays on autopilot after go-live</h2>
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
