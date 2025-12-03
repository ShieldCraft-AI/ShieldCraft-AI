import React from 'react';
import styles from './SectionTitle.module.css';

export default function SectionHeader({ title, subtitle }: { title: string; subtitle?: string }) {
    return (
        <header className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>{title}</h2>
            {subtitle ? <p className={styles.sectionSubtitle}>{subtitle}</p> : null}
        </header>
    );
}
