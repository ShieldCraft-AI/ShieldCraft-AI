import React from 'react';
import styles from './card.module.css';

export type WindowKey = '1h' | '24h' | '7d' | '30d' | '90d';

type Props = {
    value: WindowKey;
    onChange: (w: WindowKey) => void;
};

const OPTIONS: WindowKey[] = ['1h', '24h', '7d', '30d', '90d'];

export default function TimeframeControls({ value, onChange }: Props) {
    return (
        <div className={styles.timeControls}>
            <div className={styles.windowBtns} role="tablist" aria-label="Time window">
                {OPTIONS.map((opt) => (
                    <button
                        key={opt}
                        className={opt === value ? styles.btnActive : styles.btn}
                        onClick={() => onChange(opt)}
                        role="tab"
                        aria-selected={opt === value}
                    >
                        {opt}
                    </button>
                ))}
            </div>
        </div>
    );
}
