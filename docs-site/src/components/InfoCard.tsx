import React from 'react';
import styles from './InfoCard.module.css';
import Link from '@docusaurus/Link';

interface InfoCardProps {
    title: string;
    icon?: React.ReactNode;
    description: string;
    link?: string;
}

export default function InfoCard({ title, icon, description, link }: InfoCardProps) {
    const content = (
        <>
            {icon && <div className={styles.icon}>{icon}</div>}
            <h3 className={styles.title}>{title}</h3>
            <p className={styles.description}>{description}</p>
        </>
    );

    if (link) {
        return (
            <Link to={link} className={styles.cardLink}>
                <div className={styles.card}>
                    {content}
                </div>
            </Link>
        );
    }

    return (
        <div className={styles.card}>
            {content}
        </div>
    );
}
