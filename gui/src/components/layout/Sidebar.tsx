import { ChevronRight, Grid, Leaf, MapPin, Play, Rocket, Settings, Wind } from 'lucide-react';
import React, { useState } from 'react';
import { SimulationConfig } from '../../types';
import { TechButton, TechInput, TechSelect, TechSlider, TechToggle } from '../common/TechUI';

interface SidebarProps {
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;
    simConfig: SimulationConfig;
    setSimConfig: (config: SimulationConfig) => void;
    runSimulation: () => void;
    isSimulating: boolean;
    progress: number;
}

const Sidebar: React.FC<SidebarProps> = ({
    isOpen,
    setIsOpen,
    simConfig,
    setSimConfig,
    runSimulation,
    isSimulating,
    progress
}) => {
    const [activeTab, setActiveTab] = useState<'general' | 'launch' | 'separation' | 'rocket' | 'eco'>('general');

    // Zones configuration
    const ZONE_OPTIONS = [
        { value: "manual", label: "Manual (Monte Carlo)" },
        { value: "yu24_15", label: "Ю-24 (Karaganda) - Zone 15" },
        { value: "yu24_25", label: "Ю-24 (Karaganda) - Zone 25" },
    ];

    const isManual = !simConfig.zone_id || simConfig.zone_id === "manual";

    // Auto-configure when zone changes
    // Auto-configure when zone changes
    React.useEffect(() => {
        if (simConfig.zone_id === "yu24_15" || simConfig.zone_id === "yu24_25") {
            // Zone Yu-24 (Karaganda Region) configuration
            // Source: Cadastral data & Neuro-search
            // Azimuth: ~65 deg (Official vector for Yu-24)
            // Distance: ~300-400km (Proton Stage 1 Drop Zone)

            // Bounding Boxes for reference:
            // Zone 15: NW 47°25', 66°35' - SE 47°15', 66°55'
            // Zone 25: NW 47°28', 66°00' - SE 47°00', 66°45'

            setSimConfig({
                ...simConfig,
                launch_lat: 45.96459,   // Baikonur Cosmodrome Area
                launch_lon: 63.30524,
                azimuth: 65.0,          // Corrected from 45.0
                sep_altitude: 43000.0,
                sep_velocity: 1738.0,
                iterations: 1000,       // Higher precision for zones
                // Note: We deliberately do NOT override GPU or Hurricane mode here
                // to respect the user's manual toggles.
            });
        }
    }, [simConfig.zone_id]);

    const TabButton: React.FC<{ id: 'general' | 'launch' | 'separation' | 'rocket' | 'eco'; icon: any; label: string }> = ({ id, icon: Icon, label }) => (
        <button
            onClick={() => setActiveTab(id)}
            className={`flex flex-col items-center justify-center py-3 px-1 flex-1 border-b-[3px] transition-all ${activeTab === id
                ? 'border-[#06b6d4] text-[#06b6d4] bg-[rgba(6,182,212,0.05)]'
                : 'border-transparent text-[#94a3b8] hover:text-white hover:bg-[rgba(255,255,255,0.02)]'
                }`}
        >
            <Icon size={18} className="mb-1" />
            <span className="text-[10px] uppercase font-bold tracking-wider">{label}</span>
        </button>
    );

    return (
        <>
            <aside style={{ position: 'fixed', top: '110px', left: '40px', width: '380px', zIndex: 40 }}
                className={`transition-all duration-300 ${isOpen ? 'translate-x-0 opacity-100' : '-translate-x-[450px] opacity-0'}`}>
                <div className="glass-panel rounded-2xl border border-[rgba(255,255,255,0.1)] border-l-[3px] border-l-[#06b6d4] overflow-hidden flex flex-col max-h-[calc(100vh-140px)]">

                    {/* Header */}
                    <div className="px-5 py-4 bg-[rgba(0,0,0,0.3)] flex justify-center items-center border-b border-[rgba(255,255,255,0.05)] relative shrink-0">
                        <h2 className="text-[#06b6d4] text-lg font-bold uppercase tracking-wider flex items-center gap-3">
                            <Grid size={18} /> Configuration
                        </h2>
                        <div className="absolute right-5 text-[10px] text-[#475569] font-mono bg-[rgba(0,0,0,0.3)] px-2 py-1 rounded">SYS.02</div>
                    </div>

                    {/* Tabs */}
                    <div className="flex border-b border-[rgba(255,255,255,0.05)] bg-[rgba(0,0,0,0.2)] shrink-0">
                        <TabButton id="general" icon={Settings} label="General" />
                        <TabButton id="launch" icon={MapPin} label="Launch Site" />
                        <TabButton id="separation" icon={Wind} label="Separation" />
                        <TabButton id="rocket" icon={Rocket} label="Rocket" />
                        <TabButton id="eco" icon={Leaf} label="Ecology" />
                    </div>

                    {/* Content */}
                    <div className="p-5 overflow-y-auto custom-scrollbar flex-1 relative">

                        {/* GENERAL SETTINGS */}
                        <div className={activeTab === 'general' ? 'block' : 'hidden'}>
                            <TechSelect
                                label="Analysis Type / Zone"
                                value={simConfig.zone_id || "manual"}
                                onChange={(val) => setSimConfig({ ...simConfig, zone_id: val })}
                                options={ZONE_OPTIONS}
                            />

                            <div>
                                <TechSlider
                                    label="Iterations"
                                    value={simConfig.iterations}
                                    onChange={(val) => setSimConfig({ ...simConfig, iterations: val })}
                                    min={100}
                                    max={10000}
                                    step={100}
                                />

                                {/* Date Selection for Scientific Reproducibility */}
                                <div className="p-4 bg-[rgba(255,255,255,0.02)] rounded-lg border border-[rgba(255,255,255,0.05)] mb-4">
                                    <h3 className="text-[10px] text-[#475569] uppercase tracking-[0.2em] mb-4 font-bold">Date Configuration</h3>
                                    <div className="space-y-3">
                                        <TechInput
                                            label="Target Date (Imagery)"
                                            value={simConfig.target_date}
                                            onChange={(val: string) => setSimConfig({ ...simConfig, target_date: val })}
                                            type="date"
                                        />
                                        <div className="grid grid-cols-2 gap-3">
                                            <TechInput
                                                label="Start Date"
                                                value={simConfig.start_date || ""}
                                                onChange={(val: string) => setSimConfig({ ...simConfig, start_date: val })}
                                                type="date"
                                            />
                                            <TechInput
                                                label="End Date"
                                                value={simConfig.end_date || ""}
                                                onChange={(val: string) => setSimConfig({ ...simConfig, end_date: val })}
                                                type="date"
                                            />
                                        </div>
                                    </div>
                                    <div className="mt-3 text-[10px] text-[#475569]">
                                        Date ranges enable scientific reproducibility and versioning of analysis results.
                                    </div>
                                </div>
                            </div>

                            <div className="mt-4 pt-4 border-t border-[rgba(255,255,255,0.05)]">
                                <TechToggle
                                    label="GPU Acceleration"
                                    checked={simConfig.use_gpu}
                                    onChange={() => setSimConfig({ ...simConfig, use_gpu: !simConfig.use_gpu })}
                                />
                                <div className="mt-4 pt-4 border-t border-[rgba(255,255,255,0.05)]">
                                    <TechToggle
                                        label="Hurricane Mode (High Entropy)"
                                        checked={simConfig.hurricane_mode || false}
                                        onChange={() => setSimConfig({ ...simConfig, hurricane_mode: !simConfig.hurricane_mode })}
                                    />
                                    <div className="text-[9px] text-amber-500/70 mt-1 uppercase tracking-wider font-bold">
                                        ⚠ Simulations High Variance Events
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* LAUNCH SITE */}
                        <div className={activeTab === 'launch' ? 'block' : 'hidden'}>
                            <div className={!isManual ? "opacity-50 pointer-events-none filter grayscale" : ""}>
                                <div className="p-4 bg-[rgba(255,255,255,0.02)] rounded-lg border border-[rgba(255,255,255,0.05)] mb-4">
                                    <h3 className="text-[10px] text-[#475569] uppercase tracking-[0.2em] mb-4 font-bold">Launch Coordinates</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <TechInput
                                            label="Latitude"
                                            value={simConfig.launch_lat}
                                            onChange={(val: string) => setSimConfig({ ...simConfig, launch_lat: parseFloat(val) || 0 })}
                                            type="number"
                                        />
                                        <TechInput
                                            label="Longitude"
                                            value={simConfig.launch_lon}
                                            onChange={(val: string) => setSimConfig({ ...simConfig, launch_lon: parseFloat(val) || 0 })}
                                            type="number"
                                        />
                                    </div>
                                    <TechSlider
                                        label="Azimuth"
                                        value={simConfig.azimuth}
                                        onChange={(val: number) => setSimConfig({ ...simConfig, azimuth: val })}
                                        min={0}
                                        max={360}
                                        step={1}
                                        unit="°"
                                    />
                                </div>
                                {!isManual && (
                                    <div className="mt-4 p-3 bg-[rgba(245,158,11,0.1)] border border-amber-500/20 rounded text-amber-500 text-xs">
                                        ⚠ Disabled in Zone Selection mode.
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* SEPARATION CONDITIONS */}
                        <div className={activeTab === 'separation' ? 'block' : 'hidden'}>
                            <div className={!isManual ? "opacity-50 pointer-events-none filter grayscale" : ""}>
                                <div className="p-4 bg-[rgba(255,255,255,0.02)] rounded-lg border border-[rgba(255,255,255,0.05)]">
                                    <div className="grid grid-cols-1 gap-1">
                                        <TechInput
                                            label="Altitude (m)"
                                            value={simConfig.sep_altitude}
                                            onChange={(val: string) => setSimConfig({ ...simConfig, sep_altitude: parseFloat(val) || 0 })}
                                            type="number"
                                        />
                                        <TechInput
                                            label="Velocity (m/s)"
                                            value={simConfig.sep_velocity}
                                            onChange={(val: string) => setSimConfig({ ...simConfig, sep_velocity: parseFloat(val) || 0 })}
                                            type="number"
                                        />
                                        <TechInput
                                            label="F.P. Angle (°)"
                                            value={simConfig.sep_fp_angle}
                                            onChange={(val: string) => setSimConfig({ ...simConfig, sep_fp_angle: parseFloat(val) || 0 })}
                                            type="number"
                                        />
                                        <TechInput
                                            label="Rel. Azimuth (°)"
                                            value={simConfig.sep_azimuth}
                                            onChange={(val: string) => setSimConfig({ ...simConfig, sep_azimuth: parseFloat(val) || 0 })}
                                            type="number"
                                        />
                                    </div>
                                </div>
                                {!isManual && (
                                    <div className="mt-4 p-3 bg-[rgba(245,158,11,0.1)] border border-amber-500/20 rounded text-amber-500 text-xs">
                                        ⚠ Disabled in Zone Selection mode.
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* ROCKET CHARACTERISTICS */}
                        <div className={activeTab === 'rocket' ? 'block' : 'hidden'}>
                            <div className={!isManual ? "opacity-50 pointer-events-none filter grayscale" : ""}>
                                <div className="p-4 bg-[rgba(255,255,255,0.02)] rounded-lg border border-[rgba(255,255,255,0.05)]">
                                    <TechInput
                                        label="Stage Dry Mass (kg)"
                                        value={simConfig.rocket_dry_mass || 30600.0}
                                        onChange={(val: string) => setSimConfig({ ...simConfig, rocket_dry_mass: parseFloat(val) || 0 })}
                                        type="number"
                                    />
                                    <TechInput
                                        label="Reference Area (m²)"
                                        value={simConfig.rocket_ref_area || 43.0}
                                        onChange={(val: string) => setSimConfig({ ...simConfig, rocket_ref_area: parseFloat(val) || 0 })}
                                        type="number"
                                    />
                                </div>
                                <div className="mt-4 text-[10px] text-[#475569]">
                                    Default values: Proton-M Stage 1 (30,600 kg, 43.0 m²).
                                    These parameters affect the ballistic coefficient and drag calculation during re-entry.
                                </div>
                            </div>
                        </div>

                        {/* ECOLOGY */}
                        <div className={activeTab === 'eco' ? 'block' : 'hidden'}>
                            <div className="p-4 bg-[rgba(255,255,255,0.02)] rounded-lg border border-[rgba(255,255,255,0.05)]">
                                <div className="text-xs text-[#94a3b8] mb-3">
                                    Configure environmental constraints for OTU (Optical-Thermal-Urban) index calculation.
                                </div>
                            </div>

                            <div className="space-y-4">
                                <TechSlider
                                    label="Cloud Cover Threshold (%)"
                                    value={simConfig.cloud_threshold ?? 30}
                                    onChange={(val) => setSimConfig({ ...simConfig, cloud_threshold: val })}
                                    min={0}
                                    max={100}
                                    step={5}
                                    unit="%"
                                />
                                <div className="text-[10px] text-[#475569] px-1">
                                    Stricter thresholds (&lt; 20%) provide cleaner data but may reduce available scenes.
                                    Standard: 30%.
                                </div>
                            </div>

                            <div className="mt-4 pt-4 border-t border-[rgba(255,255,255,0.05)]">
                                <TechButton icon={Leaf} disabled>
                                    OTU Index Auto-Calibrated
                                </TechButton>
                                <div className="text-[10px] text-[#475569] mt-2 text-center text-opacity-50">
                                    Calculated during simulation based on target date: {simConfig.target_date}
                                </div>
                            </div>
                            <div className="mt-4 pt-4 border-t border-[rgba(255,255,255,0.05)]">
                                <div className="text-[10px] text-[#475569]">
                                    <div className="flex justify-between mb-1">
                                        <span>NDVI Layer:</span>
                                        <span className="text-[#10b981]">Active</span>
                                    </div>
                                    <div className="flex justify-between mb-1">
                                        <span>Slope Analysis:</span>
                                        <span className="text-[#10b981]">Enabled</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Biodiversity Index:</span>
                                        <span className="text-[#10b981]">Calculated</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>



                    {/* Footer Action */}
                    <div className="p-5 border-t border-[rgba(255,255,255,0.05)] bg-[rgba(0,0,0,0.2)] shrink-0">
                        <TechButton primary onClick={runSimulation} disabled={isSimulating} icon={Play}>
                            {isSimulating ? `Processing ${progress}%` : (isManual ? 'Initiate Simulation' : 'Calculate Zones')}
                        </TechButton>
                    </div>
                </div>
            </aside >

            {/* Sidebar Toggle */}
            {
                !isOpen && (
                    <button
                        onClick={() => setIsOpen(true)}
                        style={{ position: 'fixed', top: '110px', left: '20px', zIndex: 40 }}
                        className="panel-toggle p-4 glass-panel border-r-[3px] border-r-[#06b6d4] text-[#06b6d4] rounded-r-xl hover:bg-[rgba(6,182,212,0.1)]"
                    >
                        <ChevronRight size={20} />
                    </button>
                )
            }
        </>
    );
};

export default Sidebar;
