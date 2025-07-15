import React from 'react';
import styles from './LicenseFooter.module.css';

export default function LicenseFooter() {
    return (
        <div className={styles.licenseFooter}>
            <p style={{ fontSize: '0.9em', color: '#bbb', textAlign: 'center', marginTop: '3em' }}>
                License: MIT License
            </p>
        </div>
    );
}
