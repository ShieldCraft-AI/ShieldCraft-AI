import React from 'react';
import InfoCard from './InfoCard';
import styles from './InfoCardsRow.module.css';

export default function InfoCardsRow() {
    return (
        <div className={styles.row}>
            <div className={styles.card}>
                <h3>AWS-Native Foundation</h3>
                <p>
                    Built directly on AWS best-practice architecture with secure
                    multi-account boundaries, deterministic guardrails, and
                    identity-aware telemetry.
                </p>
            </div>

            <div className={styles.card}>
                <h3>GenAI Intelligence Layer</h3>
                <p>
                    Foundation-model scoring, adversarial validation, and
                    governed inference flows that strengthen detection and
                    reduce false positives.
                </p>
            </div>

            <div className={styles.card}>
                <h3>Unified Governance Engine</h3>
                <p>
                    Live correlation of configuration drift, IAM behavior, and
                    cloud events into an auditable, deterministic governance graph.
                </p>
            </div>
        </div>
    );
}
