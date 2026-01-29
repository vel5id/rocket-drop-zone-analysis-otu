import {
    Activity,
    ChevronDown, ChevronRight,
    Crosshair,
    Download, FileText,
    Globe,
    Grid,
    Layers,
    Leaf,
    Minimize,
    Moon,
    Play,
    Rocket, Settings,
    Target,
    Zap
} from 'lucide-react';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { runSimulation as apiRunSimulation, checkHealth, pollSimulation } from './api';

// ============================================
// CONFIGURATION & FALLBACK LOGIC
// ============================================

// Leaflet is installed and available
const IS_LEAFLET_AVAILABLE = true;

// --- REAL IMPORTS ---
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { CircleMarker, LayerGroup, MapContainer, Polygon, Popup, TileLayer, useMap, useMapEvents } from 'react-leaflet';


// ============================================
// TYPES
// ============================================

interface ActiveLayers {
    primary: boolean;
    fragments: boolean;
    points: boolean;
    otu: boolean;
    ndvi: boolean;
    slope: boolean;
}

interface EllipseData {
    center_lat: number;
    center_lon: number;
    semi_major_km: number;
    semi_minor_km: number;
    angle_deg: number;
}

interface ImpactPointProperties {
    id: number;
    is_fragment: boolean;
    downrange_km: number;
    crossrange_km?: number;
    velocity_m_s?: number;
}

interface OTUCellProperties {
    grid_id: string;
    q_ndvi: number;
    q_si: number;
    q_bi: number;
    q_relief: number;
    q_otu: number;
    q_fire: number;
}

interface GeoJSONGeometry {
    type: 'Point' | 'Polygon';
    coordinates: any;
}

interface GeoJSONFeature<G extends GeoJSONGeometry, P> {
    type: 'Feature';
    geometry: G;
    properties: P;
}

interface GeoJSONFeatureCollection<G extends GeoJSONGeometry, P> {
    type: 'FeatureCollection';
    features: GeoJSONFeature<G, P>[];
}

type GeoJSONPoint = GeoJSONGeometry & { type: 'Point'; coordinates: [number, number] };
type GeoJSONPolygon = GeoJSONGeometry & { type: 'Polygon'; coordinates: [number, number][][] };

interface SimulationStats {
    impactPoints: number;
    range: string;
    semiMajorAxis: number;
    avgOtu: number;
    primaryEllipse: { a: number; b: number; angle: number };
    fragmentEllipse: { a: number; b: number; angle: number };
}

// ============================================
// CSS INJECTION
// ============================================

