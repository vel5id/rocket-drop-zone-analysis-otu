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
    id: string;                // ✅ Matches backend
    q_vi: number;              // ✅ NDVI (was q_ndvi)
    q_si: number;              // ✅ Soil strength
    q_bi: number;              // ✅ Soil quality
    q_relief: number;          // ✅ Relief factor
    q_otu: number;             // ✅ OTU index
    is_processed: boolean;     // ✅ Processing status
    missing_data: string[];    // ✅ Array of missing data types
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
    jobId: string; // ✅ Added for export
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

export interface ZonePreviewResponse {
    zone_id?: string;
    primary_polygon?: any; // GeoJSONFeature
    fragment_polygon?: any; // GeoJSONFeature
    message?: string;
}

export interface SimulationResult {
    job_id: string;
    status: string;
    progress: number;
    primary_ellipse?: EllipseData;
    fragment_ellipse?: EllipseData;
    impact_points?: GeoJSONFeatureCollection<GeoJSONPoint, ImpactPointProperties>;
    otu_grid?: GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties>;
    boundaries?: GeoJSONFeatureCollection<GeoJSONPolygon, { type: string; name: string }>;
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
    boundaries?: GeoJSONFeatureCollection<GeoJSONPolygon, { type: string; name: string }>;
    // New prop for trajectory preview
    previewTrajectory?: TrajectoryPoint[];
    activeLayers: ActiveLayers;
    onZoomChange: (zoom: number) => void;
    onCursorMove: (lat: number, lng: number) => void;
    baseLayer: 'satellite' | 'dark' | 'terrain' | 'streets';
}
