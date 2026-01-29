import React, { useEffect, useState } from 'react';
import { runSimulation as apiRunSimulation, checkHealth, pollSimulation } from './api';
import { runMockSimulation } from './mockSimulation';
import { calculateDistance } from './utils';
import { GlobalStyles } from './components/common/GlobalStyles';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import ResultsPanel from './components/layout/ResultsPanel';
import Footer from './components/layout/Footer';
import MapView from './components/map/MapView';
import {
    ActiveLayers,
    EllipseData,
    GeoJSONFeatureCollection,
    GeoJSONPoint,
    GeoJSONPolygon,
    ImpactPointProperties,
    OTUCellProperties,
    SimulationConfig,
    UIStats
} from './types';

const LAUNCH_LAT = 45.72341;
const LAUNCH_LON = 63.32275;

export default function App() {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [resultsOpen, setResultsOpen] = useState(true);
    const [activeSection, setActiveSection] = useState<string | null>('monte');

    const [isSimulating, setIsSimulating] = useState(false);
    const [progress, setProgress] = useState(0);
    const [progressMessage, setProgressMessage] = useState('Initializing...');
    const [simDone, setSimDone] = useState(false);

    const [cursorCoords, setCursorCoords] = useState({ lat: LAUNCH_LAT, lng: LAUNCH_LON });
    const [mapZoom, setMapZoom] = useState(8);

    const [baseLayer, setBaseLayer] = useState<'satellite' | 'dark' | 'terrain' | 'streets'>('dark');
    const [activeLayers, setActiveLayers] = useState<ActiveLayers>({
        primary: true, fragments: true, points: false, otu: false, ndvi: false, slope: false,
    });

    const [simConfig, setSimConfig] = useState<SimulationConfig>({
        iterations: 100,
        use_gpu: true,
        launch_lat: LAUNCH_LAT,
        launch_lon: LAUNCH_LON,
        azimuth: 45.0
    });

    const [stats, setStats] = useState<UIStats | null>(null);
    const [primaryEllipse, setPrimaryEllipse] = useState<EllipseData | undefined>();
    const [fragmentEllipse, setFragmentEllipse] = useState<EllipseData | undefined>();
    const [impactPoints, setImpactPoints] = useState<GeoJSONFeatureCollection<GeoJSONPoint, ImpactPointProperties> | undefined>();
    const [otuGrid, setOtuGrid] = useState<GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties> | undefined>();

    const [backendAvailable, setBackendAvailable] = useState<boolean | null>(null);
    const [isDemoMode, setIsDemoMode] = useState(false);

    // Check backend health on mount
    useEffect(() => {
        checkHealth().then(available => {
            setBackendAvailable(available);
            setIsDemoMode(!available);
        });
    }, []);

    const toggleLayer = (layer: keyof ActiveLayers) => setActiveLayers(prev => ({ ...prev, [layer]: !prev[layer] }));

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
                const mockResult = await runMockSimulation(simConfig.iterations, simConfig.launch_lat, simConfig.launch_lon);

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
            const { job_id } = await apiRunSimulation(simConfig);

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
                    ? calculateDistance(simConfig.launch_lat, simConfig.launch_lon, result.primary_ellipse.center_lat, result.primary_ellipse.center_lon)
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
                        launchPoint={[simConfig.launch_lat, simConfig.launch_lon]}
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

                <Header
                    isSimulating={isSimulating}
                    simDone={simDone}
                    progress={progress}
                    isDemoMode={isDemoMode}
                    baseLayer={baseLayer}
                    setBaseLayer={setBaseLayer}
                />

                <Sidebar
                    isOpen={sidebarOpen}
                    setIsOpen={setSidebarOpen}
                    activeSection={activeSection}
                    setActiveSection={setActiveSection}
                    simConfig={simConfig}
                    setSimConfig={setSimConfig}
                    runSimulation={runSimulation}
                    isSimulating={isSimulating}
                    progress={progress}
                />

                <ResultsPanel
                    isOpen={resultsOpen}
                    setIsOpen={setResultsOpen}
                    simDone={simDone}
                    stats={stats}
                    activeLayers={activeLayers}
                    toggleLayer={toggleLayer}
                />

                <Footer
                    cursorCoords={cursorCoords}
                    mapZoom={mapZoom}
                />

                {/* Corner Decorations */}
                <div className="fixed pointer-events-none opacity-30" style={{ top: '20px', left: '20px', width: '80px', height: '80px', borderLeft: '2px solid #06b6d4', borderTop: '2px solid #06b6d4', borderRadius: '16px 0 0 0' }}></div>
                <div className="fixed pointer-events-none opacity-30" style={{ bottom: '20px', right: '20px', width: '80px', height: '80px', borderRight: '2px solid #06b6d4', borderBottom: '2px solid #06b6d4', borderRadius: '0 0 16px 0' }}></div>
            </div>
        </>
    );
}
