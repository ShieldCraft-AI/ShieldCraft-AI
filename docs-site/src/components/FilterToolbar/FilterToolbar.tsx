import React from 'react';
import styles from './FilterToolbar.module.css';

export interface FilterOption {
    value: string;
    label: string;
    count?: number;
}

export interface FilterGroup {
    label?: string;
    options: FilterOption[];
    activeValue: string;
    onChange: (value: string) => void;
    multiColumn?: boolean; // For wrapping into multiple rows
}

interface FilterToolbarProps {
    groups: FilterGroup[];
    summaryStats?: React.ReactNode; // Optional stats bar
    className?: string;
}

export default function FilterToolbar({ groups, summaryStats, className }: FilterToolbarProps) {
    return (
        <div className={`${styles.filterToolbar} ${className || ''}`}>
            {summaryStats && (
                <div className={styles.summaryBar}>
                    {summaryStats}
                </div>
            )}
            <div className={styles.filterGroups}>
                {groups.map((group, idx) => (
                    <div
                        key={idx}
                        className={`${styles.filterGroup} ${group.multiColumn ? styles.multiColumn : ''}`}
                        role="group"
                        aria-label={group.label}
                    >
                        {group.label && <span className={styles.groupLabel}>{group.label}:</span>}
                        <div className={styles.pillRow}>
                            {group.options.map((option) => (
                                <button
                                    key={option.value}
                                    className={styles.pill}
                                    aria-pressed={group.activeValue === option.value}
                                    onClick={() => group.onChange(option.value)}
                                >
                                    {option.label}
                                    {option.count !== undefined && (
                                        <span className={styles.pillCount}>{option.count}</span>
                                    )}
                                </button>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
