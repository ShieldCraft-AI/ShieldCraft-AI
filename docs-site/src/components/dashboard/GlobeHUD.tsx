import React from 'react';
import * as d3 from 'd3-geo';
import * as topojson from 'topojson-client';
import type { Topology, GeometryCollection } from 'topojson-specification';
import logger from '@site/src/utils/logger';

export type Arc = { from: [number, number]; to: [number, number]; color?: string };

type ActivityPoint = {
    id: number;
    coords: [number, number];
    severity: 'critical' | 'high' | 'medium' | 'info';
    timestamp: number;
};

type Props = {
    width?: number;
    height?: number;
    rotation?: [number, number, number];
    arcs?: Arc[];
    graticule?: boolean;
    className?: string;
};

// Global cache for world topology data
let globalTopoData: GeoJSON.FeatureCollection | null = null;
let isLoadingTopo = false;
let topoListeners: Array<(data: GeoJSON.FeatureCollection) => void> = [];

async function loadTopoData(): Promise<GeoJSON.FeatureCollection> {
    if (globalTopoData) return globalTopoData;

    if (isLoadingTopo) {
        return new Promise((resolve) => {
            topoListeners.push(resolve);
        });
    }

    isLoadingTopo = true;
    try {
        const response = await fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json');
        const topology = await response.json() as Topology;
        const countries = (topology.objects.countries as GeometryCollection);
        const features = topojson.feature(topology, countries);
        globalTopoData = features as GeoJSON.FeatureCollection;
        topoListeners.forEach(cb => cb(globalTopoData!));
        topoListeners = [];
        return globalTopoData;
    } catch (error) {
        logger.warn('Failed to load world topology, using fallback', error);
        // Fallback to simplified land mass
        const fallback: GeoJSON.FeatureCollection = {
            type: 'FeatureCollection',
            features: [
                {
                    type: 'Feature',
                    properties: {},
                    geometry: {
                        type: 'MultiPolygon',
                        coordinates: [
                            [[[-170, 70], [-130, 70], [-100, 75], [-85, 74], [-75, 75], [-70, 72], [-60, 68], [-55, 60], [-65, 45], [-80, 40], [-95, 35], [-110, 28], [-118, 24], [-110, 18], [-100, 15], [-85, 10], [-90, 15], [-105, 18], [-125, 30], [-145, 50], [-160, 65], [-170, 70]]],
                            [[[-80, 12], [-70, 8], [-55, 2], [-47, -2], [-43, -8], [-41, -16], [-38, -28], [-37, -36], [-43, -47], [-55, -55], [-62, -52], [-72, -42], [-77, -30], [-80, -18], [-81, -10], [-79, 2], [-80, 12]]],
                            [[[-10, 70], [0, 70], [20, 68], [40, 62], [45, 54], [42, 48], [36, 42], [28, 36], [20, 38], [10, 43], [0, 48], [-8, 55], [-10, 70]]],
                            [[[-18, 35], [-10, 30], [0, 25], [15, 15], [30, 5], [40, -2], [44, -16], [40, -30], [30, -34], [18, -32], [10, -28], [0, -20], [-10, -10], [-18, 0], [-19, 20], [-18, 35]]],
                            [[[40, 75], [60, 76], [90, 73], [120, 70], [150, 67], [172, 54], [169, 40], [157, 30], [142, 21], [127, 18], [112, 17], [97, 19], [82, 24], [67, 30], [52, 39], [44, 50], [40, 70], [40, 75]]],
                            [[[113, -10], [138, -15], [153, -19], [156, -28], [153, -37], [142, -40], [127, -38], [113, -31], [107, -20], [113, -10]]]
                        ]
                    }
                }
            ]
        };
        globalTopoData = fallback;
        topoListeners.forEach(cb => cb(globalTopoData!));
        topoListeners = [];
        return fallback;
    } finally {
        isLoadingTopo = false;
    }
}

function useTopoData() {
    const [data, setData] = React.useState<GeoJSON.FeatureCollection | null>(globalTopoData);

    React.useEffect(() => {
        if (!globalTopoData) {
            loadTopoData().then(setData);
        }
    }, []);

    return data;
}

