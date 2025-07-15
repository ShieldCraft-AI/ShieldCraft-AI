import styles from './StrategicAdvantage.module.css';

export default function StrategicAdvantage() {
    return (
        <section className={styles.advantageSection}>
            <h3 className={styles.center}>Redefining Enterprise Security in the Cloud</h3>
            <p className={styles.center}>
                ShieldCraft AI brings together the most advanced AWS technologies: SageMaker for intelligent threat detection, MSK for real-time data streaming,
            </p>
            <p className={styles.center}>
                Lambda for responsive automation, Glue and Lake Formation for secure, governed data pipelines, and OpenSearch for rapid analytics.
            </p>
            <p className={styles.center}>
                Centralized secrets management, automated attack simulation, and cloud-native hardening ensure your defenses are always adaptive and resilient.
            </p>
            <p className={styles.center}>
                Step Functions orchestrate every workflow, EventBridge enables seamless integration, and AWS Detective powers deep, actionable threat investigations.
            </p>
            <p className={styles.center}>
                Designed for and trusted by security leaders, ShieldCraft AI delivers the speed, intelligence, and control needed to stay ahead of evolving cyber threats making it your strategic advantage in the cloud.
            </p>
        </section>
    );
}
