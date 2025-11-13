import React from 'react';
import * as d3 from 'd3-geo';
import { feature } from 'topojson-client';
import type { Topology, GeometryCollection } from 'topojson-specification';
import logger from '@site/src/utils/logger';

// Fetch world-atlas data once globally (not per component instance)
let globalWorldData: GeoJSON.FeatureCollection | null = null;
let isLoading = false;
const listeners: Array<(data: GeoJSON.FeatureCollection) => void> = [];

const loadWorldData = () => {
    if (globalWorldData) return;
    if (isLoading) return;

    isLoading = true;
    fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
        .then(res => res.json())
        .then((topology: Topology) => {
            const countries = (topology.objects as any).countries as GeometryCollection;
            const geoData = feature(topology, countries) as GeoJSON.FeatureCollection;
            globalWorldData = geoData;
            listeners.forEach(cb => cb(geoData));
            listeners.length = 0;
        })
        .catch(err => {
            logger.error('Failed to load world map:', err);
            globalWorldData = { type: 'FeatureCollection', features: [] };
            listeners.forEach(cb => cb(globalWorldData!));
            listeners.length = 0;
        });
};

const useWorldData = () => {
    const [worldData, setWorldData] = React.useState<GeoJSON.FeatureCollection | null>(globalWorldData);

    React.useEffect(() => {
        if (globalWorldData) {
            setWorldData(globalWorldData);
        } else {
            listeners.push(setWorldData);
            loadWorldData();
        }
    }, []);

    return worldData;
};