function buildGraticule(): GeoJSON.MultiLineString {
    const lines: [number, number][][] = [];
    for (let lon = -180; lon <= 180; lon += 30) {
        const meridian: [number, number][] = [];
        for (let lat = -90; lat <= 90; lat += 10) meridian.push([lon, lat]);
        lines.push(meridian);
    }
    for (let lat = -60; lat <= 60; lat += 30) {
        const parallel: [number, number][] = [];
        for (let lon = -180; lon <= 180; lon += 10) parallel.push([lon, lat]);
        lines.push(parallel);
    }
    return { type: 'MultiLineString', coordinates: lines };
}

// AWS Region coordinates (lon, lat) - comprehensive list of all AWS regions
const AWS_REGIONS: Array<{ coords: [number, number]; name: string; code: string }> = [
    // US Regions
    { coords: [-77.5, 39.0], name: 'N. Virginia', code: 'us-east-1' },
    { coords: [-84.4, 39.1], name: 'Ohio', code: 'us-east-2' },
    { coords: [-122.3, 37.8], name: 'N. California', code: 'us-west-1' },
    { coords: [-119.4, 45.8], name: 'Oregon', code: 'us-west-2' },
    // Canada
    { coords: [-73.6, 45.5], name: 'Montreal', code: 'ca-central-1' },
    { coords: [-114.1, 51.0], name: 'Calgary', code: 'ca-west-1' },
    // South America
    { coords: [-46.6, -23.5], name: 'São Paulo', code: 'sa-east-1' },
    // Europe
    { coords: [0.1, 51.5], name: 'Ireland', code: 'eu-west-1' },
    { coords: [-0.1, 51.5], name: 'London', code: 'eu-west-2' },
    { coords: [8.7, 48.6], name: 'Frankfurt', code: 'eu-central-1' },
    { coords: [18.1, 59.3], name: 'Stockholm', code: 'eu-north-1' },
    { coords: [2.3, 48.9], name: 'Paris', code: 'eu-west-3' },
    { coords: [9.2, 45.5], name: 'Milan', code: 'eu-south-1' },
    { coords: [7.4, 46.9], name: 'Zurich', code: 'eu-central-2' },
    { coords: [-3.7, 40.4], name: 'Spain', code: 'eu-south-2' },
    // Middle East
    { coords: [50.6, 26.1], name: 'Bahrain', code: 'me-south-1' },
    { coords: [54.4, 24.5], name: 'UAE', code: 'me-central-1' },
    // Africa
    { coords: [18.4, -33.9], name: 'Cape Town', code: 'af-south-1' },
    // Asia Pacific
    { coords: [114.2, 22.3], name: 'Hong Kong', code: 'ap-east-1' },
    { coords: [103.8, 1.3], name: 'Singapore', code: 'ap-southeast-1' },
    { coords: [151.2, -33.9], name: 'Sydney', code: 'ap-southeast-2' },
    { coords: [139.7, 35.7], name: 'Tokyo', code: 'ap-northeast-1' },
    { coords: [126.9, 37.6], name: 'Seoul', code: 'ap-northeast-2' },
    { coords: [135.5, 34.7], name: 'Osaka', code: 'ap-northeast-3' },
    { coords: [72.9, 19.1], name: 'Mumbai', code: 'ap-south-1' },
    { coords: [78.5, 17.4], name: 'Hyderabad', code: 'ap-south-2' },
    { coords: [106.8, -6.2], name: 'Jakarta', code: 'ap-southeast-3' },
    { coords: [144.9, -37.8], name: 'Melbourne', code: 'ap-southeast-4' },
    // Israel
    { coords: [34.8, 32.1], name: 'Tel Aviv', code: 'il-central-1' },
];

