import React, { useEffect, useMemo } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { CircleMarker, LayerGroup, MapContainer, Polygon, Popup, TileLayer, useMap, useMapEvents } from 'react-leaflet';
import { ActiveLayers, EllipseData, GeoJSONFeatureCollection, GeoJSONPoint, ImpactPointProperties, OTUCellProperties, GeoJSONPolygon, MapViewProps } from '../../types';
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
            {points.features.map((f, i) => (
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
                        Range: {f.properties.downrange_km.toFixed(1)}km
                    </Popup>
                </CircleMarker>
            ))}
        </LayerGroup>
    );
});

// Optimization: Memoize OTU grid rendering
const OTULayer = React.memo(({ grid }: { grid: GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties> }) => {
    return (
        <LayerGroup>
            {grid.features.map((f, i) => (
                <Polygon
                    key={f.properties.grid_id || i}
                    positions={f.geometry.coordinates[0].map((c: any) => [c[1], c[0]])}
                    pathOptions={{
                        color: getOTUColor(f.properties.q_otu),
                        fillColor: getOTUColor(f.properties.q_otu),
                        fillOpacity: 0.6,
                        weight: 1
                    }}
                >
                    <Popup>
                        <div style={{ fontFamily: 'monospace' }}>
                            Grid: {f.properties.grid_id}<br />
                            OTU: {f.properties.q_otu.toFixed(3)}
                        </div>
                    </Popup>
                </Polygon>
            ))}
        </LayerGroup>
    );
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
        </MapContainer>
    );
};

export default LeafletMap;