// Removed simplified world landmass data - using world-atlas instead
const fallbackWorldLand: GeoJSON.FeatureCollection = {
    type: 'FeatureCollection',
    features: [
        {
            type: 'Feature',
            properties: { name: 'North America' },
            geometry: {
                type: 'Polygon',
                coordinates: [[
                    [-170, 72], [-160, 70], [-140, 69], [-130, 68], [-120, 67], [-110, 68],
                    [-100, 70], [-90, 72], [-85, 73], [-80, 74], [-75, 75], [-70, 73],
                    [-65, 70], [-60, 68], [-55, 65], [-50, 60], [-55, 55], [-60, 50],
                    [-65, 48], [-70, 45], [-75, 43], [-80, 40], [-85, 38], [-90, 36],
                    [-95, 34], [-100, 32], [-105, 30], [-110, 28], [-115, 26], [-118, 24],
                    [-115, 22], [-110, 20], [-105, 18], [-100, 16], [-95, 15], [-90, 14],
                    [-85, 13], [-82, 10], [-80, 8], [-85, 8], [-90, 10], [-95, 12],
                    [-100, 14], [-105, 16], [-110, 18], [-115, 20], [-120, 25], [-125, 30],
                    [-130, 35], [-135, 40], [-140, 45], [-145, 50], [-150, 55], [-155, 60],
                    [-160, 65], [-165, 68], [-170, 70], [-170, 72]
                ]]
            }
        },
        {
            type: 'Feature',
            properties: { name: 'South America' },
            geometry: {
                type: 'Polygon',
                coordinates: [[
                    [-80, 12], [-75, 10], [-70, 8], [-65, 6], [-60, 4], [-55, 2],
                    [-50, 0], [-47, -2], [-45, -5], [-43, -8], [-42, -12], [-41, -16],
                    [-40, -20], [-39, -24], [-38, -28], [-37, -32], [-37, -36], [-38, -40],
                    [-40, -44], [-43, -47], [-47, -50], [-50, -52], [-53, -54], [-55, -55],
                    [-58, -54], [-62, -52], [-66, -49], [-69, -46], [-72, -42], [-74, -38],
                    [-76, -34], [-77, -30], [-78, -26], [-79, -22], [-80, -18], [-81, -14],
                    [-81, -10], [-80, -6], [-79, -2], [-78, 2], [-78, 6], [-79, 9],
                    [-80, 11], [-80, 12]
                ]]
            }
        },
        {
            type: 'Feature',
            properties: { name: 'Europe' },
            geometry: {
                type: 'Polygon',
                coordinates: [[
                    [-10, 72], [-5, 71], [0, 70], [5, 69], [10, 68], [15, 67],
                    [20, 66], [25, 65], [30, 64], [35, 63], [40, 62], [42, 60],
                    [43, 58], [44, 56], [45, 54], [44, 52], [42, 50], [40, 48],
                    [38, 46], [36, 44], [34, 42], [32, 40], [30, 38], [28, 36],
                    [26, 35], [24, 36], [22, 37], [20, 38], [18, 39], [16, 40],
                    [14, 41], [12, 42], [10, 43], [8, 44], [6, 45], [4, 46],
                    [2, 47], [0, 48], [-2, 49], [-4, 50], [-6, 52], [-8, 55],
                    [-9, 60], [-10, 65], [-10, 70], [-10, 72]
                ]]
            }
        },
        {
            type: 'Feature',
            properties: { name: 'Africa' },
            geometry: {
                type: 'Polygon',
                coordinates: [[
                    [-18, 38], [-15, 36], [-12, 34], [-9, 32], [-6, 30], [-3, 28],
                    [0, 26], [3, 24], [6, 22], [9, 20], [12, 18], [15, 16],
                    [18, 14], [21, 12], [24, 10], [27, 8], [30, 6], [33, 4],
                    [36, 2], [38, 0], [40, -2], [42, -5], [43, -8], [44, -12],
                    [44, -16], [43, -20], [42, -24], [40, -28], [37, -31], [34, -33],
                    [30, -34], [26, -34], [22, -33], [18, -32], [14, -30], [10, -28],
                    [7, -26], [5, -24], [3, -22], [1, -20], [-1, -18], [-3, -16],
                    [-5, -14], [-7, -12], [-9, -10], [-11, -8], [-13, -6], [-15, -4],
                    [-17, -2], [-18, 0], [-19, 4], [-19, 8], [-19, 12], [-19, 16],
                    [-19, 20], [-19, 24], [-19, 28], [-19, 32], [-18, 36], [-18, 38]
                ]]
            }
        },
        {
            type: 'Feature',
            properties: { name: 'Asia' },
            geometry: {
                type: 'Polygon',
                coordinates: [[
                    [40, 78], [50, 77], [60, 76], [70, 75], [80, 74], [90, 73],
                    [100, 72], [110, 71], [120, 70], [130, 69], [140, 68], [150, 67],
                    [160, 66], [165, 65], [168, 63], [170, 60], [171, 57], [172, 54],
                    [172, 50], [171, 46], [169, 42], [166, 38], [162, 34], [157, 30],
                    [152, 26], [147, 23], [142, 21], [137, 20], [132, 19], [127, 18],
                    [122, 17], [117, 17], [112, 17], [107, 17], [102, 18], [97, 19],
                    [92, 20], [87, 22], [82, 24], [77, 26], [72, 28], [67, 30],
                    [62, 33], [57, 36], [52, 39], [47, 42], [45, 45], [44, 50],
                    [43, 55], [42, 60], [41, 65], [40, 70], [40, 75], [40, 78]
                ]]
            }
        },
        {
            type: 'Feature',
            properties: { name: 'Australia' },
            geometry: {
                type: 'Polygon',
                coordinates: [[
                    [113, -10], [118, -11], [123, -12], [128, -13], [133, -14], [138, -15],
                    [143, -16], [148, -17], [153, -19], [155, -22], [156, -25], [156, -28],
                    [155, -31], [153, -34], [150, -37], [146, -39], [142, -40], [137, -40],
                    [132, -39], [127, -38], [122, -36], [117, -34], [113, -31], [110, -28],
                    [108, -24], [107, -20], [107, -16], [108, -12], [110, -11], [113, -10]
                ]]
            }
        }
    ]
};

type IncidentSeverity = 'critical' | 'high' | 'medium';
type Incident = { id: number; location: string; lat: number; lon: number; severity: IncidentSeverity; description?: string; timestamp?: string };

type Props = {
    incidents: Incident[];
    width?: number;
    height?: number;
    hoveredIncident?: number | null;
    onIncidentHover?: (id: number | null) => void;
};

