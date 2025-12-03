import React from 'react';
import './Skeleton.css';

type SkeletonProps = {
    width?: string | number;
    height?: string | number;
    className?: string;
    'aria-label'?: string;
};

export default function Skeleton({ width = '100%', height = '1rem', className = '', ...rest }: SkeletonProps) {
    const style: React.CSSProperties = {
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
    };

    return <div className={`sc-skeleton ${className}`} style={style} role="status" aria-busy="true" {...rest} />;
}
