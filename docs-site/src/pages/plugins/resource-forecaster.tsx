import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import { useEffect, useMemo } from 'react';
import detailStyles from './plugin-detail.module.css';
import { getPluginById } from '@site/src/data/plugins/config';

const plugin = getPluginById('resource-forecaster');

if (!plugin) {
    throw new Error('Plugin configuration for resource-forecaster is missing.');
}

// Forecast pipeline stages (refined copy)
const FORECAST_PIPELINE: Array<{ title: string; description: string }> = [
    {
        title: 'Trusted Feature Curation',
        description: 'Tag validators reconcile AWS Config, Cost Explorer, and custom metadata to ensure 100% feature hygiene before model ingestion.',
    },
    {
        title: 'Regression Envelope & Guardrail',
        description: 'Per-environment regression envelopes produce bounded forecasts with explicit budget guardrails and RMSE-based fidelity contracts.',
    },
    {
        title: 'Recommendation Automation',
        description: 'Rightsizing, Savings Plan utilization, and reserved instance recommendations convert into owner-assigned, dollar-impact tickets.',
    },
];

const FINOPS_KPIS: Array<{ label: string; value: string; detail: string }> = [
    { label: 'Forecast Fidelity', value: 'RMSE 3.9%', detail: 'Keeps the blended regression stack under the 5% variance threshold.' },
    { label: 'Budget Compliance', value: '0 Breaches', detail: 'Zero instances of consumption exceeding committed budget envelopes.' },
    { label: 'Resource Optimization', value: '-41% Delta', detail: 'Quantifiable monthly compute spend reduction after automated rightsizing and SP adjustments.' },
];

const GOVERNANCE_LIST: string[] = [
    'FinOps runbooks run directly from WorkDocs / Confluence exports with evidence attachments for audit.',
    'Budgets + anomaly notifications align with Service Control Policies so org-level guardrails never go stale.',
    'Infra-as-code PR checks prevent rollouts that breach forecast guardrails without override justification.',
];

const CAPACITY_POINTS: Array<{ label: string; actual: number; forecast: number; budget: number }> = [
    { label: 'Jan', actual: 328, forecast: 334, budget: 360 },
    { label: 'Feb', actual: 316, forecast: 320, budget: 352 },
    { label: 'Mar', actual: 299, forecast: 304, budget: 344 },
    { label: 'Apr', actual: 284, forecast: 289, budget: 336 },
    { label: 'May', actual: 272, forecast: 276, budget: 328 },
    { label: 'Jun', actual: 261, forecast: 265, budget: 320 },
];

const ERROR_METRICS: Array<{ label: string; value: string; detail: string }> = [
    { label: 'Rolling RMSE', value: '3.9%', detail: 'Keeps the blended regression stack under the ≥5% variance guardrail across environments.' },
    { label: 'Coverage delta', value: '-41%', detail: 'Monthly compute spend change versus baseline after automated rightsizing and savings plan adjustments.' },
    { label: 'Guardrail breaches', value: '0', detail: 'Scaling limits auto-tune before budgets drift, blocking deployments that would exceed committed envelopes.' },
];

const REGRESSION_CONTROLS: string[] = [
    'Cross-environment retrains sign manifest hashes and promote through CodePipeline once RMSE proves stable for 14 days.',
    'CloudWatch anomaly alarms compare live spend to the regression envelope and trigger Slack / Jira workflows when variance > 6%.',
    'SageMaker Feature Store captures enrichment lineage so finance teams can audit every driver used in the forecast.',
];

