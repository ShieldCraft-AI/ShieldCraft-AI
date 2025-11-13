import logger from '@site/src/utils/logger';
test('debug react resolution when importing UniversalHeader', async () => {
    await jest.isolateModulesAsync(async () => {
        try {
            // resolved from test runner context
            logger.error('[debug] react resolved (before):', require.resolve('react'));
        } catch (e) {
            logger.error('[debug] react resolve before failed', e && e.message);
        }

        try {
            // import the component (may trigger other imports)
            // eslint-disable-next-line @typescript-eslint/no-var-requires
            const UH = require('@site/src/components/UniversalHeader');
            logger.error('[debug] UniversalHeader loaded OK');
        } catch (err) {
            logger.error('[debug] requiring UniversalHeader threw:', err && err.message);
        }

        try {
            logger.error('[debug] react resolved (after):', require.resolve('react'));
        } catch (e) {
            logger.error('[debug] react resolve after failed', e && e.message);
        }
    });
});
