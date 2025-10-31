import React from 'react';
import { render, screen } from '@testing-library/react';

test('ServicePill renders without hook error', async () => {
    const mod = require('@site/src/pages/pricing');
    const ServicePill = mod.ServicePill;
    render(React.createElement(ServicePill, { label: 'Amazon EventBridge' }));
    expect(await screen.findByText(/EventBridge/)).toBeTruthy();
});
