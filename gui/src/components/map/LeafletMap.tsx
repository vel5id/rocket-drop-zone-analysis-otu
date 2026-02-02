import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import React, { useEffect } from 'react';
import { CircleMarker, GeoJSON, LayerGroup, MapContainer, Polyline, Popup, TileLayer, useMap, useMapEvents } from 'react-leaflet';
import { EllipseData, GeoJSONFeatureCollection, GeoJSONPoint, GeoJSONPolygon, ImpactPointProperties, MapViewProps, OTUCellProperties } from '../../types';
import { generateEllipsePoints, getOTUColor } from '../../utils';

const MapFitter = ({ primaryEllipse, fragmentEllipse }: { primaryEllipse?: EllipseData; fragmentEllipse?: EllipseData }) => {
    const map = useMap();
    useEffect(() => {
        if (primaryEllipse || fragmentEllipse) {
            const ellipse = primaryEllipse || fragmentEllipse!;
            const points = generateEllipsePoints(ellipse);
            // @ts-ignore - Leaflet types sometimes mismatch with tuples
            const bounds = L.latLngBounds(points);
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }, [primaryEllipse, fragmentEllipse, map]);
    return null;
};

const CursorTracker = ({ onMove }: { onMove: (lat: number, lng: number) => void }) => {
    useMapEvents({
        mousemove(e) { onMove(e.latlng.lat, e.latlng.lng); },
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

// Optimization: Memoize impact points rendering
const ImpactPointsLayer = React.memo(({ points }: { points: GeoJSONFeatureCollection<GeoJSONPoint, ImpactPointProperties> }) => {
    return (
        <LayerGroup>
            {points.features?.map((f, i) => (
                <CircleMarker
                    key={f.properties.id || i}
                    center={[f.geometry.coordinates[1], f.geometry.coordinates[0]]}
                    radius={f.properties.is_fragment ? 2 : 3}
                    pathOptions={{
                        color: f.properties.is_fragment ? '#f59e0b' : '#ef4444',
                        fillColor: f.properties.is_fragment ? '#f59e0b' : '#ef4444',
                        fillOpacity: 0.8,
                        weight: 0
                    }}
                >
                    <Popup>
                        ID: {f.properties.id}<br />
                        Range: {f.properties.downrange_km?.toFixed(1) ?? 'N/A'}km
                    </Popup>
                </CircleMarker>
            ))}
        </LayerGroup>
    );
});

// Optimization: Memoize OTU grid rendering
const OTULayer = React.memo(({ grid }: { grid: GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties> }) => {
    // Style function for GeoJSON
    const style = (feature: any) => {
        const missing = feature?.properties?.missing_data;
        if (missing && missing.length > 0) {
            return {
                color: '#9333ea', // Purple-600
                fillColor: '#9333ea',
                fillOpacity: 0.8,
                weight: 1
            };
        }

        const val = feature?.properties?.q_otu;
        // console.log('OTU Value:', val); // Debug one frame if needed, but might spam
        return {
            color: getOTUColor(typeof val === 'number' ? val : 0.5),
            fillColor: getOTUColor(typeof val === 'number' ? val : 0.5),
            fillOpacity: 0.6,
            weight: 1
        };
    };

    // Binding popups with enhanced missing data display
    const onEachFeature = (feature: any, layer: any) => {
        if (feature.properties) {
            const props = feature.properties;
            const missing = props.missing_data;
            const hasMissing = missing && missing.length > 0;

            // Build missing data section
            let missingHtml = '';
            if (hasMissing) {
                const missingItems = missing.map((item: string) => {
                    const icon = item === 'ndvi' ? '🌿' : item === 'soil' ? '🏔️' : '⛰️';
                    const label = item === 'ndvi' ? 'NDVI' : item === 'soil' ? 'Soil' : 'Relief';
                    return `<div style="color: #9333ea; margin: 2px 0;">${icon} ${label}</div>`;
                }).join('');

                missingHtml = `
                    <div style="
                        background: #faf5ff; 
                        border: 2px solid #9333ea; 
                        border-radius: 6px; 
                        padding: 8px; 
                        margin: 8px 0;
                    ">
                        <div style="
                            color: #9333ea; 
                            font-weight: bold; 
                            margin-bottom: 4px;
                            font-size: 13px;
                        ">⚠️ MISSING DATA:</div>
                        ${missingItems}
                        <div style="
                            color: #7c3aed; 
                            font-size: 11px; 
                            margin-top: 4px;
                            font-style: italic;
                        ">Using fallback defaults</div>
                    </div>
                `;
            }

            const content = `
                <div style="font-family: 'Inter', sans-serif; min-width: 200px;">
                    <div style="
                        font-weight: bold; 
                        font-size: 14px; 
                        margin-bottom: 8px;
                        color: #1f2937;
                        border-bottom: 2px solid #e5e7eb;
                        padding-bottom: 4px;
                    ">
                        📍 Cell ${props.id}
                    </div>
                    ${missingHtml}
                    <div style="margin-top: 8px;">
                        <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                            <span style="color: #6b7280;">OTU Index:</span>
                            <strong style="color: ${hasMissing ? '#9333ea' : '#059669'};">
                                ${props.q_otu?.toFixed(3) ?? 'N/A'}
                            </strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                            <span style="color: #6b7280;">NDVI:</span>
                            <span style="color: ${missing?.includes('ndvi') ? '#9333ea' : '#374151'};">
                                ${props.q_vi?.toFixed(3) ?? 'N/A'}
                            </span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                            <span style="color: #6b7280;">Soil (Si):</span>
                            <span style="color: ${missing?.includes('soil') ? '#9333ea' : '#374151'};">
                                ${props.q_si?.toFixed(3) ?? 'N/A'}
                            </span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                            <span style="color: #6b7280;">Soil (Bi):</span>
                            <span style="color: ${missing?.includes('soil') ? '#9333ea' : '#374151'};">
                                ${props.q_bi?.toFixed(3) ?? 'N/A'}
                            </span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin: 4px 0;">
                            <span style="color: #6b7280;">Relief:</span>
                            <span style="color: ${missing?.includes('relief') ? '#9333ea' : '#374151'};">
                                ${props.q_relief?.toFixed(3) ?? 'N/A'}
                            </span>
                        </div>
                    </div>
                </div>
            `;
            layer.bindPopup(content, { maxWidth: 300 });
        }
    };

    return <GeoJSON data={grid as any} style={style} onEachFeature={onEachFeature} />;
});


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
        <MapContainer
            center={props.center}
            zoom={8}
            style={{ height: '100%', width: '100%', background: 'transparent' }}
            zoomControl={false}
            attributionControl={false}
        >
            <CursorTracker onMove={props.onCursorMove} />
            <ZoomTracker onZoomChange={props.onZoomChange} />
            <MapFitter primaryEllipse={props.primaryEllipse} fragmentEllipse={props.fragmentEllipse} />
            <TileLayer url={getTileUrl()} maxZoom={19} />

            {/* Hybrid Overlay: Labels & Borders from Dark Theme */}
            {props.baseLayer === 'satellite' && (
                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/dark_only_labels/{z}/{x}/{y}{r}.png"
                    zIndex={10}
                    opacity={0.8}
                />
            )}

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
                <OTULayer grid={props.otuGrid} />
            )}

            {/* Render Ellipse Boundaries from Backend */}
            {props.boundaries && props.boundaries.features && (
                <GeoJSON
                    data={props.boundaries as any}
                    style={(feature) => {
                        const isPrimary = feature?.properties?.type === 'primary';
                        return {
                            color: isPrimary ? '#ef4444' : '#f59e0b',
                            fillColor: isPrimary ? '#ef4444' : '#f59e0b',
                            fillOpacity: 0.15,
                            weight: 3
                        };
                    }}
                    onEachFeature={(feature, layer) => {
                        if (feature.properties?.name) {
                            layer.bindPopup(`<strong>${feature.properties.name}</strong>`);
                        }
                    }}
                />
            )}

            {props.activeLayers.points && props.impactPoints && (
                <ImpactPointsLayer points={props.impactPoints} />
            )}

            {/* Preview Trajectory */}
            {props.previewTrajectory && props.previewTrajectory.length > 0 && (
                <>
                    <Polyline
                        positions={props.previewTrajectory.map(p => [p.lat, p.lon])}
                        pathOptions={{ color: '#ffffff', weight: 2, opacity: 0.8, dashArray: '5, 10' }}
                    />
                    <CircleMarker
                        center={[
                            props.previewTrajectory[props.previewTrajectory.length - 1].lat,
                            props.previewTrajectory[props.previewTrajectory.length - 1].lon
                        ]}
                        radius={4}
                        pathOptions={{ color: '#ffffff', fillColor: '#ffffff', fillOpacity: 0.8 }}
                    >
                        <Popup>Nominal Impact Point</Popup>
                    </CircleMarker>
                </>
            )}
        </MapContainer>
    );
};

export default LeafletMap;
