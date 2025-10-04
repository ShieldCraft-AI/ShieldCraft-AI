import React, { useState } from 'react';

// HARDCODED DATA - NO ASYNC LOADING
const mockData = {
    capabilities: {
        ingestion: {
            capability_name: "Data Ingestion Pipeline",
            description: "Secure data ingestion from multiple sources with validation and transformation",
            category: "Data Processing",
            environments: {
                dev: { estimated_monthly_cost_usd: 125 },
                staging: { estimated_monthly_cost_usd: 280 },
                prod: { estimated_monthly_cost_usd: 650 }
            }
        },
        processing: {
            capability_name: "ML Data Processing",
            description: "Scalable data processing and feature engineering pipeline",
            category: "Machine Learning",
            environments: {
                dev: { estimated_monthly_cost_usd: 89 },
                staging: { estimated_monthly_cost_usd: 215 },
                prod: { estimated_monthly_cost_usd: 485 }
            }
        },
        storage: {
            capability_name: "Data Lake Storage",
            description: "Secure, scalable data lake with governance and access controls",
            category: "Storage",
            environments: {
                dev: { estimated_monthly_cost_usd: 45 },
                staging: { estimated_monthly_cost_usd: 125 },
                prod: { estimated_monthly_cost_usd: 320 }
            }
        },
        ml: {
            capability_name: "ML Model Training",
            description: "Distributed model training and hyperparameter optimization",
            category: "Machine Learning",
            environments: {
                dev: { estimated_monthly_cost_usd: 150 },
                staging: { estimated_monthly_cost_usd: 420 },
                prod: { estimated_monthly_cost_usd: 890 }
            }
        },
        orchestration: {
            capability_name: "Workflow Orchestration",
            description: "Automated pipeline orchestration and job scheduling",
            category: "Orchestration",
            environments: {
                dev: { estimated_monthly_cost_usd: 35 },
                staging: { estimated_monthly_cost_usd: 85 },
                prod: { estimated_monthly_cost_usd: 180 }
            }
        },
        security: {
            capability_name: "Security & Compliance",
            description: "End-to-end security controls and compliance monitoring",
            category: "Security",
            environments: {
                dev: { estimated_monthly_cost_usd: 75 },
                staging: { estimated_monthly_cost_usd: 145 },
                prod: { estimated_monthly_cost_usd: 290 }
            }
        },
        governance: {
            capability_name: "Data Governance",
            description: "Data lineage, quality monitoring, and access governance",
            category: "Governance",
            environments: {
                dev: { estimated_monthly_cost_usd: 55 },
                staging: { estimated_monthly_cost_usd: 125 },
                prod: { estimated_monthly_cost_usd: 245 }
            }
        },
        observability: {
            capability_name: "Observability & Monitoring",
            description: "Comprehensive monitoring, logging, and alerting system",
            category: "Operations",
            environments: {
                dev: { estimated_monthly_cost_usd: 65 },
                staging: { estimated_monthly_cost_usd: 145 },
                prod: { estimated_monthly_cost_usd: 285 }
            }
        }
    }
};

const ArchitectureDashboard: React.FC = () => {
    const [selectedEnvironment, setSelectedEnvironment] = useState<'dev' | 'staging' | 'prod'>('dev');

    return (
        <div style={{ color: 'white', padding: '20px', minHeight: '100vh' }}>
            <h1 style={{ textAlign: 'center', color: '#60a5fa' }}>Architecture Dashboard</h1>

            <div style={{ textAlign: 'center', margin: '20px 0' }}>
                {['dev', 'staging', 'prod'].map(env => (
                    <button
                        key={env}
                        onClick={() => setSelectedEnvironment(env as any)}
                        style={{
                            margin: '0 10px',
                            padding: '8px 16px',
                            background: selectedEnvironment === env ? '#60a5fa' : '#374151',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }}
                    >
                        {env.toUpperCase()}
                    </button>
                ))}
            </div>

            {/* DIRECT CAPABILITY DISPLAY - NO EXTERNAL COMPONENTS */}
            <div style={{
                color: 'white',
                background: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid #475569',
                borderRadius: '12px',
                padding: '30px',
                margin: '20px 0'
            }}>
                <h2 style={{ color: '#60a5fa', textAlign: 'center', marginBottom: '20px' }}>
                    🛡️ Architecture Capabilities - {selectedEnvironment.toUpperCase()}
                </h2>

                <p style={{ textAlign: 'center', marginBottom: '30px', color: '#e2e8f0' }}>
                    8 core capabilities delivering comprehensive MLOps security platform
                </p>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: '20px'
                }}>
                    {Object.entries(mockData.capabilities).map(([key, capability]) => {
                        const currentCost = capability.environments[selectedEnvironment]?.estimated_monthly_cost_usd || 0;

                        return (
                            <div
                                key={key}
                                style={{
                                    background: 'rgba(30, 41, 59, 0.6)',
                                    border: '1px solid #374151',
                                    borderRadius: '8px',
                                    padding: '20px',
                                    minHeight: '180px'
                                }}
                            >
                                <h4 style={{ color: '#ffffff', margin: '0 0 10px 0', fontSize: '16px' }}>
                                    {capability.capability_name}
                                </h4>

                                <p style={{ color: '#d1d5db', fontSize: '14px', lineHeight: '1.4', margin: '0 0 15px 0' }}>
                                    {capability.description}
                                </p>

                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    borderTop: '1px solid #374151',
                                    paddingTop: '10px'
                                }}>
                                    <div>
                                        <span style={{ color: '#34d399', fontWeight: 'bold', fontSize: '18px' }}>
                                            ${currentCost}
                                        </span>
                                        <span style={{ color: '#9ca3af', fontSize: '12px', marginLeft: '4px' }}>
                                            /month
                                        </span>
                                    </div>
                                    <div style={{
                                        background: 'rgba(96, 165, 250, 0.2)',
                                        color: '#60a5fa',
                                        fontSize: '11px',
                                        padding: '4px 8px',
                                        borderRadius: '4px',
                                        textTransform: 'uppercase'
                                    }}>
                                        {capability.category}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default ArchitectureDashboard;
