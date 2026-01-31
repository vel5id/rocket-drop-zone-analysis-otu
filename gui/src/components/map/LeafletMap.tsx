import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import React, { useEffect } from 'react';
import { CircleMarker, GeoJSON, LayerGroup, MapContainer, Polygon, Polyline, Popup, TileLayer, useMap, useMapEvents } from 'react-leaflet';
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

    // Binding popups
    const onEachFeature = (feature: any, layer: any) => {
        if (feature.properties) {
            const missing = feature.properties.missing_data;
            const missingHtml = (missing && missing.length > 0)
                ? `<div style="color: #9333ea; font-weight: bold;">MISSING: ${missing.join(', ')}</div>`
                : '';

            const content = `
                <div style="font-family: monospace;">
                    <strong>Grid:</strong> ${feature.properties.id}<br/>
                    ${missingHtml}
                    <strong>OTU:</strong> ${feature.properties.q_otu?.toFixed(3) ?? 'N/A'}<br/>
                    <strong>NDVI:</strong> ${feature.properties.q_vi?.toFixed(3) ?? 'N/A'}<br/>
                    <strong>Relief:</strong> ${feature.properties.q_relief?.toFixed(3) ?? 'N/A'}
                </div>
            `;
            layer.bindPopup(content);
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

            {props.activeLayers.fragments && props.fragmentEllipse && (
                <Polygon
                    positions={generateEllipsePoints(props.fragmentEllipse)}
                    pathOptions={{ color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 0.15, weight: 2 }}
                >
                    <Popup>Fragment Ellipse (3σ)</Popup>
                </Polygon>
            )}

            {props.activeLayers.primary && props.primaryEllipse && (
                <Polygon
                    positions={generateEllipsePoints(props.primaryEllipse)}
                    pathOptions={{ color: '#ef4444', fillColor: '#ef4444', fillOpacity: 0.15, weight: 2 }}
                >
                    <Popup>Primary Ellipse (3σ)</Popup>
                </Polygon>
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
