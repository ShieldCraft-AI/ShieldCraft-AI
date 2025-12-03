import { recommendTier } from './RiskCalculator';

describe('recommendTier deterministic mapping', () => {
    test('low telemetry maps to Starter', () => {
        expect(recommendTier(500, 3)).toBe('Starter');
    });

    test('mid telemetry maps to Pro', () => {
        // telemetry 5,000 + repos 50 * 50 = 2,500 => score 7,500 -> Pro
        expect(recommendTier(5000, 50)).toBe('Pro');
    });

    test('high telemetry maps to Enterprise', () => {
        // telemetry 20,000 + repos 100 * 50 = 5,000 => score 25,000 -> Enterprise
        expect(recommendTier(20000, 100)).toBe('Enterprise');
    });
});
