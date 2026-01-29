export interface ActiveLayers {
    primary: boolean;
    fragments: boolean;
    points: boolean;
    otu: boolean;
    preview: boolean;
    ndvi: boolean;
    slope: boolean;
}

export interface EllipseData {
    center_lat: number;
    center_lon: number;
    semi_major_km: number;
    semi_minor_km: number;
    angle_deg: number;
}

export interface ImpactPointProperties {
    id: number;
    is_fragment: boolean;
    downrange_km: number;
    crossrange_km?: number;
    velocity_m_s?: number;
}

export interface OTUCellProperties {
    grid_id: string;
    q_ndvi: number;
    q_si: number;
    q_bi: number;
    q_relief: number;
    q_otu: number;
    q_fire: number;
}

export interface GeoJSONGeometry {
    type: 'Point' | 'Polygon';
    coordinates: any;
}

export interface GeoJSONFeature<G extends GeoJSONGeometry, P> {
    type: 'Feature';
    geometry: G;
    properties: P;
}

export interface GeoJSONFeatureCollection<G extends GeoJSONGeometry, P> {
    type: 'FeatureCollection';
    features: GeoJSONFeature<G, P>[];
}

export type GeoJSONPoint = GeoJSONGeometry & { type: 'Point'; coordinates: [number, number] };
export type GeoJSONPolygon = GeoJSONGeometry & { type: 'Polygon'; coordinates: [number, number][][] };

// Stats used in the UI
export interface UIStats {
    impactPoints: number;
    range: string;
    semiMajorAxis: number;
    avgOtu: number;
    primaryEllipse: { a: number; b: number; angle: number };
    fragmentEllipse: { a: number; b: number; angle: number };
}

// Stats from the API
export interface APISimulationStats {
    iterations: number;
    simulation_time_s: number;
    primary_impacts: number;
    fragment_impacts: number;
    grid_cells: number;
}

export interface SimulationConfig {
    iterations: number;
    use_gpu: boolean;
    launch_lat: number;
    launch_lon: number;
    azimuth: number;
    target_date: string;
    start_date?: string;
    end_date?: string;
    sep_altitude: number;
    sep_velocity: number;
    sep_fp_angle: number;
    sep_azimuth: number;
    zone_id?: string;
    rocket_dry_mass?: number;
    rocket_ref_area?: number;
    hurricane_mode?: boolean;
    cloud_threshold?: number;
}

export interface SimulationStatus {
    job_id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    progress: number;
    message?: string;
}

export interface TrajectoryPoint {
    lat: number;
    lon: number;
    alt: number;
    velocity: number;
    time: number;
}

export interface TrajectoryResponse {
    path: TrajectoryPoint[];
    impact_point: TrajectoryPoint;
}

export interface SimulationResult {
    job_id: string;
    status: string;
    progress: number;
    primary_ellipse?: EllipseData;
    fragment_ellipse?: EllipseData;
    impact_points?: GeoJSONFeatureCollection<GeoJSONPoint, ImpactPointProperties>;
    otu_grid?: GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties>;
    stats?: APISimulationStats;
    error?: string;
}

// Map Component Props
export interface MapViewProps {
    center: [number, number];
    launchPoint: [number, number];
    primaryEllipse?: EllipseData;
    fragmentEllipse?: EllipseData;
    impactPoints?: GeoJSONFeatureCollection<GeoJSONPoint, ImpactPointProperties>;
    otuGrid?: GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties>;
    // New prop for trajectory preview
    previewTrajectory?: TrajectoryPoint[];
    activeLayers: ActiveLayers;
    onZoomChange: (zoom: number) => void;
    onCursorMove: (lat: number, lng: number) => void;
    baseLayer: 'satellite' | 'dark' | 'terrain' | 'streets';
}
