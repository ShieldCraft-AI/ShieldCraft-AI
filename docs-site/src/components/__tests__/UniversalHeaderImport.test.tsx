import React from 'react';

test('import UniversalHeader diagnostic', () => {
    // ensure mocks are applied (jest.config moduleNameMapper will map Docusaurus imports)
    // require rather than import to allow jest.resetModules cycles in other tests
    const mod = require('@site/src/components/UniversalHeader');
    // eslint-disable-next-line no-console
    console.error('[diag] UniversalHeader module keys', Object.keys(mod));
    const comp = mod.default || mod;
    // eslint-disable-next-line no-console
    console.error('[diag] typeof comp', typeof comp);
    // Try creating an element without rendering to ensure it's a valid component
    const el = React.createElement(comp);
    // eslint-disable-next-line no-console
    console.error('[diag] created element type', typeof el.type);
    expect(typeof comp === 'function' || typeof comp === 'object').toBeTruthy();
    expect(el).toBeTruthy();
});
