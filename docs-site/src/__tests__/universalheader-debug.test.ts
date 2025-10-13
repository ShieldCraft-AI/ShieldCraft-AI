test('debug react resolution when importing UniversalHeader', async () => {
    await jest.isolateModulesAsync(async () => {
        try {
            // resolved from test runner context
            // eslint-disable-next-line no-console
            console.error('[debug] react resolved (before):', require.resolve('react'));
        } catch (e) {
            // eslint-disable-next-line no-console
            console.error('[debug] react resolve before failed', e && e.message);
        }

        try {
            // import the component (may trigger other imports)
            // eslint-disable-next-line @typescript-eslint/no-var-requires
            const UH = require('@site/src/components/UniversalHeader');
            // eslint-disable-next-line no-console
            console.error('[debug] UniversalHeader loaded OK');
        } catch (err) {
            // eslint-disable-next-line no-console
            console.error('[debug] requiring UniversalHeader threw:', err && err.message);
        }

        try {
            // eslint-disable-next-line no-console
            console.error('[debug] react resolved (after):', require.resolve('react'));
        } catch (e) {
            // eslint-disable-next-line no-console
            console.error('[debug] react resolve after failed', e && e.message);
        }
    });
});
