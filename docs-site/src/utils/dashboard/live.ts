import { useEffect, useMemo, useRef, useState } from 'react';

export type Point = { t: number; v: number };
export type Series = Point[];

export function genInitialSeries({
    minutes = 60,
    stepSec = 5,
    base = 100,
    jitter = 1,
    driftPerMin = 0.05,
    clampMin = 0,
    clampMax = Number.POSITIVE_INFINITY,
}: {
    minutes?: number;
    stepSec?: number;
    base?: number;
    jitter?: number;
    driftPerMin?: number;
    clampMin?: number;
    clampMax?: number;
}): Series {
    const now = Date.now();
    const pts: Series = [];
    const totalSteps = Math.floor((minutes * 60) / stepSec);
    let v = base;
    for (let i = totalSteps; i >= 0; i--) {
        const t = now - i * stepSec * 1000;
        const drift = driftPerMin / (60 / stepSec);
        v = clamp(v + rand(-jitter, jitter) + drift, clampMin, clampMax);
        pts.push({ t, v: round2(v) });
    }
    return pts;
}

export function useLiveSeries(opts: {
    initial: Series;
    tickSec?: number;
    stepSec?: number;
    clampMin?: number;
    clampMax?: number;
    jitter?: number;
    driftPerMin?: number;
    live?: boolean;
    maxPoints?: number;
}) {
    const {
        initial,
        tickSec = 1,
        stepSec = 5,
        clampMin = 0,
        clampMax = Number.POSITIVE_INFINITY,
        jitter = 1,
        driftPerMin = 0.05,
        live = true,
        maxPoints = 600,
    } = opts;

    const [series, setSeries] = useState<Series>(initial);
    const lastRef = useRef<Point | null>(initial.at(-1) ?? null);

    useEffect(() => {
        lastRef.current = initial.at(-1) ?? null;
        setSeries(initial);
    }, [initial]);

    useEffect(() => {
        if (!live) return;
        let id: number | null = null;
        const tick = () => {
            const last = lastRef.current ?? series.at(-1);
            const now = Date.now();
            if (!last) return;
            if (now - last.t >= stepSec * 1000) {
                const drift = driftPerMin / (60 / stepSec);
                const nextV = clamp((last.v ?? 0) + rand(-jitter, jitter) + drift, clampMin, clampMax);
                const next: Point = { t: now, v: round2(nextV) };
                lastRef.current = next;
                setSeries((prev) => {
                    const trimmed = prev.length > maxPoints ? prev.slice(prev.length - maxPoints) : prev;
                    return [...trimmed, next];
                });
            } else {
                // Jitter the latest point slightly to create visible motion between time steps
                const tweenV = clamp((last.v ?? 0) + rand(-jitter * 0.25, jitter * 0.25), clampMin, clampMax);
                const updated: Point = { t: last.t, v: round2(tweenV) };
                lastRef.current = updated;
                setSeries((prev) => {
                    if (!prev.length) return prev;
                    const copy = prev.slice();
                    copy[copy.length - 1] = updated;
                    return copy;
                });
            }
            id = window.setTimeout(tick, tickSec * 1000);
        };
        id = window.setTimeout(tick, tickSec * 1000);
        return () => {
            if (id) window.clearTimeout(id);
        };
    }, [live, tickSec, stepSec, clampMin, clampMax, jitter, driftPerMin, maxPoints]);

    const kpis = useMemo(() => {
        if (!series.length) return { current: 0, deltaPct: 0, min: 0, max: 0 };
        const current = series.at(-1)!.v;
        const start = series[0].v;
        let min = start;
        let max = start;
        for (let i = 1; i < series.length; i++) {
            const v = series[i].v;
            if (v < min) min = v;
            if (v > max) max = v;
        }
        const deltaPct = start ? ((current - start) / start) * 100 : 0;
        return { current: round2(current), deltaPct: round2(deltaPct), min: round2(min), max: round2(max) };
    }, [series]);

    return { series, kpis };
}

export function formatTime(ts: number) {
    const d = new Date(ts);
    return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

export function formatNumber(v: number, digits = 2) {
    return (Math.round(v * 10 ** digits) / 10 ** digits).toFixed(digits);
}

// helpers
function rand(min: number, max: number) {
    return Math.random() * (max - min) + min;
}
function round2(v: number) {
    return Math.round(v * 100) / 100;
}
function clamp(v: number, min: number, max: number) {
    return Math.min(max, Math.max(min, v));
}
function pad(n: number) {
    return n.toString().padStart(2, '0');
}