export default function GlobeHUD({
    width = 520,
    height = 520,
    rotation = [0, -10, 0],
    arcs = [],
    graticule = true,
    className,
}: Props) {
    const [rot, setRot] = React.useState<[number, number, number]>(rotation);
    const [isDragging, setIsDragging] = React.useState(false);
    const [lastPos, setLastPos] = React.useState<[number, number] | null>(null);
    const [activityPoints, setActivityPoints] = React.useState<ActivityPoint[]>([]);
    const [liveArcs, setLiveArcs] = React.useState<Arc[]>([]);
    const [scale, setScale] = React.useState(1.0); // Zoom scale
    const [hoveredRegion, setHoveredRegion] = React.useState<string | null>(null);
    const svgRef = React.useRef<SVGSVGElement>(null);

    // Load real world topology data
    const land = useTopoData();

    const projection = d3.geoOrthographic()
        .fitExtent([[8, 8], [width - 8, height - 8]], { type: 'Sphere' } as any)
        .scale(d3.geoOrthographic().fitExtent([[8, 8], [width - 8, height - 8]], { type: 'Sphere' } as any).scale()! * scale)
        .rotate(rot);
    const path = d3.geoPath(projection);
    const sphere = { type: 'Sphere' } as any;
    const grat = buildGraticule();

    // Handle mouse wheel zoom
    React.useEffect(() => {
        const handleWheel = (e: WheelEvent) => {
            e.preventDefault();
            setScale(prev => {
                const delta = e.deltaY > 0 ? 0.95 : 1.05;
                return Math.max(0.5, Math.min(3.0, prev * delta));
            });
        };

        const svg = svgRef.current;
        if (svg) {
            svg.addEventListener('wheel', handleWheel, { passive: false });
            return () => svg.removeEventListener('wheel', handleWheel);
        }
    }, []);

    // Generate live activity points at AWS availability zones
    React.useEffect(() => {
        const severities: Array<'critical' | 'high' | 'medium' | 'info'> = ['critical', 'high', 'high', 'medium', 'medium', 'medium', 'info', 'info', 'info'];

        let id = 0;
        const addPoint = () => {
            const region = AWS_REGIONS[Math.floor(Math.random() * AWS_REGIONS.length)];
            const severity = severities[Math.floor(Math.random() * severities.length)];
            const point: ActivityPoint = { id: id++, coords: region.coords, severity, timestamp: Date.now() };
            setActivityPoints(prev => {
                const filtered = prev.filter(p => Date.now() - p.timestamp < 8000);
                return [...filtered, point].slice(-20);
            });
        };

        // Add initial points
        for (let i = 0; i < 6; i++) {
            setTimeout(() => addPoint(), i * 800);
        }

        // Add new points every 2-4s for live activity
        const schedule = () => {
            const ms = 2000 + Math.floor(Math.random() * 2000);
            setTimeout(() => {
                addPoint();
                schedule();
            }, ms);
        };
        schedule();
    }, []);

    // Static AWS region connections (major data transfer routes)
    const staticAwsConnections: Arc[] = React.useMemo(() => [
        // US East to other major regions
        { from: [-77.5, 39.0], to: [0.1, 51.5], color: '#22d3ee' },        // us-east-1 -> eu-west-1
        { from: [-77.5, 39.0], to: [139.7, 35.7], color: '#22d3ee' },      // us-east-1 -> ap-northeast-1
        { from: [-77.5, 39.0], to: [103.8, 1.3], color: '#22d3ee' },       // us-east-1 -> ap-southeast-1

        // US West connections
        { from: [-119.4, 45.8], to: [139.7, 35.7], color: '#22d3ee' },     // us-west-2 -> ap-northeast-1
        { from: [-119.4, 45.8], to: [151.2, -33.9], color: '#22d3ee' },    // us-west-2 -> ap-southeast-2

        // Europe hub connections
        { from: [0.1, 51.5], to: [8.7, 48.6], color: '#22d3ee' },          // eu-west-1 -> eu-central-1
        { from: [0.1, 51.5], to: [50.6, 26.1], color: '#22d3ee' },         // eu-west-1 -> me-central-1
        { from: [8.7, 48.6], to: [139.7, 35.7], color: '#22d3ee' },        // eu-central-1 -> ap-northeast-1

        // Asia-Pacific connections
        { from: [139.7, 35.7], to: [126.9, 37.6], color: '#22d3ee' },      // ap-northeast-1 -> ap-northeast-2
        { from: [139.7, 35.7], to: [103.8, 1.3], color: '#22d3ee' },       // ap-northeast-1 -> ap-southeast-1
        { from: [103.8, 1.3], to: [151.2, -33.9], color: '#22d3ee' },      // ap-southeast-1 -> ap-southeast-2
        { from: [103.8, 1.3], to: [72.9, 19.1], color: '#22d3ee' },        // ap-southeast-1 -> ap-south-1

        // South America connection
        { from: [-46.6, -23.5], to: [-77.5, 39.0], color: '#22d3ee' },     // sa-east-1 -> us-east-1

        // Africa connection
        { from: [18.4, -33.9], to: [0.1, 51.5], color: '#22d3ee' },        // af-south-1 -> eu-west-1

        // Middle East connections
        { from: [50.6, 26.1], to: [72.9, 19.1], color: '#22d3ee' },        // me-central-1 -> ap-south-1

        // Canada connections
        { from: [-73.6, 45.5], to: [-77.5, 39.0], color: '#22d3ee' },      // ca-central-1 -> us-east-1
    ], []);

    // Generate live arcs between AWS regions - always show 5 connections
    React.useEffect(() => {
        const updateArcs = () => {
            const newArcs: Arc[] = [];
            const colors = ['#ef4444', '#f59e0b', '#22d3ee'];

            // Always create exactly 5 live arcs between random AWS regions
            const usedPairs = new Set<string>();
            let attempts = 0;
            const maxAttempts = 50;

            while (newArcs.length < 5 && attempts < maxAttempts) {
                const from = AWS_REGIONS[Math.floor(Math.random() * AWS_REGIONS.length)];
                const to = AWS_REGIONS[Math.floor(Math.random() * AWS_REGIONS.length)];

                // Create a unique key for this pair (order-independent)
                const pairKey = [from.code, to.code].sort().join('-');

                if (from.code !== to.code && !usedPairs.has(pairKey)) {
                    usedPairs.add(pairKey);
                    const color = colors[Math.floor(Math.random() * colors.length)];
                    newArcs.push({ from: from.coords, to: to.coords, color });
                }
                attempts++;
            }

            setLiveArcs(newArcs);
        };

        // Update arcs every 2.5 seconds to keep it dynamic
        updateArcs();
        const interval = setInterval(updateArcs, 2500);
        return () => clearInterval(interval);
    }, []);

    // Handle mouse drag for rotation
    const handleMouseDown = (e: React.MouseEvent) => {
        setIsDragging(true);
        setLastPos([e.clientX, e.clientY]);
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!isDragging || !lastPos) return;
        const dx = e.clientX - lastPos[0];
        const dy = e.clientY - lastPos[1];
        setRot(([lon, lat, roll]) => [
            lon + dx * 0.2,
            Math.max(-90, Math.min(90, lat - dy * 0.2)),
            roll
        ]);
        setLastPos([e.clientX, e.clientY]);
    };

    const handleMouseUp = () => {
        setIsDragging(false);
        setLastPos(null);
    };

    React.useEffect(() => {
        if (isDragging) {
            const handleGlobalMouseUp = () => {
                setIsDragging(false);
                setLastPos(null);
            };
            window.addEventListener('mouseup', handleGlobalMouseUp);
            return () => window.removeEventListener('mouseup', handleGlobalMouseUp);
        }
    }, [isDragging]);

    // Auto-rotation when not dragging and not hovering over a region
    React.useEffect(() => {
        if (isDragging || hoveredRegion) return; // Pause rotation when hovering over AWS AZ

        const rotationSpeed = 0.15; // degrees per frame (slow and smooth)
        let animationFrame: number;

        const animate = () => {
            setRot(([lon, lat, roll]) => [
                (lon + rotationSpeed) % 360,
                lat,
                roll
            ]);
            animationFrame = requestAnimationFrame(animate);
        };

        animationFrame = requestAnimationFrame(animate);
        return () => cancelAnimationFrame(animationFrame);
    }, [isDragging, hoveredRegion]);

    return (
        <svg
            ref={svgRef}
            viewBox={`0 0 ${width} ${height}`}
            width="100%"
            height="100%"
            className={className}
            aria-label="Global activity globe"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
        >
            <defs>
                <radialGradient id="gShade" cx="50%" cy="45%" r="60%">
                    <stop offset="0%" stopColor="rgba(34,211,238,0.20)" />
                    <stop offset="70%" stopColor="rgba(34,211,238,0.10)" />
                    <stop offset="100%" stopColor="rgba(34,211,238,0.02)" />
                </radialGradient>
                <radialGradient id="critGlow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="rgba(239,68,68,0.8)" />
                    <stop offset="50%" stopColor="rgba(239,68,68,0.4)" />
                    <stop offset="100%" stopColor="rgba(239,68,68,0)" />
                </radialGradient>
                <radialGradient id="highGlow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="rgba(245,158,11,0.8)" />
                    <stop offset="50%" stopColor="rgba(245,158,11,0.4)" />
                    <stop offset="100%" stopColor="rgba(245,158,11,0)" />
                </radialGradient>
                <radialGradient id="medGlow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="rgba(34,211,238,0.8)" />
                    <stop offset="50%" stopColor="rgba(34,211,238,0.4)" />
                    <stop offset="100%" stopColor="rgba(34,211,238,0)" />
                </radialGradient>
                <radialGradient id="infoGlow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="rgba(148,163,184,0.6)" />
                    <stop offset="50%" stopColor="rgba(148,163,184,0.3)" />
                    <stop offset="100%" stopColor="rgba(148,163,184,0)" />
                </radialGradient>
                <filter id="glow">
                    <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                    <feMerge>
                        <feMergeNode in="coloredBlur" />
                        <feMergeNode in="SourceGraphic" />
                    </feMerge>
                </filter>
            </defs>

            {/* Sphere backdrop */}
            <path d={path(sphere)!} fill="url(#gShade)" stroke="rgba(34,211,238,0.35)" strokeWidth={0.8} />

            {/* Land masses */}
            {land && land.features.map((feature, i) => (
                <path
                    key={`land-${i}`}
                    d={path(feature as any) || ''}
                    fill="rgba(34,211,238,0.12)"
                    stroke="rgba(34,211,238,0.45)"
                    strokeWidth={0.5}
                />
            ))}

            {/* Graticule */}
            {graticule && <path d={path(grat as any)!} fill="none" stroke="#334155" strokeOpacity={0.35} strokeWidth={0.6} />}

            {/* Static AWS region connections - always visible */}
            {staticAwsConnections.map((a, i) => {
                const geo: any = { type: 'LineString', coordinates: [a.from, a.to] };
                const d = path(geo);
                if (!d) return null;
                return (
                    <path
                        key={`aws-conn-${i}`}
                        d={d}
                        fill="none"
                        stroke={a.color ?? '#22d3ee'}
                        strokeWidth={0.8}
                        strokeOpacity={0.25}
                        strokeDasharray="2 3"
                    />
                );
            })}

            {/* Live activity arcs - highlight active transfers */}
            {liveArcs.map((a, i) => {
                const geo: any = { type: 'LineString', coordinates: [a.from, a.to] };
                const d = path(geo);
                if (!d) return null;
                return (
                    <path
                        key={`arc-${i}`}
                        d={d}
                        fill="none"
                        stroke={a.color ?? '#22d3ee'}
                        strokeWidth={2}
                        strokeOpacity={0.8}
                        strokeDasharray="4 4"
                        filter="url(#glow)"
                    >
                        <animate
                            attributeName="stroke-dashoffset"
                            from="0"
                            to="8"
                            dur="0.8s"
                            repeatCount="indefinite"
                        />
                    </path>
                );
            })}

            {/* Static arcs (from props) */}
            {arcs.map((a, i) => {
                const geo: any = { type: 'LineString', coordinates: [a.from, a.to] };
                const d = path(geo);
                if (!d) return null;
                return <path key={`static-${i}`} d={d} fill="none" stroke={a.color ?? '#22d3ee'} strokeWidth={1.2} strokeOpacity={0.9} />
            })}

            {/* Static AWS Region Markers - only visible on front hemisphere */}
            {AWS_REGIONS.map((region, i) => {
                const projected = projection(region.coords);
                if (!projected) return null;

                // Check if point is on visible side of globe
                const distance = d3.geoDistance(region.coords, projection.invert!([width / 2, height / 2]) || [0, 0]);
                if (distance > Math.PI / 2) return null; // Point is on back side

                // Fade markers near the edge
                const edgeFade = 1 - Math.pow(distance / (Math.PI / 2), 3);
                const isHovered = hoveredRegion === region.code;

                return (
                    <g
                        key={`aws-${region.code}`}
                        transform={`translate(${projected[0]}, ${projected[1]})`}
                        opacity={edgeFade}
                        onMouseEnter={() => setHoveredRegion(region.code)}
                        onMouseLeave={() => setHoveredRegion(null)}
                        style={{ cursor: 'pointer' }}
                    >
                        {/* Outer ring */}
                        <circle
                            r={isHovered ? 6.6 : 4.4}
                            fill="none"
                            stroke={isHovered ? "rgba(34,211,238,0.8)" : "rgba(34,211,238,0.4)"}
                            strokeWidth={isHovered ? 1 : 0.5}
                            style={{ transition: 'all 0.2s ease' }}
                        />
                        {/* Core dot */}
                        <circle
                            r={isHovered ? 2.2 : 1.65}
                            fill={isHovered ? "rgba(34,211,238,0.9)" : "rgba(34,211,238,0.6)"}
                            style={{ transition: 'all 0.2s ease' }}
                        />
                        {/* Hover glow effect */}
                        {isHovered && (
                            <circle
                                r={8.8}
                                fill="rgba(34,211,238,0.15)"
                                style={{ transition: 'all 0.2s ease' }}
                            />
                        )}
                        {/* Region label on hover with enhanced info */}
                        {isHovered && (
                            <g>
                                <rect
                                    x={10}
                                    y={-18}
                                    width={Math.max(region.name.length * 6 + 16, 140)}
                                    height={52}
                                    rx={6}
                                    fill="rgba(15, 23, 42, 0.97)"
                                    stroke="rgba(34,211,238,0.6)"
                                    strokeWidth={1.2}
                                    filter="url(#glow)"
                                />
                                {/* Region name */}
                                <text
                                    x={16}
                                    y={-6}
                                    fontSize={11}
                                    fill="rgba(34,211,238,1)"
                                    fontWeight={700}
                                    fontFamily="ui-monospace, monospace"
                                >
                                    {region.name}
                                </text>
                                {/* Region code */}
                                <text
                                    x={16}
                                    y={6}
                                    fontSize={9}
                                    fill="rgba(148,163,184,0.9)"
                                    fontFamily="ui-monospace, monospace"
                                >
                                    {region.code}
                                </text>
                                {/* Divider line */}
                                <line
                                    x1={16}
                                    y1={12}
                                    x2={Math.max(region.name.length * 6 + 16, 140) - 6}
                                    y2={12}
                                    stroke="rgba(34,211,238,0.3)"
                                    strokeWidth={0.5}
                                />
                                {/* Availability Zones */}
                                <text
                                    x={16}
                                    y={21}
                                    fontSize={8}
                                    fill="rgba(148,163,184,0.7)"
                                    fontFamily="ui-monospace, monospace"
                                >
                                    AZs: 3-6
                                </text>
                                {/* Status indicator */}
                                <circle
                                    cx={16 + 38}
                                    cy={18}
                                    r={2}
                                    fill="rgba(34,197,94,1)"
                                />
                                <text
                                    x={16 + 44}
                                    y={21}
                                    fontSize={8}
                                    fill="rgba(34,197,94,0.9)"
                                    fontFamily="ui-monospace, monospace"
                                >
                                    Active
                                </text>
                                {/* Latency info */}
                                <text
                                    x={16}
                                    y={30}
                                    fontSize={7}
                                    fill="rgba(148,163,184,0.6)"
                                    fontFamily="ui-monospace, monospace"
                                >
                                    Latency: {Math.floor(Math.random() * 30 + 10)}ms
                                </text>
                            </g>
                        )}
                    </g>
                );
            })}

            {/* Activity points with pulsing effect (overlay on AWS regions) */}
            {activityPoints.map((point) => {
                const projected = projection(point.coords);
                if (!projected) return null;

                // Check if point is on visible side of globe
                const distance = d3.geoDistance(point.coords, projection.invert!([width / 2, height / 2]) || [0, 0]);
                if (distance > Math.PI / 2) return null; // Point is on back side

                const age = Date.now() - point.timestamp;
                const maxAge = 8000;
                const opacity = Math.max(0, 1 - age / maxAge);
                const scale = 1 + (age / maxAge) * 2;

                // Fade activity points near the edge
                const edgeFade = 1 - Math.pow(distance / (Math.PI / 2), 3);

                const colorMap = {
                    critical: '#ef4444',
                    high: '#f59e0b',
                    medium: '#22d3ee',
                    info: '#94a3b8'
                };
                const glowMap = {
                    critical: 'url(#critGlow)',
                    high: 'url(#highGlow)',
                    medium: 'url(#medGlow)',
                    info: 'url(#infoGlow)'
                };

                return (
                    <g key={point.id} transform={`translate(${projected[0]}, ${projected[1]})`}>
                        {/* Outer pulse ring */}
                        <circle
                            r={8 * scale}
                            fill={glowMap[point.severity]}
                            opacity={opacity * edgeFade * 0.4}
                        />
                        {/* Middle ring */}
                        <circle
                            r={5 * (1 + scale * 0.3)}
                            fill="none"
                            stroke={colorMap[point.severity]}
                            strokeWidth={1}
                            opacity={opacity * edgeFade * 0.6}
                        />
                        {/* Core dot */}
                        <circle
                            r={2.5}
                            fill={colorMap[point.severity]}
                            opacity={opacity * edgeFade}
                            filter="url(#glow)"
                        />
                    </g>
                );
            })}
        </svg>
    );
}
