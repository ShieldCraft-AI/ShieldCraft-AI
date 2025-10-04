import React from 'react';
import InfoCard from './InfoCard';
import styles from './InfoCardsRow.module.css';

export default function InfoCardsRow() {
    return (
        <section className={styles.rowSection}>
            <div className={styles.rowContainer}>
                <InfoCard
                    title="AWS-Native Architecture"
                    icon={<img src="/aws-icons/Amazon-VPC.svg" alt="AWS VPC" style={{ width: 48, height: 48 }} />}
                    description="Explore the resilient, scalable, and secure AWS foundation that powers ShieldCraft AI's advanced MLOps and security capabilities."
                    link="/aws_stack_architecture"
                />
                <InfoCard
                    title="Generative AI Core"
                    icon={<img src="/aws-icons/Arch_Amazon-SageMaker_48.svg" alt="GenAI" style={{ width: 48, height: 48 }} />}
                    description="Discover how we leverage foundational models for proactive threat simulation, prediction, and autonomous defense."
                    link="/generative_ai_core"
                />
            </div>
        </section>
    );
}