export default function ResourceForecasterPage() {
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
        const allValues = CAPACITY_POINTS.flatMap(point => [point.actual, point.forecast, point.budget]);
        const minValue = Math.min(...allValues) - 12;
        const maxValue = Math.max(...allValues) + 12;
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        const xForIndex = (index: number) => {
            if (CAPACITY_POINTS.length === 1) {
                return margin.left + innerWidth / 2;
            }
            return margin.left + (index / (CAPACITY_POINTS.length - 1)) * innerWidth;
        };

        const yForValue = (value: number) => {
            const ratio = (value - minValue) / (maxValue - minValue);
            return height - margin.bottom - ratio * innerHeight;
        };

        const coordsToPath = (coords: Array<{ x: number; y: number }>) => coords
            .map((coord, index) => `${index === 0 ? 'M' : 'L'}${coord.x},${coord.y}`)
            .join(' ');

        const actualCoords: Array<{ x: number; y: number }> = [];
        const forecastCoords: Array<{ x: number; y: number }> = [];
        const budgetCoords: Array<{ x: number; y: number }> = [];

        CAPACITY_POINTS.forEach((point, index) => {
            const x = xForIndex(index);
            actualCoords.push({ x, y: yForValue(point.actual) });
            forecastCoords.push({ x, y: yForValue(point.forecast) });
            budgetCoords.push({ x, y: yForValue(point.budget) });
        });

        const savingsAreaCoords = [...budgetCoords, ...actualCoords.slice().reverse()];

        const axisTicks = CAPACITY_POINTS.map((point, index) => ({ x: xForIndex(index), label: point.label }));
        const tickCount = 4;
        const valueTicks = Array.from({ length: tickCount }, (_, idx) => {
            const value = minValue + ((maxValue - minValue) / (tickCount - 1)) * idx;
            return { value, y: yForValue(value) };
        });

        return {
            width,
            height,
            margin,
            actualPath: coordsToPath(actualCoords),
            forecastPath: coordsToPath(forecastCoords),
            budgetPath: coordsToPath(budgetCoords),
            savingsAreaPath: coordsToPath(savingsAreaCoords) + ' Z',
            axisTicks,
            valueTicks,
            actualDots: CAPACITY_POINTS.map((point, index) => ({ label: point.label, x: actualCoords[index].x, y: actualCoords[index].y })),
            forecastDots: CAPACITY_POINTS.map((point, index) => ({ label: point.label, x: forecastCoords[index].x, y: forecastCoords[index].y })),
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
                        {/* Core value proposition: lead with financial control */}
                        <h1 className={detailStyles.heroTitle}>Resource Forecaster: Deterministic FinOps Control Plane 💰</h1>
                        <p className={detailStyles.heroTagline}>
                            A regression-driven <strong>FinOps Assurance Engine</strong> that validates compute expenditure against projected demand and <strong>codifies budget guardrails directly into IaC</strong>. It delivers the <strong>Deterministic Cost-to-Serve (CTS)</strong> transparency required to manage AI at enterprise scale.
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
                            <table className={detailStyles.heroMetaTable}>
                                <tbody>
                                    <tr>
                                        <th>Domain Focus</th>
                                        <td>FinOps & Capacity Governance</td>
                                    </tr>
                                    <tr>
                                        <th>Target Audience</th>
                                        <td>Finance / Platform / SRE Leaders</td>
                                    </tr>
                                    <tr>
                                        <th>Platform Fee</th>
                                        <td>$1,950/mo fixed</td>
                                    </tr>
                                </tbody>
                            </table>
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

                    <section className={detailStyles.visualSection} aria-label="Regression telemetry and guardrails">
                        <article className={`${detailStyles.contentCard} ${detailStyles.vizCard}`} data-tone={plugin.tone}>
                            <div className={detailStyles.vizHeader}>
                                <h2 className={detailStyles.vizTitle}>FinOps Budget Certainty: Regression Envelope vs. Guardrail</h2>
                                <p className={detailStyles.vizSubtitle}>
                                    The Forecasted Regression Envelope bounds expected consumption while the <strong>Budget Guardrail</strong> represents a distinct, hard spending limit. Actual consumption is presented to show adherence to these guarantees.
                                </p>
                            </div>
                            <svg
                                className={detailStyles.chartSvg}
                                viewBox={`0 0 ${chart.width} ${chart.height}`}
                                role="img"
                                aria-labelledby="resource-forecast-chart-title"
                            >
                                <title id="resource-forecast-chart-title">Resource Forecaster regression vs. actual consumption</title>
                                <defs>
                                    <linearGradient id="resourceSavingsGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                        <stop offset="0%" stopColor="rgba(16, 185, 129, 0.25)" />
                                        <stop offset="100%" stopColor="rgba(16, 185, 129, 0.05)" />
                                    </linearGradient>
                                    <linearGradient id="resourceForecastGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stopColor="#22c55e" />
                                        <stop offset="90%" stopColor="#0ea5e9" />
                                    </linearGradient>
                                </defs>
                                <path d={chart.savingsAreaPath} fill="url(#resourceSavingsGradient)" opacity={0.85} />
                                {/* Budget guardrail: draw as a distinct solid line to emphasize the hard spending limit */}
                                <path d={chart.budgetPath} stroke="rgba(220, 38, 38, 0.95)" strokeWidth={3} strokeDasharray="" fill="none" />
                                <path d={chart.forecastPath} stroke="url(#resourceForecastGradient)" strokeWidth={3} fill="none" />
                                <path d={chart.actualPath} stroke="rgba(30, 64, 175, 0.9)" strokeWidth={2.4} fill="none" />
                                {chart.forecastDots.map(dot => (
                                    <circle key={`forecast-${dot.label}`} cx={dot.x} cy={dot.y} r={5} fill="#34d399" stroke="#0f766e" strokeWidth={1.5} />
                                ))}
                                {chart.actualDots.map(dot => (
                                    <circle key={`actual-${dot.label}`} cx={dot.x} cy={dot.y} r={4.5} fill="#1d4ed8" stroke="#eff6ff" strokeWidth={1.2} />
                                ))}
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
                                    <g key={`value-${tick.value.toFixed(0)}`}>
                                        <line
                                            x1={chart.margin.left - 6}
                                            y1={tick.y}
                                            x2={chart.width - chart.margin.right}
                                            y2={tick.y}
                                            stroke="rgba(148, 163, 184, 0.18)"
                                            strokeWidth={0.75}
                                        />
                                        <text x={chart.margin.left - 32} y={tick.y + 4} className={detailStyles.chartAxisLabel} textAnchor="end">
                                            {tick.value.toFixed(0)}
                                        </text>
                                    </g>
                                ))}
                                <text x={(chart.width + chart.margin.left) / 2} y={chart.height - 8} className={detailStyles.chartAxisTitle}>
                                    Monthly normalized compute hours
                                </text>
                                <text
                                    x={chart.margin.left - 48}
                                    y={chart.margin.top - 10}
                                    className={detailStyles.chartAxisTitle}
                                    transform={`rotate(-90 ${chart.margin.left - 48},${chart.margin.top - 10})`}
                                >
                                    Spend envelope (k$)
                                </text>
                            </svg>
                            <div className={detailStyles.chartLegend}>
                                <span className={detailStyles.chartLegendItem}>
                                    <span className={detailStyles.chartLegendSwatch} aria-hidden />
                                    <span>Forecasted regression envelope</span>
                                </span>
                                <span className={detailStyles.chartLegendItem}>
                                    <span className={detailStyles.chartLegendDot} aria-hidden />
                                    <span>Actual consumption</span>
                                </span>
                                <span className={detailStyles.chartLegendItem}>
                                    <span className={detailStyles.chartLegendSwatchGuardrail} aria-hidden />
                                    <span>Budget Guardrail (hard limit)</span>
                                </span>
                            </div>
                        </article>
                        <article className={detailStyles.contentCard} data-tone={plugin.tone}>
                            <h2>Model Fidelity & Cost Assurance Scorecard</h2>
                            <p>
                                Finance, platform, and SRE teams rely on deterministic guarantees. This scorecard surfaces fidelity, budget compliance, and realized optimization impact.
                            </p>
                            <ul className={detailStyles.metricList}>
                                <li className={detailStyles.metricItem}>
                                    <span className={detailStyles.metricLabel}>Forecast Fidelity (RMSE)</span>
                                    <span className={detailStyles.metricValue}>3.9%</span>
                                    <span className={detailStyles.metricDetail}>Keeps the blended regression stack under the 5% variance threshold, guaranteeing high-confidence projections.</span>
                                </li>
                                <li className={detailStyles.metricItem}>
                                    <span className={detailStyles.metricLabel}>Budget Compliance</span>
                                    <span className={detailStyles.metricValue}>0 Breaches</span>
                                    <span className={detailStyles.metricDetail}>Zero instances of deployments or consumption exceeding committed budget envelopes.</span>
                                </li>
                                <li className={detailStyles.metricItem}>
                                    <span className={detailStyles.metricLabel}>Resource Optimization</span>
                                    <span className={detailStyles.metricValue}>-41% Delta</span>
                                    <span className={detailStyles.metricDetail}>Quantifiable reduction in monthly compute spend versus baseline after automated rightsizing and SP adjustments.</span>
                                </li>
                            </ul>

                            <h3>Policy Enforcement & Budget Governance</h3>
                            <ul className={detailStyles.bulletList}>
                                <li><strong>Model Auditability:</strong> SageMaker Feature Store captures complete enrichment lineage so finance teams can audit every input driver used in the forecast.</li>
                                <li><strong>Deployment Blockers:</strong> Infra-as-Code PR checks prevent resource rollouts that breach forecast guardrails without explicit executive override and justification.</li>
                                <li><strong>Immutable Retraining:</strong> Cross-environment retrains sign manifest hashes and promote through CodePipeline only once RMSE proves stable for 14 days.</li>
                            </ul>
                        </article>
                    </section>

                    <section className={detailStyles.contentGrid}>
                        <article className={detailStyles.contentCard}>
                            <h2>Forecast pipeline blueprint</h2>
                            <p>Blueprinted to operationalize budget certainty: feature hygiene, bounded regression envelopes, and enforced guardrails run in concert so forecasts are auditable and actionable from day one.</p>
                            <ul className={detailStyles.bulletList}>
                                {FORECAST_PIPELINE.map(stage => (
                                    <li key={stage.title}>
                                        <strong>{stage.title}.</strong> {stage.description}
                                    </li>
                                ))}
                            </ul>
                        </article>
                        <article className={detailStyles.contentCard}>
                            <h2>Operational KPIs</h2>
                            <p>Dial in success metrics and how every alert or recommendation converts to owner-assigned actions with dollar impact.</p>
                            <ul className={detailStyles.bulletList}>
                                {FINOPS_KPIS.map(kpi => (
                                    <li key={kpi.label}>
                                        <strong>{kpi.label} - {kpi.value}.</strong> {kpi.detail}
                                    </li>
                                ))}
                            </ul>
                        </article>
                        <article className={detailStyles.contentCard}>
                            <h2>Governance baked into IaC</h2>
                            <p>Governance elements are embedded in the pipeline so policy enforcement is automatic and auditable.</p>
                            <ul className={detailStyles.bulletList}>
                                <li>Trusted feature curation and tag validators reconcile AWS Config, Cost Explorer, and custom metadata to ensure feature hygiene before ingestion.</li>
                                <li>Recommendations convert to Jira tickets with owner, quantifiable dollar impact, and due date.</li>
                                <li>Budgets and anomaly notifications align with Service Control Policies (SCPs) to maintain org-level financial guardrails.</li>
                            </ul>
                        </article>
                    </section>

                    <section className={detailStyles.contentCard}>
                        <h2>What ships with the accelerator</h2>
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
