import React from 'react';
import PortalLayout from '../components/PortalLayout';
import styles from './dashboard-simple.module.css';

// Simple mock data for showcase
const mockCards = [
    {
        id: 'datalake',
        title: 'Data Lake',
        metrics: [
            { label: 'Used', value: '1.42 TB' },
            { label: 'Utilization', value: '71%' },
            { label: 'Growth', value: '+2.4%' }
        ],
        chartType: 'donut',
        status: 'healthy'
    },
    {
        id: 'api-latency',
        title: 'API Latency',
        metrics: [
            { label: 'P50', value: '124ms' },
            { label: 'P95', value: '287ms' },
            { label: 'Errors', value: '0.02%' }
        ],
        chartType: 'line',
        status: 'healthy'
    },
    {
        id: 'resources',
        title: 'Resource Usage',
        metrics: [
            { label: 'CPU', value: '65%' },
            { label: 'Memory', value: '70%' },
            { label: 'Storage', value: '45%' }
        ],
        chartType: 'gauges',
        status: 'healthy'
    },
    {
        id: 'active-users',
        title: 'Active Users',
        metrics: [
            { label: 'Current', value: '2,847' },
            { label: 'Peak', value: '3,122' },
            { label: '24h Change', value: '+12%' }
        ],
        chartType: 'area',
        status: 'healthy'
    },
    {
        id: 'threats',
        title: 'Threat Analysis',
        metrics: [
            { label: 'Critical', value: '0' },
            { label: 'High', value: '3' },
            { label: 'Medium', value: '12' }
        ],
        chartType: 'heatmap',
        status: 'healthy'
    },
    {
        id: 'processing',
        title: 'Processing Pipeline',
        metrics: [
            { label: 'Queue', value: '1,234' },
            { label: 'Rate', value: '45/min' },
            { label: 'Errors', value: '0' }
        ],
        chartType: 'bar',
        status: 'healthy'
    }
];

// Simple chart placeholders - no complex Plotly, just visual representations
function ChartPlaceholder({ type, title }: { type: string; title: string }) {
    const getChartContent = () => {
        switch (type) {
            case 'donut':
                return (
                    <div className={styles.donutChart}>
                        <div className={styles.donutRing}>
                            <span className={styles.donutLabel}>71%</span>
                        </div>
                    </div>
                );
            case 'line':
                return (
                    <div className={styles.lineChart}>
                        <svg viewBox="0 0 300 120" className={styles.chartSvg}>
                            <polyline
                                fill="none"
                                stroke="#22d3ee"
                                strokeWidth="2"
                                points="20,80 60,60 100,70 140,50 180,65 220,45 260,55 300,40"
                            />
                        </svg>
                    </div>
                );
            case 'gauges':
                return (
                    <div className={styles.gaugeChart}>
                        <div className={styles.gauge}>
                            <div className={styles.gaugeLabel}>CPU</div>
                            <div className={styles.gaugeValue}>65%</div>
                        </div>
                        <div className={styles.gauge}>
                            <div className={styles.gaugeLabel}>RAM</div>
                            <div className={styles.gaugeValue}>70%</div>
                        </div>
                    </div>
                );
            case 'area':
                return (
                    <div className={styles.areaChart}>
                        <svg viewBox="0 0 300 120" className={styles.chartSvg}>
                            <defs>
                                <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                    <stop offset="0%" stopColor="#a78bfa" stopOpacity="0.3" />
                                    <stop offset="100%" stopColor="#a78bfa" stopOpacity="0" />
                                </linearGradient>
                            </defs>
                            <path
                                fill="url(#areaGradient)"
                                stroke="#a78bfa"
                                strokeWidth="2"
                                d="M20,90 L60,70 L100,75 L140,60 L180,80 L220,55 L260,65 L300,50 L300,120 L20,120 Z"
                            />
                        </svg>
                    </div>
                );
            case 'heatmap':
                return (
                    <div className={styles.heatmapChart}>
                        <div className={styles.heatmapGrid}>
                            {Array.from({ length: 25 }, (_, i) => (
                                <div
                                    key={i}
                                    className={styles.heatmapCell}
                                    style={{
                                        opacity: Math.random() * 0.8 + 0.1,
                                        backgroundColor: i < 5 ? '#ef4444' : i < 15 ? '#f59e0b' : '#22d3ee'
                                    }}
                                />
                            ))}
                        </div>
                    </div>
                );
            case 'bar':
                return (
                    <div className={styles.barChart}>
                        <svg viewBox="0 0 300 120" className={styles.chartSvg}>
                            {[40, 65, 80, 45, 90, 55, 70].map((height, i) => (
                                <rect
                                    key={i}
                                    x={20 + i * 40}
                                    y={120 - height}
                                    width={30}
                                    height={height}
                                    fill="#f472b6"
                                    opacity="0.8"
                                />
                            ))}
                        </svg>
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

function DashboardCard({ card }: { card: typeof mockCards[0] }) {
    return (
        <div className={styles.card}>
            <div className={styles.cardHeader}>
                <h3 className={styles.cardTitle}>{card.title}</h3>
                <div className={`${styles.statusDot} ${styles[card.status]}`} />
            </div>

            <div className={styles.metrics}>
                {card.metrics.map((metric) => (
                    <div key={metric.label} className={styles.metric}>
                        <div className={styles.metricLabel}>{metric.label}</div>
                        <div className={styles.metricValue}>{metric.value}</div>
                    </div>
                ))}
            </div>

            <ChartPlaceholder type={card.chartType} title={card.title} />
        </div>
    );
}

export default function SimpleDashboard() {
    return (
        <PortalLayout title="Dashboard" description="ShieldCraft AI Dashboard">
            <div className={styles.dashboard}>
                <div className={styles.dashboardGrid}>
                    {mockCards.map((card) => (
                        <DashboardCard key={card.id} card={card} />
                    ))}
                </div>
            </div>
        </PortalLayout>
    );
}
