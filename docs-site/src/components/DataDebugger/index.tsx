import React, { useState, useEffect } from 'react';

const DataDebugger: React.FC = () => {
    const [data, setData] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadData = async () => {
            try {
                const response = await fetch('/data/architecture_discovery.json');

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                if (data.service_matrix) {
                    const firstService = Object.keys(data.service_matrix)[0];
                }

                if (data.capabilities) {
                    // capabilities present
                }

                setData(data);
            } catch (err) {
                console.error('Error loading data:', err);
                setError(err instanceof Error ? err.message : 'Unknown error');
            }
        };

        loadData();
    }, []);

    if (error) {
        return (
            <div style={{ padding: '20px', background: '#fee', border: '1px solid #fcc', borderRadius: '8px', margin: '20px' }}>
                <h3>Debug: Data Loading Error</h3>
                <p><strong>Error:</strong> {error}</p>
                <p>Check the browser console for more details.</p>
            </div>
        );
    }

    if (!data) {
        return (
            <div style={{ padding: '20px', background: '#ffe', border: '1px solid #ffc', borderRadius: '8px', margin: '20px' }}>
                <h3>Debug: Loading Data...</h3>
            </div>
        );
    }

};

export default DataDebugger;
