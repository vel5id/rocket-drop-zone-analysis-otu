import { EllipseData } from './types';

export function generateEllipsePoints(ellipse: EllipseData, numPoints: number = 64): [number, number][] {
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

export function getOTUColor(value: number): string {
    const clamped = Math.max(0, Math.min(1, value));
    if (clamped < 0.5) {
        const ratio = clamped * 2;
        return `rgb(248, ${Math.round(81 + 107 * ratio)}, ${Math.round(73 - 69 * ratio)})`;
    } else {
        const ratio = (clamped - 0.5) * 2;
        return `rgb(${Math.round(251 - 216 * ratio)}, ${Math.round(188 - 54 * ratio)}, ${Math.round(4 + 50 * ratio)})`;
    }
}

export function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
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
