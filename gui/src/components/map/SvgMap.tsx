import React, { useCallback, useRef, useState } from 'react';
import { MapViewProps, EllipseData } from '../../types';
import { generateEllipsePoints, getOTUColor } from '../../utils';

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

export default SvgMap;
