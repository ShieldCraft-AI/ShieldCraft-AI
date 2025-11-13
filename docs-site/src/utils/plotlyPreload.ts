import type { ComponentType } from 'react';

type PlotlyModule = { default: ComponentType<any> };

let plotlyPromise: Promise<PlotlyModule> | null = null;

export function loadPlotly(): Promise<PlotlyModule> | null {
    if (typeof window === 'undefined') return null;
    if (!plotlyPromise) {
        try {
            plotlyPromise = import(/* webpackChunkName: "plotly-basic" */ './plotlyBasicComponent');
        } catch {
            plotlyPromise = Promise.reject(new Error('Failed to load Plotly chunk'));
        }
    }
    return plotlyPromise;
}

export const preloadPlotly = loadPlotly;
