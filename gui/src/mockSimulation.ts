import {
    EllipseData,
    GeoJSONFeatureCollection,
    GeoJSONPoint,
    GeoJSONPolygon,
    ImpactPointProperties,
    OTUCellProperties,
    UIStats
} from './types';
import { calculateDistance, calculateAverageOtu } from './utils';

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

export function runMockSimulation(iterations: number, launchLat: number, launchLon: number): Promise<{
    primaryEllipse: EllipseData;
    fragmentEllipse: EllipseData;
    impactPoints: GeoJSONFeatureCollection<GeoJSONPoint, ImpactPointProperties>;
    otuGrid: GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties>;
    stats: UIStats;
}> {
    return new Promise((resolve) => {
        setTimeout(() => {
            const centerLat = 48.0 + (Math.random() - 0.5) * 0.2;
            const centerLon = 66.5 + (Math.random() - 0.5) * 0.2;

            const primaryEllipse = generateMockEllipse(centerLat, centerLon, false);
            const fragmentEllipse = generateMockEllipse(centerLat, centerLon, true);
            const impactPoints = generateMockImpactPoints(Math.floor(iterations / 10));
            const otuGrid = generateMockOTUGrid();

            const rangeKm = calculateDistance(launchLat, launchLon, primaryEllipse.center_lat, primaryEllipse.center_lon);

            resolve({
                primaryEllipse,
                fragmentEllipse,
                impactPoints,
                otuGrid,
                stats: {
                    impactPoints: impactPoints.features.length,
                    range: `${rangeKm.toFixed(1)}`,
                    semiMajorAxis: primaryEllipse.semi_major_km,
                    avgOtu: calculateAverageOtu(otuGrid),
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