export default function WorldMap({ incidents, width = 360, height = 180, hoveredIncident, onIncidentHover }: Props) {
    const worldData = useWorldData();

    // Equirectangular projection (simple lat/lon to x/y)
    const projection = d3.geoEquirectangular()
        .scale(width / (2 * Math.PI))
        .translate([width / 2, height / 2]);

    const path = d3.geoPath(projection);
    const landData = worldData || fallbackWorldLand;

    return (
        <div className="worldMapContainer" style={{ position: 'relative', width: '100%', height: '100%' }}>
            <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="100%" style={{ position: 'absolute', top: 0, left: 0 }}>
                <defs>
                    <radialGradient id="worldGlow" cx="50%" cy="40%" r="60%">
                        <stop offset="0%" stopColor="rgba(34,211,238,0.08)" />
                        <stop offset="100%" stopColor="rgba(34,211,238,0)" />
                    </radialGradient>
                    <pattern id="worldDots" x="0" y="0" width="3" height="3" patternUnits="userSpaceOnUse">
                        <circle cx="1.5" cy="1.5" r="0.6" fill="rgba(34,211,238,0.5)" />
                    </pattern>
                </defs>

                {/* Background */}
                <rect width={width} height={height} fill="url(#worldGlow)" />

                {/* Landmasses */}
                {landData.features.map((feature, i) => (
                    <path
                        key={i}
                        d={path(feature as any) || ''}
                        fill="url(#worldDots)"
                        stroke="var(--hud-accent)"
                        strokeWidth="0.5"
                        opacity="0.85"
                    />
                ))}

                {/* Grid lines */}
                {Array.from({ length: 6 }, (_, i) => (
                    <line key={`lat-${i}`} x1={0} y1={(i + 1) * 30} x2={width} y2={(i + 1) * 30}
                        stroke="rgba(34,211,238,0.12)" strokeWidth={0.5} strokeDasharray="3,5" />
                ))}
                {Array.from({ length: 12 }, (_, i) => (
                    <line key={`lon-${i}`} x1={(i + 1) * 30} y1={0} x2={(i + 1) * 30} y2={height}
                        stroke="rgba(34,211,238,0.12)" strokeWidth={0.5} strokeDasharray="3,5" />
                ))}
            </svg>

            {/* Incident markers */}
            {incidents.map((inc) => {
                const [x, y] = projection([inc.lon, inc.lat]) || [0, 0];
                const xPercent = (x / width) * 100;
                const yPercent = (y / height) * 100;
                const isHovered = hoveredIncident === inc.id;
                return (
                    <div
                        key={inc.id}
                        style={{
                            position: 'absolute',
                            left: `${xPercent}%`,
                            top: `${yPercent}%`,
                            transform: 'translate(-50%, -50%)',
                            pointerEvents: 'auto',
                            cursor: 'pointer',
                            zIndex: isHovered ? 10 : 1
                        }}
                        onMouseEnter={() => onIncidentHover?.(inc.id)}
                        onMouseLeave={() => onIncidentHover?.(null)}
                    >
                        <div className={`incidentPulse ${inc.severity}`} style={{
                            width: isHovered ? '16px' : '12px',
                            height: isHovered ? '16px' : '12px',
                            borderRadius: '50%',
                            backgroundColor: inc.severity === 'critical' ? 'var(--hud-crit)' : inc.severity === 'high' ? 'var(--hud-warn)' : 'var(--hud-ok)',
                            opacity: 0.9,
                            animation: `pulse ${isHovered ? '1s' : '2s'} ease-in-out infinite`,
                            transition: 'all 0.2s ease',
                            boxShadow: isHovered ? '0 0 12px currentColor' : 'none'
                        }} />
                        <span style={{
                            position: 'absolute',
                            top: isHovered ? '18px' : '14px',
                            left: '50%',
                            transform: 'translateX(-50%)',
                            fontSize: isHovered ? '10px' : '9px',
                            fontWeight: 600,
                            color: 'var(--hud-text)',
                            whiteSpace: 'nowrap',
                            textShadow: '0 0 4px rgba(0,0,0,0.8)',
                            transition: 'all 0.2s ease'
                        }}>
                            {inc.location}
                        </span>
                        {isHovered && inc.description && (
                            <div style={{
                                position: 'absolute',
                                top: '32px',
                                left: '50%',
                                transform: 'translateX(-50%)',
                                background: 'var(--ifm-background-surface-color)',
                                border: '1px solid var(--ifm-color-emphasis-300)',
                                borderRadius: '6px',
                                padding: '6px 10px',
                                fontSize: '10px',
                                color: 'var(--ifm-font-color-base)',
                                whiteSpace: 'nowrap',
                                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
                                zIndex: 20,
                                pointerEvents: 'none'
                            }}>
                                <div style={{ fontWeight: 600, marginBottom: '2px' }}>{inc.description}</div>
                                <div style={{ fontSize: '9px', color: 'var(--hud-text-dim)' }}>
                                    {inc.severity.toUpperCase()} • {inc.timestamp || 'Now'}
                                </div>
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
