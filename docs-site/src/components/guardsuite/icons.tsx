import React from 'react';

type IconProps = { width?: number; height?: number; className?: string };

export function IconIntegration({ width = 24, height = 24, className }: IconProps): React.ReactElement {
    return (
        <svg className={className} width={width} height={height} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
            <rect x="2.5" y="3" width="19" height="18" rx="3" stroke="currentColor" strokeWidth="1.5" fill="none" />
            <path d="M7 9h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M7 13h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="8.4" cy="7.8" r="1" fill="currentColor" opacity="0.12" />
            <circle cx="15.6" cy="7.8" r="1" fill="currentColor" opacity="0.12" />
        </svg>
    );
}

export function IconFileList({ width = 24, height = 24, className }: IconProps): React.ReactElement {
    return (
        <svg className={className} width={width} height={height} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
            <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="1.5" fill="none" />
            <path d="M8 9h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M8 13h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M8 17h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    );
}

export function IconBox({ width = 24, height = 24, className }: IconProps): React.ReactElement {
    return (
        <svg className={className} width={width} height={height} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
            <rect x="3.5" y="3.5" width="17" height="17" rx="2" stroke="currentColor" strokeWidth="1.5" fill="none" />
            <path d="M12 6v4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M8 12h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M9 16h6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    );
}

export function IconCheckCircle({ width = 24, height = 24, className }: IconProps): React.ReactElement {
    return (
        <svg className={className} width={width} height={height} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
            <circle cx="12" cy="12" r="8.2" stroke="currentColor" strokeWidth="1.5" fill="none" />
            <path d="M9.4 12.4l1.6 1.6L14.6 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    );
}

export function IconLock({ width = 24, height = 24, className }: IconProps): React.ReactElement {
    return (
        <svg className={className} width={width} height={height} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
            <rect x="4" y="8" width="16" height="12" rx="2" stroke="currentColor" strokeWidth="1.5" fill="none" />
            <path d="M9 11V9a3 3 0 016 0v2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    );
}

export function IconShieldCheck({ width = 24, height = 24, className }: IconProps): React.ReactElement {
    return (
        <svg className={className} width={width} height={height} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
            <path d="M12 3l6 3v5c0 4.4-3.6 8-8 8s-8-3.6-8-8V6l8-3z" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinejoin="round" />
            <path d="M8.5 12h2.5l1 1 3-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    );
}

export function IconData({ width = 24, height = 24, className }: IconProps): React.ReactElement {
    return (
        <svg className={className} width={width} height={height} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
            <ellipse cx="12" cy="8" rx="6" ry="2" stroke="currentColor" strokeWidth="1.5" fill="none" />
            <path d="M6 8v6c0 1.1 2.7 2 6 2s6-0.9 6-2V8" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinejoin="round" />
            <path d="M6 12v4c0 1.1 2.7 2 6 2s6-0.9 6-2v-4" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinejoin="round" />
        </svg>
    );
}

export default null;