const GlobalStyles = () => (
    <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;700&family=Rajdhani:wght@500;600;700&display=swap');
    
    :root {
      --bg-space: #050a10;
      --bg-glass: rgba(13, 20, 30, 0.85);
      --bg-glass-heavy: rgba(13, 20, 30, 0.95);
      --text-bright: #ffffff;
      --text-dim: #94a3b8;
      --text-muted: #475569;
      --accent-cyan: #06b6d4;
      --accent-green: #10b981;
      --accent-red: #ef4444;
      --accent-amber: #f59e0b;
      --border-glass: rgba(255, 255, 255, 0.1);
      --font-main: 'Inter', sans-serif;
      --font-tech: 'Rajdhani', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }
    
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    body {
      background-color: var(--bg-space);
      color: var(--text-bright);
      font-family: var(--font-main);
      overflow: hidden;
    }
    
    .glass-panel {
      background: var(--bg-glass);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--border-glass);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    /* Inputs, Buttons, Scrollbars */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.02); border-radius: 3px; }
    ::-webkit-scrollbar-thumb { background: rgba(6, 182, 212, 0.3); border-radius: 3px; }
    
    input[type="range"] {
      -webkit-appearance: none; width: 100%; height: 6px;
      background: linear-gradient(to right, var(--accent-cyan) 0%, var(--accent-cyan) var(--value-percent, 10%), rgba(255, 255, 255, 0.1) 100%);
      border-radius: 3px; outline: none; cursor: pointer; margin: 12px 0;
    }
    input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none; width: 20px; height: 20px; background: var(--bg-space);
      border: 3px solid var(--accent-cyan); border-radius: 50%; cursor: grab;
      box-shadow: 0 0 12px rgba(6, 182, 212, 0.5); transition: all 0.2s ease;
    }
    
    button { font-family: var(--font-tech); transition: all 0.2s ease; }
    button:active:not(:disabled) { transform: scale(0.98); }
    
    @keyframes subtle-pulse { 0%, 100% { box-shadow: 0 0 15px rgba(6, 182, 212, 0.3); } 50% { box-shadow: 0 0 25px rgba(6, 182, 212, 0.5); } }
    .btn-primary-glow { animation: subtle-pulse 2s infinite; }
    
    /* Typography & Utils */
    .text-tech-label { font-family: var(--font-tech); font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; color: var(--text-dim); }
    .text-tech-value { font-family: var(--font-mono); font-size: 14px; color: var(--accent-cyan); font-weight: 600; }
    .text-header-title { font-family: var(--font-tech); font-weight: 700; letter-spacing: 0.02em; }
    
    .bg-grid {
      background-size: 50px 50px;
      background-image: linear-gradient(to right, rgba(6, 182, 212, 0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(6, 182, 212, 0.05) 1px, transparent 1px);
    }

    /* Map Tooltip for SVG Fallback */
    .map-tooltip {
      position: absolute; background: rgba(13, 20, 30, 0.95); border: 1px solid var(--accent-cyan);
      color: #fff; padding: 8px 12px; border-radius: 6px; font-family: var(--font-mono); font-size: 12px;
      pointer-events: none; z-index: 100; box-shadow: 0 4px 12px rgba(0,0,0,0.5); transform: translate(-50%, -120%);
    }

    /* Leaflet overrides */
    .leaflet-container { background: transparent !important; }
    .leaflet-popup-content-wrapper { background: rgba(13, 20, 30, 0.95) !important; color: white !important; border: 1px solid var(--accent-cyan); }
    .leaflet-popup-tip { background: rgba(13, 20, 30, 0.95) !important; }
  `}</style>
);

// ============================================
// SHARED UTILS
// ============================================

function generateEllipsePoints(ellipse: EllipseData, numPoints: number = 64): [number, number][] {
    const { center_lat, center_lon, semi_major_km, semi_minor_km, angle_deg } = ellipse;
    const points: [number, number][] = [];
    const kmToDegLat = 1 / 111.32;
    const kmToDegLon = 1 / (111.32 * Math.cos((center_lat * Math.PI) / 180));
    const angleRad = (angle_deg * Math.PI) / 180;

    for (let i = 0; i < numPoints; i++) {
        const theta = (2 * Math.PI * i) / numPoints;
        const x = semi_major_km * Math.cos(theta);
        const y = semi_minor_km * Math.sin(theta);
        const xRot = x * Math.cos(angleRad) - y * Math.sin(angleRad);
        const yRot = x * Math.sin(angleRad) + y * Math.cos(angleRad);
        points.push([center_lat + yRot * kmToDegLat, center_lon + xRot * kmToDegLon]);
    }
    return points;
}

function getOTUColor(value: number): string {
    const clamped = Math.max(0, Math.min(1, value));
    if (clamped < 0.5) {
        const ratio = clamped * 2;
        return `rgb(248, ${Math.round(81 + 107 * ratio)}, ${Math.round(73 - 69 * ratio)})`;
    } else {
        const ratio = (clamped - 0.5) * 2;
        return `rgb(${Math.round(251 - 216 * ratio)}, ${Math.round(188 - 54 * ratio)}, ${Math.round(4 + 50 * ratio)})`;
    }
}

// ============================================
// HELPER: Haversine Distance
// ============================================

function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371; // Radius of the earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

// ============================================
// COMPONENT: Leaflet Map (Primary)
// ============================================

const MapFitter = ({ primaryEllipse, fragmentEllipse }: { primaryEllipse?: EllipseData; fragmentEllipse?: EllipseData }) => {
    const map = useMap();
    useEffect(() => {
        if (primaryEllipse || fragmentEllipse) {
            const ellipse = primaryEllipse || fragmentEllipse!;
            const points = generateEllipsePoints(ellipse);
            // @ts-ignore
            const bounds = L.latLngBounds(points);
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }, [primaryEllipse, fragmentEllipse, map]);
    return null;
};

const CursorTracker = ({ onMove }: { onMove: (lat: number, lng: number) => void }) => {
    useMapEvents({
        mousemove(e: any) { onMove(e.latlng.lat, e.latlng.lng); },
    });
    return null;
};

const ZoomTracker = ({ onZoomChange }: { onZoomChange: (zoom: number) => void }) => {
    const map = useMap();
    useEffect(() => {
        const handleZoom = () => {
            onZoomChange(map.getZoom());
        };
        map.on('zoomend', handleZoom);
        // Set initial zoom
        onZoomChange(map.getZoom());
        return () => {
            map.off('zoomend', handleZoom);
        };
    }, [map, onZoomChange]);
    return null;
};

const LeafletMap = (props: MapViewProps) => {
    const getTileUrl = () => {
        switch (props.baseLayer) {
            case 'dark': return 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
            case 'satellite': return 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
            case 'terrain': return 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png';
            default: return 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
        }
    };

    return (
        <MapContainer center={props.center} zoom={8} style={{ height: '100%', width: '100%', background: 'transparent' }} zoomControl={false} attributionControl={false}>
            <CursorTracker onMove={props.onCursorMove} />
            <ZoomTracker onZoomChange={props.onZoomChange} />
            <MapFitter primaryEllipse={props.primaryEllipse} fragmentEllipse={props.fragmentEllipse} />
            <TileLayer url={getTileUrl()} maxZoom={19} />

            {/* Launch Point Marker */}
            <CircleMarker
                center={props.launchPoint}
                radius={8}
                pathOptions={{
                    color: '#06b6d4',
                    fillColor: '#06b6d4',
                    fillOpacity: 0.8,
                    weight: 3
                }}
            >
                <Popup>
                    <div style={{ fontFamily: 'monospace' }}>
                        <strong>Launch Site</strong><br />
                        Lat: {props.launchPoint[0].toFixed(5)}<br />
                        Lon: {props.launchPoint[1].toFixed(5)}
                    </div>
                </Popup>
            </CircleMarker>

            {props.activeLayers.otu && props.otuGrid && (
                <LayerGroup>
                    {props.otuGrid.features.map((f, i) => (
                        <Polygon key={i} positions={f.geometry.coordinates[0].map((c: any) => [c[1], c[0]])}
                            pathOptions={{ color: getOTUColor(f.properties.q_otu), fillColor: getOTUColor(f.properties.q_otu), fillOpacity: 0.6, weight: 1 }}>
                            <Popup><div style={{ fontFamily: 'monospace' }}>Grid: {f.properties.grid_id}<br />OTU: {f.properties.q_otu.toFixed(3)}</div></Popup>
                        </Polygon>
                    ))}
                </LayerGroup>
            )}

            {props.activeLayers.fragments && props.fragmentEllipse && (
                <Polygon positions={generateEllipsePoints(props.fragmentEllipse)} pathOptions={{ color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 0.15, weight: 2 }}>
                    <Popup>Fragment Ellipse (3σ)</Popup>
                </Polygon>
            )}

            {props.activeLayers.primary && props.primaryEllipse && (
                <Polygon positions={generateEllipsePoints(props.primaryEllipse)} pathOptions={{ color: '#ef4444', fillColor: '#ef4444', fillOpacity: 0.15, weight: 2 }}>
                    <Popup>Primary Ellipse (3σ)</Popup>
                </Polygon>
            )}

            {props.activeLayers.points && props.impactPoints && (
                <LayerGroup>
                    {props.impactPoints.features.map((f, i) => (
                        <CircleMarker key={i} center={[f.geometry.coordinates[1], f.geometry.coordinates[0]]} radius={f.properties.is_fragment ? 2 : 3}
                            pathOptions={{ color: f.properties.is_fragment ? '#f59e0b' : '#ef4444', fillColor: f.properties.is_fragment ? '#f59e0b' : '#ef4444', fillOpacity: 0.8, weight: 0 }}>
                            <Popup>ID: {f.properties.id}<br />Range: {f.properties.downrange_km.toFixed(1)}km</Popup>
                        </CircleMarker>
                    ))}
                </LayerGroup>
            )}
        </MapContainer>
    );
};

// ============================================
// COMPONENT: SVG Map (Fallback)
// ============================================

function useMapProjection(centerLat: number, centerLon: number, zoom: number) {
    const latScale = 1.0 / zoom;
    const lonScale = 1.0 / (zoom * Math.cos(centerLat * Math.PI / 180));
    return useCallback((lat: number, lon: number) => ({
        y: 50 - (lat - centerLat) / latScale * 50,
        x: 50 + (lon - centerLon) / lonScale * 50
    }), [centerLat, centerLon, latScale, lonScale]);
}

const SvgMap = (props: MapViewProps) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [hoverInfo, setHoverInfo] = useState<{ x: number, y: number, content: React.ReactNode } | null>(null);
    const zoomLevel = 3.0;
    const project = useMapProjection(props.center[0], props.center[1], zoomLevel);

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const xPct = (e.clientX - rect.left) / rect.width;
        const yPct = (e.clientY - rect.top) / rect.height;

        // Inverse projection for coords
        const latScale = 1.0 / zoomLevel;
        const lonScale = 1.0 / (zoomLevel * Math.cos(props.center[0] * Math.PI / 180));
        const lat = props.center[0] - ((yPct * 100 - 50) / 50) * latScale;
        const lng = props.center[1] + ((xPct * 100 - 50) / 50) * lonScale;
        props.onCursorMove(lat, lng);
    };

    const handleElementHover = (e: React.MouseEvent, content: React.ReactNode) => {
        e.stopPropagation();
        const rect = containerRef.current?.getBoundingClientRect();
        if (rect) setHoverInfo({ x: e.clientX - rect.left, y: e.clientY - rect.top, content });
    };

    const renderEllipse = (data: EllipseData, color: string, label: string) => {
        const points = generateEllipsePoints(data).map(p => {
            const xy = project(p[0], p[1]);
            return `${xy.x},${xy.y}`;
        }).join(' ');
        return <polygon points={points} fill={color} fillOpacity={0.15} stroke={color} strokeWidth={0.5} vectorEffect="non-scaling-stroke" onMouseEnter={(e) => handleElementHover(e, label)} onMouseLeave={() => setHoverInfo(null)} />;
    };

    const launchPos = project(props.launchPoint[0], props.launchPoint[1]);
    const bg = props.baseLayer === 'dark' ? '#050a10' : props.baseLayer === 'satellite' ? 'linear-gradient(to bottom, #0f172a, #1e293b)' : '#1e293b';

    return (
        <div ref={containerRef} style={{ position: 'absolute', inset: 0, zIndex: 0, borderRadius: '16px', overflow: 'hidden', background: bg, cursor: 'crosshair' }} onMouseMove={handleMouseMove} onMouseLeave={() => setHoverInfo(null)}>
            <div className="absolute inset-0 bg-grid pointer-events-none opacity-20"></div>
            <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
                {props.activeLayers.otu && props.otuGrid && props.otuGrid.features.map((f, i) => (
                    <polygon key={i} points={f.geometry.coordinates[0].map((c: any) => { const p = project(c[1], c[0]); return `${p.x},${p.y}`; }).join(' ')}
                        fill={getOTUColor(f.properties.q_otu)} fillOpacity={0.4} stroke="none" onMouseEnter={(e) => handleElementHover(e, `OTU: ${f.properties.q_otu.toFixed(2)}`)} onMouseLeave={() => setHoverInfo(null)} />
                ))}
                {props.activeLayers.fragments && props.fragmentEllipse && renderEllipse(props.fragmentEllipse, '#f59e0b', 'Fragment Field (3σ)')}
                {props.activeLayers.primary && props.primaryEllipse && renderEllipse(props.primaryEllipse, '#ef4444', 'Primary Drop Zone (3σ)')}
                {props.activeLayers.points && props.impactPoints && props.impactPoints.features.map((f, i) => {
                    const p = project(f.geometry.coordinates[1], f.geometry.coordinates[0]);
                    return <circle key={i} cx={p.x} cy={p.y} r={f.properties.is_fragment ? 0.3 : 0.4} fill={f.properties.is_fragment ? '#f59e0b' : '#ef4444'} onMouseEnter={(e) => handleElementHover(e, `ID: ${f.properties.id}`)} onMouseLeave={() => setHoverInfo(null)} />
                })}
                <circle cx={launchPos.x} cy={launchPos.y} r={0.8} fill="#06b6d4" stroke="white" strokeWidth={0.2} />
            </svg>
            {hoverInfo && <div className="map-tooltip" style={{ left: hoverInfo.x, top: hoverInfo.y }}>{hoverInfo.content}</div>}
            <div className="absolute bottom-4 left-4 text-[10px] text-gray-500 font-mono">RENDERER: SVG (FALLBACK)</div>
        </div>
    );
};

// ============================================
// MAIN MAP CONTROLLER
// ============================================

interface MapViewProps {
    center: [number, number];
    launchPoint: [number, number];
    primaryEllipse?: EllipseData;
    fragmentEllipse?: EllipseData;
    impactPoints?: GeoJSONFeatureCollection<GeoJSONPoint, ImpactPointProperties>;
    otuGrid?: GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties>;
    activeLayers: ActiveLayers;
    onZoomChange: (zoom: number) => void;
    onCursorMove: (lat: number, lng: number) => void;
    baseLayer: 'satellite' | 'dark' | 'terrain' | 'streets';
}

const MapView = (props: MapViewProps) => {
    if (IS_LEAFLET_AVAILABLE) {
        return <LeafletMap {...props} />;
    }
    return <SvgMap {...props} />;
};

// ============================================
// COMPONENT: App
// ============================================

const LAUNCH_LAT = 45.72341;
const LAUNCH_LON = 63.32275;

// --- Enhanced Tech UI Components ---

const TechHeader: React.FC<{ title: string; icon?: React.ElementType }> = ({ title, icon: Icon }) => (
    <div className="flex items-center gap-3 mb-5 text-[#06b6d4] uppercase tracking-wider text-sm font-bold border-b border-[rgba(6,182,212,0.3)] pb-3">
        {Icon && <Icon size={16} strokeWidth={2.5} />}
        <span className="text-header-title">{title}</span>
        <div className="flex-1" />
        <div className="flex gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-[#06b6d4]"></div>
            <div className="w-1.5 h-1.5 rounded-full bg-[#06b6d4] opacity-50"></div>
            <div className="w-1.5 h-1.5 rounded-full bg-[#06b6d4] opacity-25"></div>
        </div>
    </div>
);

const TechButton: React.FC<{
    children: React.ReactNode;
    onClick?: () => void;
    primary?: boolean;
    icon?: React.ElementType;
    disabled?: boolean;
}> = ({ children, onClick, primary, icon: Icon, disabled }) => (
    <button
        onClick={onClick}
        disabled={disabled}
        className={`
      w-full py-4 px-5 rounded-lg flex items-center justify-center gap-3 font-bold text-sm uppercase tracking-wider transition-all relative overflow-hidden
      ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-[1.02] active:scale-[0.98]'}
      ${primary
                ? 'bg-gradient-to-r from-[rgba(6,182,212,0.15)] to-[rgba(6,182,212,0.05)] border-2 border-[#06b6d4] text-[#06b6d4] hover:bg-[#06b6d4] hover:text-white btn-primary-glow'
                : 'bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.15)] text-[#94a3b8] hover:bg-[rgba(255,255,255,0.08)] hover:text-white hover:border-[rgba(255,255,255,0.3)]'}
    `}
    >
        {Icon && <Icon size={18} className={primary && !disabled ? "animate-pulse" : ""} />}
        <span>{children}</span>
        {primary && !disabled && (
            <div className="absolute inset-0 shimmer-effect pointer-events-none"></div>
        )}
    </button>
);

const StatReadout: React.FC<{ label: string; value: string | number; unit?: string; color?: string }> = ({ label, value, unit, color = "#06b6d4" }) => (
    <div className="bg-[rgba(0,0,0,0.3)] p-4 rounded-lg border-l-3 border-[rgba(255,255,255,0.1)] hover:border-l-[#06b6d4] transition-all hover:bg-[rgba(0,0,0,0.4)] group" style={{ borderLeftWidth: '3px' }}>
        <div className="text-tech-label mb-2 group-hover:text-white transition-colors">{label}</div>
        <div className="font-mono text-2xl text-white flex items-baseline gap-2" style={{ textShadow: `0 0 15px ${color}50` }}>
            {value}
            {unit && <span className="text-xs font-semibold" style={{ color }}>{unit}</span>}
        </div>
    </div>
);

const TechAccordion: React.FC<{ title: string; isOpen: boolean; onToggle: () => void; children: React.ReactNode }> = ({ title, isOpen, onToggle, children }) => (
    <div className="border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.02)] mb-3 rounded-lg overflow-hidden">
        <button
            onClick={onToggle}
            className={`accordion-header w-full flex items-center justify-between text-sm uppercase font-bold tracking-wider transition-all ${isOpen ? 'text-[#06b6d4] bg-[rgba(6,182,212,0.08)]' : 'text-[#94a3b8] hover:text-white hover:bg-[rgba(255,255,255,0.03)]'}`}
            style={{ padding: '14px 16px' }}
        >
            <span>{title}</span>
            <div className={`transition-transform duration-200 ${isOpen ? 'rotate-0' : '-rotate-90'}`}>
                <ChevronDown size={16} />
            </div>
        </button>
        <div className={`transition-all duration-300 ${isOpen ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'}`}>
            <div className="accordion-content border-t border-[rgba(255,255,255,0.05)]" style={{ padding: '20px' }}>
                {children}
            </div>
        </div>
    </div>
);

// Enhanced Slider Component
const TechSlider: React.FC<{
    label: string;
    value: number;
    onChange: (val: number) => void;
    min: number;
    max: number;
    step: number;
    unit?: string;
}> = ({ label, value, onChange, min, max, step, unit }) => {
    const percentage = ((value - min) / (max - min)) * 100;

    return (
        <div className="mb-6">
            <div className="flex justify-between items-center mb-3">
                <span className="text-tech-label">{label}</span>
                <div className="flex items-center gap-2">
                    <span className="text-tech-value text-lg">{value.toLocaleString()}</span>
                    {unit && <span className="text-xs text-[#475569]">{unit}</span>}
                </div>
            </div>
            <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={value}
                onChange={(e) => onChange(parseInt(e.target.value))}
                style={{ '--value-percent': `${percentage}%` } as React.CSSProperties}
            />
            <div className="flex justify-between text-[10px] text-[#475569] mt-2">
                <span>{min.toLocaleString()}</span>
                <span>{max.toLocaleString()}</span>
            </div>
        </div>
    );
};

// Toggle Switch Component
const TechToggle: React.FC<{ label: string; checked: boolean; onChange: () => void }> = ({ label, checked, onChange }) => (
    <button
        onClick={onChange}
        className="w-full flex items-center justify-between p-3 bg-[rgba(255,255,255,0.02)] rounded-lg border border-[rgba(255,255,255,0.05)] hover:border-[rgba(255,255,255,0.15)] transition-all"
    >
        <span className="text-sm uppercase text-[#94a3b8] tracking-wide">{label}</span>
        <div className={`w-12 h-6 rounded-full relative transition-all ${checked ? 'bg-[#06b6d4]' : 'bg-[rgba(255,255,255,0.1)]'}`}>
            <div className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow-lg transition-all ${checked ? 'right-1' : 'left-1'}`}></div>
        </div>
    </button>
);

// --- Mock Data Generators ---
function generateMockEllipse(centerLat: number, centerLon: number, isFragment: boolean = false): EllipseData {
    const semiMajor = isFragment ? 15 + Math.random() * 5 : 25 + Math.random() * 10;
    const semiMinor = isFragment ? 8 + Math.random() * 3 : 12 + Math.random() * 5;
    return {
        center_lat: centerLat + (Math.random() - 0.5) * 0.5,
        center_lon: centerLon + (Math.random() - 0.5) * 0.5,
        semi_major_km: semiMajor,
        semi_minor_km: semiMinor,
        angle_deg: Math.random() * 180
    };
}

function generateMockImpactPoints(count: number): GeoJSONFeatureCollection<GeoJSONPoint, ImpactPointProperties> {
    const features: GeoJSONFeatureCollection<GeoJSONPoint, ImpactPointProperties>['features'] = [];
    const centerLat = 48.0, centerLon = 66.5;
    for (let i = 0; i < count; i++) {
        const isFragment = Math.random() > 0.6;
        const u1 = Math.random(), u2 = Math.random();
        const z0 = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
        const z1 = Math.sqrt(-2 * Math.log(u1)) * Math.sin(2 * Math.PI * u2);
        features.push({
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [centerLon + z0 * (isFragment ? 0.7 : 0.5), centerLat + z1 * (isFragment ? 0.5 : 0.35)] },
            properties: { id: i + 1, is_fragment: isFragment, downrange_km: 306 + z0 * 25, crossrange_km: z1 * 15, velocity_m_s: 200 + Math.random() * 100 },
        });
    }
    return { type: 'FeatureCollection', features };
}

function generateMockOTUGrid(): GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties> {
    const features: GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties>['features'] = [];
    const centerLat = 48.0, centerLon = 66.5, cellSize = 0.1;
    for (let i = -5; i < 5; i++) {
        for (let j = -5; j < 5; j++) {
            const lat = centerLat + i * cellSize, lon = centerLon + j * cellSize;
            const q_otu = Math.max(0.1, Math.min(0.95, 0.5 + 0.3 * Math.sin(i * 0.5) + 0.2 * Math.cos(j * 0.5) + (Math.random() - 0.5) * 0.2));
            features.push({
                type: 'Feature',
                geometry: { type: 'Polygon', coordinates: [[[lon, lat], [lon + cellSize, lat], [lon + cellSize, lat + cellSize], [lon, lat + cellSize], [lon, lat]]] },
                properties: { grid_id: `cell_${i + 5}_${j + 5}`, q_ndvi: Math.random() * 0.8 + 0.1, q_si: Math.random() * 0.6 + 0.3, q_bi: Math.random() * 0.7 + 0.2, q_relief: Math.random() * 0.4 + 0.5, q_otu, q_fire: Math.random() * 0.5 },
            });
        }
    }
    return { type: 'FeatureCollection', features };
}

function runMockSimulation(iterations: number): Promise<{
    primaryEllipse: EllipseData;
    fragmentEllipse: EllipseData;
    impactPoints: GeoJSONFeatureCollection<GeoJSONPoint, ImpactPointProperties>;
    otuGrid: GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties>;
    stats: SimulationStats;
}> {
    return new Promise((resolve) => {
        setTimeout(() => {
            const centerLat = 48.0 + (Math.random() - 0.5) * 0.2;
            const centerLon = 66.5 + (Math.random() - 0.5) * 0.2;

            const primaryEllipse = generateMockEllipse(centerLat, centerLon, false);
            const fragmentEllipse = generateMockEllipse(centerLat, centerLon, true);
            const impactPoints = generateMockImpactPoints(Math.floor(iterations / 10));
            const otuGrid = generateMockOTUGrid();

            const rangeKm = calculateDistance(LAUNCH_LAT, LAUNCH_LON, primaryEllipse.center_lat, primaryEllipse.center_lon);

            resolve({
                primaryEllipse,
                fragmentEllipse,
                impactPoints,
                otuGrid,
                stats: {
                    impactPoints: impactPoints.features.length,
                    range: `${rangeKm.toFixed(1)}`,
                    semiMajorAxis: primaryEllipse.semi_major_km,
                    avgOtu: 0.65 + Math.random() * 0.3,
                    primaryEllipse: {
                        a: primaryEllipse.semi_major_km * 2,
                        b: primaryEllipse.semi_minor_km * 2,
                        angle: primaryEllipse.angle_deg,
                    },
                    fragmentEllipse: {
                        a: fragmentEllipse.semi_major_km * 2,
                        b: fragmentEllipse.semi_minor_km * 2,
                        angle: fragmentEllipse.angle_deg,
                    },
                }
            });
        }, 1500); // Simulate network delay
    });
}

// --- Main Application ---
export default function App() {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [resultsOpen, setResultsOpen] = useState(true);
    const [activeSection, setActiveSection] = useState<string | null>('monte');

    const [isSimulating, setIsSimulating] = useState(false);
    const [progress, setProgress] = useState(0);
    const [progressMessage, setProgressMessage] = useState('Initializing...'); // <--- New state
    const [simDone, setSimDone] = useState(false);

    const [cursorCoords, setCursorCoords] = useState({ lat: LAUNCH_LAT, lng: LAUNCH_LON });
    const [mapZoom, setMapZoom] = useState(8);

    const [baseLayer, setBaseLayer] = useState<'satellite' | 'dark' | 'terrain' | 'streets'>('dark');
    const [activeLayers, setActiveLayers] = useState<ActiveLayers>({
        primary: true, fragments: true, points: false, otu: false, ndvi: false, slope: false,
    });

    const [simConfig, setSimConfig] = useState({ iterations: 100, useGpu: true, launchLat: LAUNCH_LAT, launchLon: LAUNCH_LON, azimuth: 45.0 });

    const [stats, setStats] = useState<SimulationStats | null>(null);
    const [primaryEllipse, setPrimaryEllipse] = useState<EllipseData | undefined>();
    const [fragmentEllipse, setFragmentEllipse] = useState<EllipseData | undefined>();
    const [impactPoints, setImpactPoints] = useState<GeoJSONFeatureCollection<GeoJSONPoint, ImpactPointProperties> | undefined>();
    const [otuGrid, setOtuGrid] = useState<GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties> | undefined>();

    const toggleLayer = (layer: keyof ActiveLayers) => setActiveLayers(prev => ({ ...prev, [layer]: !prev[layer] }));

    const [backendAvailable, setBackendAvailable] = useState<boolean | null>(null);
    const [isDemoMode, setIsDemoMode] = useState(false);

    // Check backend health on mount
    useEffect(() => {
        checkHealth().then(available => {
            setBackendAvailable(available);
            setIsDemoMode(!available);
        });
    }, []);

    const runSimulation = async () => {
        setIsSimulating(true);
        setProgress(0);
        setProgressMessage('Initializing...');
        setSimDone(false);

        // Check if backend is available
        const isBackendUp = await checkHealth();
        setBackendAvailable(isBackendUp);
        setIsDemoMode(!isBackendUp);

        if (!isBackendUp) {
            // Use mock simulation
            setProgressMessage('Backend unavailable, running in demo mode...');

            try {
                // Simulate progress
                const interval = setInterval(() => {
                    setProgress(prev => {
                        if (prev >= 90) {
                            clearInterval(interval);
                            return 90;
                        }
                        return prev + 10;
                    });
                }, 200);

                // Run mock simulation
                const mockResult = await runMockSimulation(simConfig.iterations);

                clearInterval(interval);
                setProgress(100);

                // Update state with mock results
                setPrimaryEllipse(mockResult.primaryEllipse);
                setFragmentEllipse(mockResult.fragmentEllipse);
                setImpactPoints(mockResult.impactPoints);
                setOtuGrid(mockResult.otuGrid);
                setStats(mockResult.stats);

                setActiveLayers(l => ({ ...l, points: true, otu: true }));
                setSimDone(true);
                setResultsOpen(true);

            } catch (error) {
                console.error('Mock simulation failed:', error);
                alert(`Demo simulation failed: ${error}`);
            } finally {
                setIsSimulating(false);
            }
            return;
        }

        try {
            // Call the real API
            const { job_id } = await apiRunSimulation({
                iterations: simConfig.iterations,
                use_gpu: simConfig.useGpu,
                launch_lat: simConfig.launchLat,
                launch_lon: simConfig.launchLon,
                azimuth: simConfig.azimuth,
            });

            // Poll for results
            const result = await pollSimulation(job_id, (status) => {
                setProgress(status.progress);
                if (status.message) setProgressMessage(status.message);
            });

            // Update state with real results
            if (result.primary_ellipse) {
                setPrimaryEllipse(result.primary_ellipse);
            }
            if (result.fragment_ellipse) {
                setFragmentEllipse(result.fragment_ellipse);
            }
            if (result.impact_points) {
                setImpactPoints(result.impact_points as any);
            }
            if (result.otu_grid) {
                setOtuGrid(result.otu_grid as any);
            }
            if (result.stats) {
                const rangeKm = result.primary_ellipse
                    ? calculateDistance(simConfig.launchLat, simConfig.launchLon, result.primary_ellipse.center_lat, result.primary_ellipse.center_lon)
                    : 0;

                setStats({
                    impactPoints: result.stats.primary_impacts + result.stats.fragment_impacts,
                    range: `${rangeKm.toFixed(1)}`,
                    semiMajorAxis: result.primary_ellipse?.semi_major_km || 0,
                    avgOtu: 0.72,  // TODO: Calculate from OTU grid stats
                    primaryEllipse: {
                        a: (result.primary_ellipse?.semi_major_km || 0) * 2,
                        b: (result.primary_ellipse?.semi_minor_km || 0) * 2,
                        angle: result.primary_ellipse?.angle_deg || 0,
                    },
                    fragmentEllipse: {
                        a: (result.fragment_ellipse?.semi_major_km || 0) * 2,
                        b: (result.fragment_ellipse?.semi_minor_km || 0) * 2,
                        angle: result.fragment_ellipse?.angle_deg || 0,
                    },
                });
            }

            setActiveLayers(l => ({ ...l, points: true, otu: true }));
            setSimDone(true);
            setResultsOpen(true);

        } catch (error) {
            console.error('Simulation failed:', error);
            alert(`Simulation Failed: ${error}`);
            // Do not use mock fallback on error
        } finally {
            setIsSimulating(false);
            setProgress(100);
        }
    };

    return (
        <>
            <GlobalStyles />
            <div className="relative w-screen h-screen overflow-hidden bg-[#050a10]" style={{ padding: '20px' }}>

                {/* ========== MAP BACKGROUND ========== */}
                <div style={{ position: 'absolute', inset: '20px', borderRadius: '16px', border: '1px solid rgba(6, 182, 212, 0.2)', overflow: 'hidden', zIndex: 0 }}>
                    <MapView
                        center={[48.0, 66.5]}
                        launchPoint={[simConfig.launchLat, simConfig.launchLon]}
                        primaryEllipse={primaryEllipse}
                        fragmentEllipse={fragmentEllipse}
                        impactPoints={impactPoints}
                        otuGrid={otuGrid}
                        onZoomChange={setMapZoom}
                        activeLayers={activeLayers}
                        onCursorMove={(lat, lng) => setCursorCoords({ lat, lng })}
                        baseLayer={baseLayer}
                    />
                </div>

                {/* ========== HEADER ========== */}
                <header style={{ position: 'fixed', top: '28px', left: '50%', transform: 'translateX(-50%)', width: '92%', maxWidth: '1000px', height: '60px', zIndex: 50 }}
                    className="glass-panel rounded-full flex items-center justify-between px-8">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#06b6d4] to-[#0891b2] flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.4)]">
                            <Rocket className="text-white rotate-45" size={22} />
                        </div>
                        <div>
                            <h1 className="text-white font-bold tracking-tight text-xl leading-none uppercase text-header-title">
                                Orbital <span className="text-[#06b6d4]">Command</span>
                            </h1>
                            <div className="text-[11px] text-[#64748b] tracking-[0.2em] uppercase font-mono mt-0.5">Mission Control v2.0</div>
                        </div>
                    </div>

                    <div className="flex items-center gap-5">
                        {/* Status Badge */}
                        <div className="px-4 py-2 rounded-full border border-[rgba(255,255,255,0.1)] text-xs font-mono uppercase bg-[rgba(0,0,0,0.3)] flex items-center gap-3">
                            <div className={`w-2.5 h-2.5 rounded-full ${simDone ? 'bg-green-500 status-ready' : isSimulating ? 'bg-amber-500 status-computing' : 'bg-slate-500'}`}></div>
                            <span className="text-[#94a3b8]">{isSimulating ? 'COMPUTING' : simDone ? 'READY' : 'IDLE'}</span>
                            {isSimulating && <span className="text-[#06b6d4] font-bold">{progress}%</span>}
                        </div>

                        {/* Demo Mode Badge */}
                        {isDemoMode && (
                            <div className="px-3 py-1 rounded-full border border-amber-500/30 text-xs font-mono uppercase bg-amber-500/10 flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-amber-500"></div>
                                <span className="text-amber-300">DEMO</span>
                            </div>
                        )}

                        <div className="h-8 w-px bg-[rgba(255,255,255,0.1)]"></div>

                        {/* Layer Buttons */}
                        <div className="flex items-center gap-1">
                            <button onClick={() => setBaseLayer('satellite')} className={`p-2.5 rounded-lg transition-all ${baseLayer === 'satellite' ? 'text-[#06b6d4] bg-[rgba(6,182,212,0.15)]' : 'text-[#64748b] hover:text-white hover:bg-[rgba(255,255,255,0.05)]'}`} title="Satellite">
                                <Globe size={18} />
                            </button>
                            <button onClick={() => setBaseLayer('dark')} className={`p-2.5 rounded-lg transition-all ${baseLayer === 'dark' ? 'text-[#06b6d4] bg-[rgba(6,182,212,0.15)]' : 'text-[#64748b] hover:text-white hover:bg-[rgba(255,255,255,0.05)]'}`} title="Dark">
                                <Moon size={18} />
                            </button>
                            <button className="p-2.5 rounded-lg text-[#64748b] hover:text-white hover:bg-[rgba(255,255,255,0.05)] transition-all" title="Settings">
                                <Settings size={18} />
                            </button>
                        </div>
                    </div>
                </header>

                {/* ========== LEFT SIDEBAR ========== */}
                <aside style={{ position: 'fixed', top: '110px', left: '40px', width: '340px', zIndex: 40 }}
                    className={`transition-all duration-300 ${sidebarOpen ? 'translate-x-0 opacity-100' : '-translate-x-[400px] opacity-0'}`}>
                    <div className="glass-panel rounded-2xl border border-[rgba(255,255,255,0.1)] border-l-[3px] border-l-[#06b6d4]">
                        {/* Panel Header - 20px padding */}
                        <div className="px-5 py-4 bg-[rgba(0,0,0,0.3)] flex justify-center items-center border-b border-[rgba(255,255,255,0.05)] rounded-t-2xl relative">
                            <h2 className="text-[#06b6d4] text-lg font-bold uppercase tracking-wider flex items-center gap-3">
                                <Grid size={18} /> Configuration
                            </h2>
                            <div className="absolute right-5 text-[10px] text-[#475569] font-mono bg-[rgba(0,0,0,0.3)] px-2 py-1 rounded">SYS.01</div>
                        </div>
                        {/* Panel Content - 20px padding */}
                        <div className="p-5 max-h-[calc(100vh-220px)] overflow-y-auto">
                            <TechAccordion title="Monte Carlo Simulation" isOpen={activeSection === 'monte'} onToggle={() => setActiveSection(activeSection === 'monte' ? null : 'monte')}>
                                <TechSlider
                                    label="Iterations"
                                    value={simConfig.iterations}
                                    onChange={(val) => setSimConfig({ ...simConfig, iterations: val })}
                                    min={100}
                                    max={10000}
                                    step={100}
                                />
                                <TechToggle
                                    label="GPU Acceleration"
                                    checked={simConfig.useGpu}
                                    onChange={() => setSimConfig({ ...simConfig, useGpu: !simConfig.useGpu })}
                                />
                                <div className="mt-5">
                                    <TechButton primary onClick={runSimulation} disabled={isSimulating} icon={Play}>
                                        {isSimulating ? `Processing ${progress}%` : 'Initiate Simulation'}
                                    </TechButton>
                                </div>
                            </TechAccordion>

                            <TechAccordion title="Ecological Assessment" isOpen={activeSection === 'otu'} onToggle={() => setActiveSection(activeSection === 'otu' ? null : 'otu')}>
                                <div className="text-sm text-[#64748b] mb-4 flex items-center gap-2">
                                    <Target size={14} /> Date: <span className="text-[#06b6d4] font-mono">2024-09-09</span>
                                </div>
                                <TechButton icon={Leaf}>Calculate OTU Index</TechButton>
                            </TechAccordion>
                        </div>
                    </div>
                </aside>

                {/* Sidebar Toggle */}
                {!sidebarOpen && (
                    <button
                        onClick={() => setSidebarOpen(true)}
                        style={{ position: 'fixed', top: '110px', left: '20px', zIndex: 40 }}
                        className="panel-toggle p-4 glass-panel border-r-[3px] border-r-[#06b6d4] text-[#06b6d4] rounded-r-xl hover:bg-[rgba(6,182,212,0.1)]"
                    >
                        <ChevronRight size={20} />
                    </button>
                )}

                {/* ========== RIGHT PANEL ========== */}
                <aside style={{ position: 'fixed', top: '110px', right: '40px', width: '400px', zIndex: 40 }}
                    className={`transition-all duration-300 ${resultsOpen ? 'translate-x-0 opacity-100' : 'translate-x-[460px] opacity-0'}`}>
                    <div className="glass-panel rounded-2xl border border-[rgba(255,255,255,0.1)] border-r-[3px] border-r-[#ef4444]">
                        {/* Panel Header - centered title */}
                        <div className="px-5 py-4 bg-[rgba(0,0,0,0.3)] flex justify-center items-center border-b border-[rgba(255,255,255,0.05)] rounded-t-2xl relative">
                            <h2 className="text-[#ef4444] text-lg font-bold uppercase tracking-wider flex items-center gap-3">
                                <Activity size={18} /> Telemetry
                            </h2>
                            <button onClick={() => setResultsOpen(false)} className="absolute right-5 text-[#64748b] hover:text-white p-1 hover:bg-[rgba(255,255,255,0.1)] rounded transition-all">
                                <Minimize size={16} />
                            </button>
                        </div>
                        {/* Panel Content - 20px padding */}
                        <div className="p-5 max-h-[calc(100vh-220px)] overflow-y-auto">
                            {simDone && stats ? (
                                <div className="space-y-6">
                                    <TechHeader title="Mission Statistics" icon={Zap} />
                                    <div className="grid grid-cols-2 gap-3">
                                        <StatReadout label="Impact Points" value={stats.impactPoints} />
                                        <StatReadout label="Range (3σ)" value={stats.semiMajorAxis} unit="km" />
                                        <StatReadout label="Mean OTU" value={stats.avgOtu} color="#10b981" />
                                        <StatReadout label="Sim Time" value="3.2" unit="sec" />
                                    </div>

                                    <TechHeader title="Dispersion Ellipses" icon={Target} />
                                    <div className="bg-[rgba(0,0,0,0.3)] border border-[rgba(255,255,255,0.05)] rounded-xl p-4">
                                        <table className="w-full text-sm font-mono">
                                            <thead className="text-[#64748b] border-b border-[rgba(255,255,255,0.08)]">
                                                <tr>
                                                    <th className="text-left py-2 font-medium">Zone</th>
                                                    <th className="text-right py-2 font-medium">Axes (km)</th>
                                                    <th className="text-right py-2 font-medium">Angle</th>
                                                </tr>
                                            </thead>
                                            <tbody className="text-white">
                                                <tr className="border-b border-[rgba(255,255,255,0.03)]">
                                                    <td className="py-3 text-[#ef4444] font-bold">PRIMARY</td>
                                                    <td className="text-right">{stats.primaryEllipse.a} × {stats.primaryEllipse.b}</td>
                                                    <td className="text-right">{stats.primaryEllipse.angle}°</td>
                                                </tr>
                                                <tr>
                                                    <td className="py-3 text-[#f59e0b] font-bold">FRAGMENTS</td>
                                                    <td className="text-right">{stats.fragmentEllipse.a} × {stats.fragmentEllipse.b}</td>
                                                    <td className="text-right">{stats.fragmentEllipse.angle}°</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>

                                    <TechHeader title="Visibility Layers" icon={Layers} />
                                    <div className="space-y-2">
                                        {[
                                            { id: 'primary', label: 'Primary Ellipse', color: '#ef4444' },
                                            { id: 'fragments', label: 'Fragment Field', color: '#f59e0b' },
                                            { id: 'points', label: 'Impact Points', color: '#06b6d4' },
                                            { id: 'otu', label: 'OTU Heatmap', color: '#10b981' },
                                        ].map((layer) => (
                                            <button
                                                key={layer.id}
                                                onClick={() => toggleLayer(layer.id as keyof ActiveLayers)}
                                                className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all ${activeLayers[layer.id as keyof ActiveLayers] ? 'bg-[rgba(255,255,255,0.05)] border-[rgba(255,255,255,0.15)]' : 'bg-transparent border-transparent opacity-60 hover:opacity-100'}`}
                                            >
                                                <div className="flex items-center gap-3">
                                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: layer.color, boxShadow: `0 0 8px ${layer.color}` }}></div>
                                                    <span className="text-sm font-medium text-[#94a3b8]">{layer.label}</span>
                                                </div>
                                                <div className={`w-10 h-5 rounded-full relative transition-all ${activeLayers[layer.id as keyof ActiveLayers] ? 'bg-[#06b6d4]' : 'bg-[rgba(255,255,255,0.1)]'}`}>
                                                    <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow-md transition-all ${activeLayers[layer.id as keyof ActiveLayers] ? 'right-0.5' : 'left-0.5'}`}></div>
                                                </div>
                                            </button>
                                        ))}
                                    </div>

                                    <div className="pt-4 flex gap-3">
                                        <TechButton icon={Download}>Export JSON</TechButton>
                                        <TechButton icon={FileText}>Export CSV</TechButton>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center py-16 relative">
                                    <Activity size={56} className="mx-auto mb-5 text-[#475569] empty-state-icon" />
                                    <div className="font-mono text-sm uppercase text-[#64748b] mb-2">Awaiting Data Stream</div>
                                    <div className="text-xs text-[#475569]">Run a simulation to view results</div>
                                    <div className="absolute inset-0 scan-effect pointer-events-none overflow-hidden"></div>
                                </div>
                            )}
                        </div>
                    </div>
                </aside>

                {/* Results Toggle */}
                {!resultsOpen && (
                    <button
                        onClick={() => setResultsOpen(true)}
                        style={{ position: 'fixed', top: '110px', right: '20px', zIndex: 40 }}
                        className="panel-toggle p-4 glass-panel border-l-[3px] border-l-[#ef4444] text-[#ef4444] rounded-l-xl hover:bg-[rgba(239,68,68,0.1)]"
                    >
                        <ChevronDown className="rotate-90" size={20} />
                    </button>
                )}

                {/* ========== FOOTER ========== */}
                <footer style={{ position: 'fixed', bottom: '28px', left: '50%', transform: 'translateX(-50%)', zIndex: 50 }}
                    className="glass-panel rounded-full px-6 py-3 flex items-center gap-6 text-xs uppercase font-mono tracking-wider">
                    <div className="coord-group flex items-center gap-2">
                        <Crosshair size={14} className="text-[#06b6d4]" />
                        <span className="text-[#64748b]">LAT:</span>
                        <span className="coord-value">{cursorCoords.lat.toFixed(5)}</span>
                    </div>
                    <div className="w-px h-4 bg-[rgba(255,255,255,0.15)]"></div>
                    <div className="coord-group flex items-center gap-2">
                        <Crosshair size={14} className="text-[#06b6d4]" />
                        <span className="text-[#64748b]">LON:</span>
                        <span className="coord-value">{cursorCoords.lng.toFixed(5)}</span>
                    </div>
                    <div className="w-px h-4 bg-[rgba(255,255,255,0.15)]"></div>
                    <div className="flex items-center gap-2">
                        <span className="text-[#64748b]">ZOOM:</span>
                        <span className="coord-value">{String(mapZoom).padStart(2, '0')}X</span>
                    </div>
                </footer>

                {/* Corner Decorations */}
                <div className="fixed pointer-events-none opacity-30" style={{ top: '20px', left: '20px', width: '80px', height: '80px', borderLeft: '2px solid #06b6d4', borderTop: '2px solid #06b6d4', borderRadius: '16px 0 0 0' }}></div>
                <div className="fixed pointer-events-none opacity-30" style={{ bottom: '20px', right: '20px', width: '80px', height: '80px', borderRight: '2px solid #06b6d4', borderBottom: '2px solid #06b6d4', borderRadius: '0 0 16px 0' }}></div>
            </div>
        </>
    );
}