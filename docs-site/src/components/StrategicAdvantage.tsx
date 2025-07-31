import styles from './StrategicAdvantage.module.css';

export default function StrategicAdvantage() {
    return (
        <section className={styles.advantageSection}>
            <div style={{ width: '100%', maxWidth: 1200, margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <h3 className={styles.center} style={{ fontSize: '1.6em', color: '#a5b4fc', marginBottom: '0.7em' }}>
                    ShieldCraft AI: Engineered for Autonomous, Adaptive Cloud Security
                </h3>
                <div style={{ maxWidth: 1100, margin: '0 auto 1.1em auto' }}>
                    <p className={styles.center} style={{ fontSize: '1.15em', fontWeight: 500, color: '#eee' }}>
                        ShieldCraft AI unifies the most advanced AWS technologies to deliver proactive, intelligent, and resilient cloud defense. Every layer is architected for speed, automation, and continuous adaptation.
                    </p>
                </div>
                <div style={{ display: 'flex', justifyContent: 'center', margin: '0 auto 1.2em auto' }}>
                    <div style={{ textAlign: 'left', lineHeight: 1.7, color: '#e3e6ee', maxWidth: 900 }}>
                        <div><b><a href="https://aws.amazon.com/sagemaker/" target="_blank" rel="noopener noreferrer">SageMaker</a></b> for predictive threat detection and generative attack emulation</div>
                        <div><b><a href="https://aws.amazon.com/msk/" target="_blank" rel="noopener noreferrer">MSK</a></b> for real-time security data streaming</div>
                        <div><b><a href="https://aws.amazon.com/lambda/" target="_blank" rel="noopener noreferrer">Lambda</a></b> for event-driven, autonomous remediation</div>
                        <div><b><a href="https://aws.amazon.com/glue/" target="_blank" rel="noopener noreferrer">Glue</a></b> & <b><a href="https://aws.amazon.com/lake-formation/" target="_blank" rel="noopener noreferrer">Lake Formation</a></b> for governed, scalable data pipelines</div>
                        <div><b><a href="https://aws.amazon.com/opensearch-service/" target="_blank" rel="noopener noreferrer">OpenSearch</a></b> for rapid, actionable analytics</div>
                        <div><b><a href="https://aws.amazon.com/secrets-manager/" target="_blank" rel="noopener noreferrer">Secrets Manager</a></b> for centralized, secure credential management</div>
                        <div><b><a href="https://aws.amazon.com/security/" target="_blank" rel="noopener noreferrer">Attack Simulation</a></b> and <b><a href="https://aws.amazon.com/architecture/security/" target="_blank" rel="noopener noreferrer">Cloud Native Hardening</a></b> for continuous validation and resilience</div>
                        <div><b><a href="https://aws.amazon.com/step-functions/" target="_blank" rel="noopener noreferrer">Step Functions</a></b> for orchestrating complex workflows</div>
                        <div><b><a href="https://aws.amazon.com/eventbridge/" target="_blank" rel="noopener noreferrer">EventBridge</a></b> for seamless, real-time integration</div>
                        <div><b><a href="https://aws.amazon.com/detective/" target="_blank" rel="noopener noreferrer">AWS Detective</a></b> for deep, actionable threat investigations</div>
                    </div>
                </div>
                <div style={{ maxWidth: 1100, margin: '0 auto 0.7em auto' }}>
                    <p className={styles.center} style={{ fontSize: '1.1em', color: '#eee' }}>
                        ShieldCraft AI empowers your enterprise to anticipate, adapt, and autonomously defeat threats, delivering the speed, intelligence, and control needed to stay ahead in the modern cloud.
                    </p>
                </div>
            </div>
        </section>
    );
}
