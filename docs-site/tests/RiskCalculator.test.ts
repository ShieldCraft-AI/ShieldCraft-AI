import { recommendTier } from '../src/components/guardsuite/RiskCalculator';

describe('recommendTier deterministic mapping (docs-site tests)', () => {
    test('low telemetry maps to Starter', () => {
        expect(recommendTier(500, 3)).toBe('Starter');
    });

    test('mid telemetry maps to Pro', () => {
        expect(recommendTier(5000, 50)).toBe('Pro');
    });

    test('high telemetry maps to Enterprise', () => {
        expect(recommendTier(20000, 100)).toBe('Enterprise');
    });
});
