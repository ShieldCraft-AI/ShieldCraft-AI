import Layout from '@theme/Layout';
import React, { useCallback, useEffect } from 'react';
import { useHistory } from '@docusaurus/router';
import styles from './plugins.module.css';
import { PLUGIN_CONFIG, PLUGIN_SUMMARY } from '@site/src/data/plugins/config';

const LATENCY_STEPS = [
    {
        title: 'Budget envelope established',
        detail: 'P50 ≤ 150ms and P95 ≤ 320ms enforced via Step Functions service integrations, with per-branch alarms feeding CloudWatch SLO dashboards.',
    },
    {
        title: 'Orchestrated resiliency',
        detail: 'Concurrency windows and retry policies adapt by environment, ensuring dev stays cost-lean while prod absorbs burst workloads without throttling.',
    },
    {
        title: 'High-throughput readiness',
        detail: 'Warm pool management automates GPU endpoint rotation, and read replicas serve vector lookups in-region to avoid cross-AZ jitter.',
    },
];

export default function PluginsPage() {
    const history = useHistory();

    useEffect(() => {
        if (typeof document === 'undefined') return () => undefined;
        document.body.classList.add('plugins-page');
        document.body.classList.add('aurora-surface');
        return () => {
            document.body.classList.remove('plugins-page');
            document.body.classList.remove('aurora-surface');
        };
    }, []);

    const navigateToDetail = useCallback((href: string) => {
        history.push(href);
    }, [history]);

    const handleCardKeyDown = useCallback((event: React.KeyboardEvent<HTMLElement>, href: string) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            navigateToDetail(href);
        }
    }, [navigateToDetail]);

    return (
        <Layout title="Plugins" description="ShieldCraft AI plugins and modular accelerators for threat intelligence and generative workflows.">
            <div className={styles.pluginsPageWrapper}>
                <div className={styles.pluginsInner}>
                    <section className={styles.hero}>
                        <div className={styles.titleCluster}>
                            <p className={styles.pageSubtitle}>
                                Modular accelerators that snap into ShieldCraft AI&apos;s governed control plane. Each plugin inherits our IaC guardrails, FinOps envelopes,
                                and cross-environment promotion workflows so platform teams can ship faster without sacrificing rigor.
                            </p>
                        </div>
                    </section>

                    <section className={styles.pluginGrid} aria-label="Plugin catalog">
                        {PLUGIN_CONFIG.map((plugin) => (
                            <article
                                key={plugin.id}
                                id={plugin.id}
                                className={styles.pluginCard}
                                data-tone={plugin.tone}
                                role="link"
                                tabIndex={0}
                                aria-label={`${plugin.name} deep dive`}
                                onClick={() => navigateToDetail(plugin.detailHref)}
                                onKeyDown={(event) => handleCardKeyDown(event, plugin.detailHref)}
                            >
                                <div className={styles.cardHeading}>
                                    <h2 className={styles.cardTitle}>{plugin.name}</h2>
                                    <p className={styles.cardSubtitle}>{plugin.tagline}</p>
                                    <div className={styles.cardPrice}>
                                        <span className={styles.cardPriceLabel}>Starting at</span>
                                        <span className={styles.cardPriceValue}>{plugin.price}</span>
                                    </div>
                                </div>
                                <div className={styles.cardMetaRow}>
                                    {plugin.chips.map((chip) => (
                                        chip.href ? (
                                            <a
                                                key={`${plugin.id}-${chip.label}`}
                                                className={styles.cardChip}
                                                data-tone={chip.tone ?? 'default'}
                                                href={chip.href}
                                                onClick={(event) => event.stopPropagation()}
                                                onKeyDown={(event) => event.stopPropagation()}
                                            >
                                                {chip.label}
                                            </a>
                                        ) : (
                                            <span
                                                key={`${plugin.id}-${chip.label}`}
                                                className={styles.cardChip}
                                                data-tone={chip.tone ?? 'default'}
                                            >
                                                {chip.label}
                                            </span>
                                        )
                                    ))}
                                </div>
                                <div className={styles.cardStatRow}>
                                    {plugin.stats.map((stat) => (
                                        <div key={`${plugin.id}-${stat.label}`} className={styles.cardStat}>
                                            <span className={styles.cardStatLabel}>{stat.label}</span>
                                            <span className={styles.cardStatValue}>{stat.value}</span>
                                            <span className={styles.cardStatDetail}>{stat.detail}</span>
                                        </div>
                                    ))}
                                </div>
                                <div className={styles.cardDivider} aria-hidden />
                                <div className={styles.cardBody}>
                                    <ul className={styles.cardBullets}>
                                        {plugin.bullets.map((point, idx) => (
                                            <li key={`${plugin.id}-bullet-${idx}`}>{point}</li>
                                        ))}
                                    </ul>
                                </div>
                            </article>
                        ))}
                    </section>

                    <section className={styles.architectureStrip} aria-label="Seq2Seq architecture focus">
                        <div className={styles.architecturePanel}>
                            <div className={styles.architectureTitle}>Scale &amp; latency contract</div>
                            <p className={styles.architectureText}>
                                Retrieval, prompt shaping, and inference run as discrete stages so ShieldCraft can flex concurrency without breaching cost ceilings. Step Functions state machines enforce
                                timeouts per branch, while CloudWatch SLO alarms trigger warm-pool scaling or fall-back heuristics when latency drifts.
                            </p>
                            <div className={styles.timeline}>
                                {LATENCY_STEPS.map((step) => (
                                    <div key={step.title} className={styles.timelineStep}>
                                        <span className={styles.timelineMarker} aria-hidden />
                                        <div className={styles.timelineContent}>
                                            <div className={styles.timelineHeading}>{step.title}</div>
                                            <div className={styles.timelineDetail}>{step.detail}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className={styles.architecturePanel}>
                            <div className={styles.architectureTitle}>Unstructured data management</div>
                            <p className={styles.architectureText}>
                                Knowledge bases hydrate from governed S3 zones into pgvector with schema tags, retention policies, and lineage hooks. Chunking profiles mirror ingestion contracts
                                so updates remain deterministic, and sensitive payloads route through DLP inspectors before ever reaching inference.
                            </p>
                            <p className={styles.architectureText}>
                                Guardrails span the full path: prompts are scrubbed for PII, completions are redacted for policy violations, and every decision is logged with environment-specific tracing IDs.
                            </p>
                        </div>
                    </section>
                </div>
            </div>
        </Layout>
    );
}
