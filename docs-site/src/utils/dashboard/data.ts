import dayjs from 'dayjs';
import { quantileSorted } from 'simple-statistics';
import regression from 'regression';

export type Point = { t: number; v: number };
export type Series = { id: string; data: Point[] };

export function genDriftSeries({
    points,
    start = dayjs().subtract(7, 'day').valueOf(),
    stepMs = 60_000,
    base = 100,
    volatility = 0.5,
    drift = 0.0,
    floor = 0,
    ceiling = Number.POSITIVE_INFINITY,
    seed,
}: {
    points: number;
    start?: number;
    stepMs?: number;
    base?: number;
    volatility?: number;
    drift?: number;
    floor?: number;
    ceiling?: number;
    seed?: number;
}): Point[] {
    let t = start;
    let v = base;
    let s = seed ?? Math.floor(Math.random() * 1e9);
    const rand = () => (s = (s * 1664525 + 1013904223) % 4294967296) / 4294967296 - 0.5;
    const out: Point[] = [];
    for (let i = 0; i < points; i++) {
        v = v + drift + rand() * volatility;
        v = Math.max(floor, Math.min(ceiling, v));
        out.push({ t, v });
        t += stepMs;
    }
    return out;
}

export function windowBy(fromMs: number, toMs: number, series: Point[]): Point[] {
    return series.filter(p => p.t >= fromMs && p.t <= toMs);
}

export function quantiles(values: number[]) {
    if (values.length === 0) return { p50: 0, p95: 0, p99: 0 };
    return {
        p50: quantileSorted([...values].sort((a, b) => a - b), 0.5),
        p95: quantileSorted([...values].sort((a, b) => a - b), 0.95),
        p99: quantileSorted([...values].sort((a, b) => a - b), 0.99),
    };
}

export function linearRegression(points: Point[]) {
    if (points.length < 2) return null;
    const res = regression.linear(points.map(p => [p.t, p.v]));
    return res;
}

export function toCSV(series: Series[]): string {
    const rows: string[] = ['id,t,v'];
    for (const s of series) {
        for (const p of s.data) rows.push(`${s.id},${new Date(p.t).toISOString()},${p.v}`);
    }
    return rows.join('\n');
}
