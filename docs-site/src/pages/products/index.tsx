import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

export default function ProductsIndex(): JSX.Element {
    return (
        <Layout title="Products" description="ShieldCraft product listing">
            <main style={{ padding: '48px 16px', maxWidth: 1100, margin: '0 auto' }}>
                <h1 style={{ marginBottom: 16 }}>Products</h1>
                <p style={{ marginBottom: 24 }}>Explore our product offerings and demos.</p>
                <ul>
                    <li>
                        <Link to="/products/vectorscan">VectorScan - deterministic IaC scanning</Link>
                    </li>
                    <li>
                        <Link to="/guard-suite">Guard Suite - governance and enforcement</Link>
                    </li>
                </ul>
            </main>
        </Layout>
    );
}
