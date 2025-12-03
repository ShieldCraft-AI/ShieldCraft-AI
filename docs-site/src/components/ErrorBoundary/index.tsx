import React from 'react';
import Link from '@docusaurus/Link';

type ErrorBoundaryState = { hasError: boolean; error?: any };

export default class ErrorBoundary extends React.Component<React.PropsWithChildren, ErrorBoundaryState> {
    constructor(props: React.PropsWithChildren) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: any): ErrorBoundaryState {
        return { hasError: true, error };
    }

    componentDidCatch(error: any, info: any) {
        // Optional: hook up to telemetry here
    }

    render(): React.ReactNode {
        if (!this.state.hasError) return this.props.children;
        const message = (this.state.error && (this.state.error.message || String(this.state.error))) || 'Unexpected error';
        return (
            <div style={{ padding: '24px 20px' }}>
                <div style={{
                    maxWidth: 760,
                    margin: '40px auto',
                    borderRadius: 16,
                    border: '1px solid var(--ifm-color-emphasis-300)',
                    background: 'var(--ifm-background-surface-color)',
                    boxShadow: '0 14px 30px rgba(0,0,0,.08)'
                }}>
                    <div style={{ padding: 20, borderBottom: '1px solid var(--ifm-color-emphasis-200)' }}>
                        <h1 style={{ margin: 0 }}>Oh dear, something went wrong</h1>
                        <p style={{ margin: '6px 0 0', opacity: .85 }}>An unexpected error occurred while rendering this page.</p>
                    </div>
                    <div style={{ padding: 20 }}>
                        <code style={{ display: 'block', whiteSpace: 'pre-wrap', opacity: .8, fontSize: '.9rem' }}>{message}</code>
                        <div style={{ display: 'flex', gap: 12, marginTop: 16, flexWrap: 'wrap' }}>
                            <button onClick={() => window.location.reload()} className="button button--primary" style={{ cursor: 'pointer' }}>Reload</button>
                            <Link to="/" className="button button--secondary">Go Home</Link>
                            <Link to="/intro" className="button">Open Docs</Link>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}
