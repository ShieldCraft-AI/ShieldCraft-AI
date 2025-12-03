import React, { useState } from 'react';

/**
 * recommendTier - deterministic mapping from telemetry inputs to product tier.
 *
 * Determinism guarantees:
 * - No randomness used.
 * - No time-based variance (pure function of inputs).
 * - Stable thresholds: identical inputs always return the same tier.
 *
 * Keep the algorithm unchanged; this export allows a static unit test
 * to assert deterministic behavior across runtime environments.
 */
export function recommendTier(telemetryPerDay: number, repos: number) {
    // Simple deterministic heuristic using thresholds (UNCHANGED)
    const score = telemetryPerDay + repos * 50; // repo weighting
    if (score <= 1000) return 'Starter';
    if (score <= 10000) return 'Pro';
    return 'Enterprise';
}

export default function RiskCalculator(): React.ReactElement {
    const [telemetry, setTelemetry] = useState<number>(500);
    const [repos, setRepos] = useState<number>(3);

    const tier = recommendTier(telemetry, repos);
    const hoursSaved = Math.max(1, Math.round((telemetry * 0.002) * 100) / 100); // heuristic
    const penaltyAvoided = Math.round((telemetry / 1000) * 120);

    return (
        <section className="vs-risk container" aria-labelledby="risk-title">
            <h2 id="risk-title" className="vs-section-title">Risk Calculator</h2>
            <div className="vs-risk__inner">
                <div className="vs-risk__controls">
                    <label>
                        Telemetry/day
                        <input
                            type="range"
                            min={0}
                            max={50000}
                            step={100}
                            value={telemetry}
                            onChange={(e) => setTelemetry(Number(e.target.value))}
                        />
                        <div className="vs-risk__value">{telemetry.toLocaleString()}</div>
                    </label>

                    <label>
                        Repositories
                        <input
                            type="number"
                            min={1}
                            max={1000}
                            value={repos}
                            onChange={(e) => setRepos(Math.max(1, Number(e.target.value)))}
                        />
                    </label>
                </div>

                <div className="vs-risk__output">
                    <div className="vs-risk__box vs-card">
                        <strong>Recommended Tier</strong>
                        <div className="vs-risk__tier">{tier}</div>
                    </div>

                    <div className="vs-risk__box vs-card">
                        <strong>Hours triage avoided / month</strong>
                        <div>{hoursSaved.toLocaleString()}</div>
                    </div>

                    <div className="vs-risk__box vs-card">
                        <strong>Reduced risk</strong>
                        <div>High</div>
                    </div>
                </div>
            </div>
        </section>
    );
}
