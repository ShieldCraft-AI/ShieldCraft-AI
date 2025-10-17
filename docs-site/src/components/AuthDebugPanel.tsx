import React from 'react';

type LogEntry = { ts: string; msg: string; data?: any };

function CopyButton({ logs }: { logs: LogEntry[] }) {
    const [copied, setCopied] = React.useState(false);
    const onCopy = async () => {
        try {
            const text = logs.length === 0 ? '' : logs.map((l) => `${l.ts} ${l.msg}\n${l.data ? JSON.stringify(l.data, null, 2) : ''}`).join('\n---\n');
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 1800);
        } catch (e) {
            try { await navigator.clipboard.writeText(JSON.stringify(logs, null, 2)); setCopied(true); setTimeout(() => setCopied(false), 1800); } catch { /* ignore */ }
        }
    };
    return (
        <button
            onClick={onCopy}
            title="Copy debug logs to clipboard"
            aria-label="Copy debug logs"
            style={{ background: 'transparent', color: copied ? '#7ef' : '#9aa', border: '1px solid rgba(255,255,255,0.04)', padding: '6px 8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
        >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
                <path d="M16 21H8a2 2 0 0 1-2-2V7h2v12h8v2z" fill="currentColor" />
                <path d="M20 3H10a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10V5a2 2 0 0 0-2-2z" stroke="currentColor" strokeWidth="0" fill="currentColor" />
            </svg>
            <span style={{ fontSize: 12 }}>{copied ? 'Copied' : ''}</span>
        </button>
    );
}

function isAuthRelevant(entry: LogEntry): boolean {
    try {
        const m = (entry.msg || '').toLowerCase();
        // match key debug tokens we care about
        const keywords = [
            '[auth-cognito]',
            '[auth-debug]',
            'refreshauthstate',
            'tokenexchange',
            'token exchange',
            'redirecturi',
            'redirecting to hosted ui',
            'amplify config',
            '__sc_oauth',
            'persistauthsnapshottostorage',
            'sc-auth-change',
            'notifyauthchange',
            'lastauthuser',
            'cognitoidentityserviceprovider',
        ];
        for (const k of keywords) if (m.includes(k)) return true;
        // also include storage events and hub/auth mentions
        if (m.includes('storage') || m.includes('hub') || m.includes('auth')) return true;
        return false;
    } catch {
        return false;
    }
}

export default function AuthDebugPanel(): JSX.Element | null {
    const isDevHost = (): boolean => {
        try {
            if (typeof window === 'undefined') return false;
            const h = window.location.hostname || '';
            return h === 'localhost' || h === '127.0.0.1' || h === '::1' || h.endsWith('.local') || h.endsWith('.test');
        } catch {
            return false;
        }
    };
    const STORAGE_ENABLED_KEY = 'sc_auth_debug_enabled';
    const STORAGE_LOGS_KEY = 'sc_auth_debug_logs';

    const [visible, setVisible] = React.useState<boolean>(() => {
        try {
            // show if explicitly enabled via global flag, URL flag, or previous session
            if (typeof window !== 'undefined') {
                const urlHasDebug = window.location.search.includes('sc_debug=1');
                const prev = sessionStorage.getItem(STORAGE_ENABLED_KEY) === '1';
                // Only show in development hosts to avoid leaking debug UI into staging/prod.
                return isDevHost() && Boolean((window as any).__SC_AUTH_DEBUG__ || urlHasDebug || prev);
            }
        } catch (e) { /* ignore */ }
        return true;
    });

    const [logs, setLogs] = React.useState<LogEntry[]>(() => {
        try {
            if (typeof window !== 'undefined') {
                const raw = localStorage.getItem(STORAGE_LOGS_KEY);
                if (raw) return JSON.parse(raw) as LogEntry[];
            }
        } catch (e) { /* ignore parse errors */ }
        return [];
    });
    const STORAGE_POS_KEY = 'sc_auth_debug_pos';

    const STORAGE_COMPACT_KEY = 'sc_auth_debug_compact';
    const [compact, setCompact] = React.useState<boolean>(() => {
        try {
            if (typeof window !== 'undefined') {
                return localStorage.getItem(STORAGE_COMPACT_KEY) === '1';
            }
        } catch { /* ignore */ }
        return true;
    });

    const [pos, setPos] = React.useState<{ right: number; top: number }>(() => {
        try {
            if (typeof window !== 'undefined') {
                const raw = localStorage.getItem(STORAGE_POS_KEY);
                if (raw) return JSON.parse(raw) as { right: number; top: number };
            }
        } catch (e) { /* ignore */ }
        return { right: 0, top: 120 };
    });

    React.useEffect(() => {
        const handler = (ev: Event) => {
            try {
                const detail = (ev as CustomEvent).detail || {};
                const entry: LogEntry = {
                    ts: new Date().toISOString(),
                    msg: String(detail.msg ?? detail),
                    data: detail.data,
                };
                setLogs((prev) => {
                    const next = prev.concat(entry).slice(-500);
                    try { localStorage.setItem(STORAGE_LOGS_KEY, JSON.stringify(next)); } catch (e) { /* ignore */ }
                    return next;
                });
            } catch { /* ignore */ }
        };
        window.addEventListener('sc-auth-log', handler as EventListener);
        return () => window.removeEventListener('sc-auth-log', handler as EventListener);
    }, []);

    // persist visible flag across reloads/redirects
    React.useEffect(() => {
        try { localStorage.setItem(STORAGE_ENABLED_KEY, visible ? '1' : '0'); } catch (e) { /* ignore */ }
    }, [visible]);

    React.useEffect(() => {
        try { localStorage.setItem(STORAGE_COMPACT_KEY, compact ? '1' : '0'); } catch (e) { /* ignore */ }
    }, [compact]);

    if (typeof window === 'undefined') return null;
    // Never mount debug UI on non-development hosts.
    if (!isDevHost()) return null;
    // only mount the panel when debug mode is explicitly enabled either now or previously
    if (!((window as any).__SC_AUTH_DEBUG__) && localStorage.getItem(STORAGE_ENABLED_KEY) !== '1' && !window.location.search.includes('sc_debug=1')) {
        return null;
    }

    const panelStyle: React.CSSProperties = {
        position: 'fixed',
        right: pos.right,
        top: pos.top,
        width: '580px',
        maxHeight: '60vh',
        background: 'rgba(17,17,17,0.95)',
        color: '#e6e6e6',
        fontSize: '12px',
        zIndex: 9999,
        boxShadow: '-4px 4px 24px rgba(0,0,0,0.6)',
        display: 'flex',
        flexDirection: 'column',
    };

    const headerStyle: React.CSSProperties = {
        padding: '6px 8px',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
    };

    const bodyStyle: React.CSSProperties = {
        overflow: 'auto',
        padding: '8px',
        lineHeight: 1.3,
    };


    // Drag handling using pointer events for robust start/stop semantics
    const dragRef = React.useRef<{ startX: number; startY: number; startRight: number; startTop: number; pointerId?: number; move?: (ev: PointerEvent) => void; up?: (ev: PointerEvent) => void } | null>(null);

    const startDrag = (ev: React.MouseEvent | React.TouchEvent | React.PointerEvent) => {
        try {
            // prefer pointer events, fallback to mouse/touch
            const isPointer = (ev as React.PointerEvent).pointerId !== undefined;
            const clientX = isPointer ? (ev as React.PointerEvent).clientX : ((ev as React.TouchEvent).touches ? (ev as React.TouchEvent).touches[0].clientX : (ev as React.MouseEvent).clientX);
            const clientY = isPointer ? (ev as React.PointerEvent).clientY : ((ev as React.TouchEvent).touches ? (ev as React.TouchEvent).touches[0].clientY : (ev as React.MouseEvent).clientY);

            const pointerId = isPointer ? (ev as React.PointerEvent).pointerId : undefined;

            const onMove = (e: PointerEvent) => {
                try {
                    const x = e.clientX;
                    const y = e.clientY;
                    const dx = x - dragRef.current!.startX;
                    const dy = y - dragRef.current!.startY;
                    const newRight = Math.max(0, Math.round(dragRef.current!.startRight - dx));
                    const newTop = Math.max(0, Math.round(dragRef.current!.startTop + dy));
                    setPos({ right: newRight, top: newTop });
                } catch (err) { /* ignore */ }
            };

            const onUp = (e: PointerEvent) => {
                try {
                    // if pointerId is set, ensure the up matches
                    if (dragRef.current && dragRef.current.pointerId !== undefined && e.pointerId !== dragRef.current.pointerId) return;
                    // persist and cleanup
                    try { localStorage.setItem(STORAGE_POS_KEY, JSON.stringify(pos)); } catch (er) { /* ignore */ }
                } finally {
                    if (dragRef.current) {
                        if (dragRef.current.move) window.removeEventListener('pointermove', dragRef.current.move);
                        if (dragRef.current.up) window.removeEventListener('pointerup', dragRef.current.up);
                        window.removeEventListener('pointercancel', dragRef.current.up as any);
                        dragRef.current = null;
                    }
                }
            };

            dragRef.current = { startX: clientX, startY: clientY, startRight: pos.right, startTop: pos.top, pointerId, move: onMove, up: onUp };
            // ensure pointer capture across the window
            window.addEventListener('pointermove', onMove);
            window.addEventListener('pointerup', onUp);
            window.addEventListener('pointercancel', onUp);
            // prevent default to avoid accidental text selection / page scroll on touch
            if ((ev as React.TouchEvent).preventDefault) try { (ev as React.TouchEvent).preventDefault(); } catch { /* ignore */ }
        } catch (e) { /* ignore */ }
    };

    return (
        <div style={panelStyle} aria-hidden={!visible}>
            <div style={{ ...headerStyle, cursor: 'grab' }} onMouseDown={startDrag} onTouchStart={startDrag}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ fontWeight: 700 }}>Auth Debug</div>
                    <div style={{ fontSize: 11, opacity: 0.6 }}>(drag to reposition)</div>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <CopyButton logs={logs} />
                    <label style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: '#9aa', fontSize: 12 }} title="Show only auth-related logs">
                        <input type="checkbox" checked={compact} onChange={(e) => setCompact(e.target.checked)} />
                        Compact
                    </label>
                    <button
                        onClick={() => {
                            setLogs([]);
                            try { localStorage.removeItem(STORAGE_LOGS_KEY); } catch (e) { /* ignore */ }
                        }}
                        style={{ background: 'transparent', color: '#9aa', border: '1px solid rgba(255,255,255,0.04)', padding: '4px 6px', cursor: 'pointer' }}
                    >Clear</button>
                    <button
                        onClick={() => setVisible((v) => !v)}
                        style={{ background: 'transparent', color: '#9aa', border: '1px solid rgba(255,255,255,0.04)', padding: '4px 6px', cursor: 'pointer' }}
                    >{visible ? 'Hide' : 'Show'}</button>
                </div>
            </div>
            {visible && (
                <div style={bodyStyle}>
                    {logs.length === 0 ? (
                        <div style={{ opacity: 0.7 }}>No auth logs yet.</div>
                    ) : (
                        // Optionally filter to compact auth-focused entries
                        (compact ? logs.filter(isAuthRelevant) : logs).slice().reverse().map((l, i) => (
                            <div key={i} style={{ marginBottom: 8, borderBottom: '1px dashed rgba(255,255,255,0.03)', paddingBottom: 6 }}>
                                <div style={{ color: '#7ea', fontSize: 11 }}>{l.ts}</div>
                                <div style={{ whiteSpace: 'pre-wrap', marginTop: 4 }}>{l.msg}</div>
                                {l.data !== undefined && (
                                    <pre style={{ marginTop: 6, color: '#cce', fontSize: 11, background: 'rgba(0,0,0,0.2)', padding: 6, overflow: 'auto' }}>
                                        {typeof l.data === 'string' ? l.data : JSON.stringify(l.data, null, 2)}
                                    </pre>
                                )}
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
}
