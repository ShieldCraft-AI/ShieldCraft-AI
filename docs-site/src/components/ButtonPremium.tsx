import React from 'react';
import styles from './ButtonPremium.module.css';

type PremiumButtonProps = {
    children: React.ReactNode;
    onClick?: () => void;
    disabled?: boolean;
    variant?: 'primary' | 'secondary';
    className?: string;
};

function resolveClassName(className?: string): string {
    if (!className) return '';
    return className
        .split(' ')
        .filter(Boolean)
        .map(token => styles[token] ?? token)
        .join(' ');
}

export default function PremiumButton({ children, onClick, disabled, variant = 'primary', className }: PremiumButtonProps) {
    const baseClass =
        variant === 'secondary'
            ? `${styles.premium} ${styles.secondary}`
            : styles.premium;
    const extraClass = resolveClassName(className);
    const buttonClass = [baseClass, extraClass].filter(Boolean).join(' ');
    return (
        <button
            className={buttonClass}
            onClick={onClick}
            disabled={disabled}
            aria-pressed={false}
            tabIndex={0}
        >
            {children}
        </button>
    );
}
