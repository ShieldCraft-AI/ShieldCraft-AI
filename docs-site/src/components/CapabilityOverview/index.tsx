import React from 'react';

interface CapabilityOverviewProps {
    data: any;
    selectedEnvironment: string;
}

const CapabilityOverview: React.FC<CapabilityOverviewProps> = ({ data, selectedEnvironment }) => {
    const capabilitiesData = data?.capabilities || data?.data?.capabilities;

    if (!capabilitiesData) {
        return (
            <div style={{
                color: 'white',
                background: 'rgba(239, 68, 68, 0.2)',
                border: '1px solid #ef4444',
                borderRadius: '8px',
                padding: '20px',
                textAlign: 'center'
            }}>
                No capabilities data available
            </div>
        );
    }

    const capabilities = Object.entries(capabilitiesData);
    const environmentLabels = {
        dev: 'TRIAL',
        staging: 'STANDARD',
        prod: 'ENTERPRISE'
    };

    return (
        <div style={{
            color: 'white',
            background: 'rgba(30, 41, 59, 0.8)',
            border: '1px solid #475569',
            borderRadius: '12px',
            padding: '30px',
            margin: '20px 0'
        }}>
            <h2 style={{
                color: '#60a5fa',
                textAlign: 'center',
                marginBottom: '20px',
                fontSize: '24px'
            }}>
                🛡️ Architecture Capabilities - {environmentLabels[selectedEnvironment] || selectedEnvironment.toUpperCase()}
            </h2>

            <p style={{
                textAlign: 'center',
                marginBottom: '30px',
                color: '#e2e8f0'
            }}>
                {capabilities.length} core capabilities delivering comprehensive MLOps security platform
            </p>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '20px'
            }}>
                {capabilities.map(([key, capability]: [string, any]) => {
                    const currentEnv = capability.environments?.[selectedEnvironment];
                    const currentCost = currentEnv?.estimated_monthly_cost_usd || 0;

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
                            <h4 style={{
                                color: '#ffffff',
                                margin: '0 0 10px 0',
                                fontSize: '16px'
                            }}>
                                {capability.capability_name}
                            </h4>

                            <p style={{
                                color: '#d1d5db',
                                fontSize: '14px',
                                lineHeight: '1.4',
                                margin: '0 0 15px 0'
                            }}>
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
                                    <span style={{
                                        color: '#34d399',
                                        fontWeight: 'bold',
                                        fontSize: '18px'
                                    }}>
                                        ${currentCost}
                                    </span>
                                    <span style={{
                                        color: '#9ca3af',
                                        fontSize: '12px',
                                        marginLeft: '4px'
                                    }}>
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
    );
};

export default CapabilityOverview;
