import React from 'react';

export default function AccessibilityHints(): JSX.Element {
    return (
        <div style={{ fontSize: 12, color: 'var(--muted-1)', marginTop: 8 }}>
            <div>Keyboard: use <kbd>Tab</kbd> to focus CTAs.</div>
            <div>Reduced-motion respected via OS preferences.</div>
        </div>
    );
}
