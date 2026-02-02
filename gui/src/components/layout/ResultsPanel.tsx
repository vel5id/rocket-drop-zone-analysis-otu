import { Activity, Calendar, ChevronDown, Code, Database, FileText, Layers, Minimize, Target, Zap } from 'lucide-react';
import React from 'react';
import { ActiveLayers, UIStats } from '../../types';
import ExportButton from '../common/ExportButton';
import { StatReadout, TechButton, TechHeader } from '../common/TechUI';

interface ResultsPanelProps {
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;
    simDone: boolean;
    stats: UIStats | null;
    activeLayers: ActiveLayers;
    toggleLayer: (layer: keyof ActiveLayers) => void;
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({
    isOpen,
    setIsOpen,
    simDone,
    stats,
    activeLayers,
    toggleLayer
}) => {
    return (
        <>
            <aside style={{ position: 'fixed', top: '110px', right: '40px', width: '400px', zIndex: 40 }}
                className={`transition-all duration-300 ${isOpen ? 'translate-x-0 opacity-100' : 'translate-x-[460px] opacity-0'}`}>
                <div className="glass-panel rounded-2xl border border-[rgba(255,255,255,0.1)] border-r-[3px] border-r-[#ef4444]">
                    {/* Panel Header */}
                    <div className="px-5 py-4 bg-[rgba(0,0,0,0.3)] flex justify-center items-center border-b border-[rgba(255,255,255,0.05)] rounded-t-2xl relative">
                        <h2 className="text-[#ef4444] text-lg font-bold uppercase tracking-wider flex items-center gap-3">
                            <Activity size={18} /> Telemetry
                        </h2>
                        <button onClick={() => setIsOpen(false)} className="absolute right-5 text-[#64748b] hover:text-white p-1 hover:bg-[rgba(255,255,255,0.1)] rounded transition-all">
                            <Minimize size={16} />
                        </button>
                    </div>
                    {/* Panel Content */}
                    <div className="p-5 max-h-[calc(100vh-220px)] overflow-y-auto">
                        {simDone && stats ? (
                            <div className="space-y-6">
                                <TechHeader title="Mission Statistics" icon={Zap} />
                                <div className="grid grid-cols-2 gap-3">
                                    <StatReadout label="Impact Points" value={stats.impactPoints} />
                                    <StatReadout label="Range (3σ)" value={stats.semiMajorAxis} unit="km" />
                                    <StatReadout label="Mean OTU" value={stats.avgOtu.toFixed(2)} color="#10b981" />
                                    <StatReadout label="Sim Time" value="3.2" unit="sec" />
                                </div>

                                <TechHeader title="Dispersion Ellipses" icon={Target} />
                                <div className="bg-[rgba(0,0,0,0.3)] border border-[rgba(255,255,255,0.05)] rounded-xl p-4">
                                    <table className="w-full text-sm font-mono">
                                        <thead className="text-[#64748b] border-b border-[rgba(255,255,255,0.08)]">
                                            <tr>
                                                <th className="text-left py-2 font-medium">Zone</th>
                                                <th className="text-right py-2 font-medium">Axes (km)</th>
                                                <th className="text-right py-2 font-medium">Angle</th>
                                            </tr>
                                        </thead>
                                        <tbody className="text-white">
                                            <tr className="border-b border-[rgba(255,255,255,0.03)]">
                                                <td className="py-3 text-[#ef4444] font-bold">PRIMARY</td>
                                                <td className="text-right">{stats.primaryEllipse.a.toFixed(1)} × {stats.primaryEllipse.b.toFixed(1)}</td>
                                                <td className="text-right">{stats.primaryEllipse.angle.toFixed(1)}°</td>
                                            </tr>
                                            <tr>
                                                <td className="py-3 text-[#f59e0b] font-bold">FRAGMENTS</td>
                                                <td className="text-right">{stats.fragmentEllipse.a.toFixed(1)} × {stats.fragmentEllipse.b.toFixed(1)}</td>
                                                <td className="text-right">{stats.fragmentEllipse.angle.toFixed(1)}°</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>

                                {/* Scientific Reproducibility Section */}
                                <div className="pt-4 border-t border-[rgba(255,255,255,0.05)]">
                                    <TechHeader title="Scientific Reproducibility" icon={Database} />
                                    <div className="bg-[rgba(0,0,0,0.3)] border border-[rgba(255,255,255,0.05)] rounded-xl p-4 mb-4">
                                        <div className="space-y-2 text-xs font-mono">
                                            <div className="flex justify-between">
                                                <span className="text-[#64748b]">Analysis ID:</span>
                                                <span className="text-white">SIM_{Date.now().toString(36).toUpperCase()}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-[#64748b]">Date Range:</span>
                                                <span className="text-white">2024-01-01 to 2024-12-31</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-[#64748b]">Config Hash:</span>
                                                <span className="text-[#10b981]">a1b2c3d4</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-[#64748b]">Timestamp:</span>
                                                <span className="text-white">{new Date().toISOString().split('T')[0]} {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-3">
                                        <ExportButton
                                            jobId={stats.jobId}
                                            date="2024-09-09" // TODO: Pass from config
                                            label="Full Report"
                                        />
                                        <TechButton icon={FileText} onClick={() => alert('Exporting configuration...')}>
                                            Config Only
                                        </TechButton>
                                        <TechButton icon={Code} onClick={() => alert('Exporting raw data...')}>
                                            Raw Data
                                        </TechButton>
                                        <TechButton icon={Calendar} onClick={() => alert('Exporting time series...')}>
                                            Time Series
                                        </TechButton>
                                    </div>
                                    <div className="mt-3 text-[10px] text-[#475569] text-center">
                                        Export for peer review, archival, or further analysis
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="text-center py-16 relative">
                                <Activity size={56} className="mx-auto mb-5 text-[#475569] empty-state-icon" />
                                <div className="font-mono text-sm uppercase text-[#64748b] mb-2">Awaiting Data Stream</div>
                                <div className="text-xs text-[#475569]">Run a simulation to view results</div>
                                <div className="absolute inset-0 scan-effect pointer-events-none overflow-hidden"></div>
                            </div>
                        )}

                        {/* Visibility Layers - always available */}
                        <div className="mt-6">
                            <TechHeader title="Visibility Layers" icon={Layers} />
                            <div className="space-y-2">
                                {/* Simulation-dependent layers - only shown when simDone && stats */}
                                {simDone && stats && [
                                    { id: 'primary', label: 'Primary Ellipse', color: '#ef4444' },
                                    { id: 'fragments', label: 'Fragment Field', color: '#f59e0b' },
                                    { id: 'points', label: 'Impact Points', color: '#06b6d4' },
                                    { id: 'otu', label: 'OTU Heatmap', color: '#10b981' },
                                ].map((layer) => (
                                    <button
                                        key={layer.id}
                                        onClick={() => toggleLayer(layer.id as keyof ActiveLayers)}
                                        className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all ${activeLayers[layer.id as keyof ActiveLayers] ? 'bg-[rgba(255,255,255,0.05)] border-[rgba(255,255,255,0.15)]' : 'bg-transparent border-transparent opacity-60 hover:opacity-100'}`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: layer.color, boxShadow: `0 0 8px ${layer.color}` }}></div>
                                            <span className="text-sm font-medium text-[#94a3b8]">{layer.label}</span>
                                        </div>
                                        <div className={`w-10 h-5 rounded-full relative transition-all ${activeLayers[layer.id as keyof ActiveLayers] ? 'bg-[#06b6d4]' : 'bg-[rgba(255,255,255,0.1)]'}`}>
                                            <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow-md transition-all ${activeLayers[layer.id as keyof ActiveLayers] ? 'right-0.5' : 'left-0.5'}`}></div>
                                        </div>
                                    </button>
                                ))}

                                {/* Trajectory Preview - always available */}
                                {[
                                    { id: 'preview', label: 'Trajectory Preview', color: '#ffffff' },
                                ].map((layer) => (
                                    <button
                                        key={layer.id}
                                        onClick={() => toggleLayer(layer.id as keyof ActiveLayers)}
                                        className={`w-full flex items-center justify-between p-3 rounded-lg border transition-all ${activeLayers[layer.id as keyof ActiveLayers] ? 'bg-[rgba(255,255,255,0.05)] border-[rgba(255,255,255,0.15)]' : 'bg-transparent border-transparent opacity-60 hover:opacity-100'}`}
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: layer.color, boxShadow: `0 0 8px ${layer.color}` }}></div>
                                            <span className="text-sm font-medium text-[#94a3b8]">{layer.label}</span>
                                        </div>
                                        <div className={`w-10 h-5 rounded-full relative transition-all ${activeLayers[layer.id as keyof ActiveLayers] ? 'bg-[#06b6d4]' : 'bg-[rgba(255,255,255,0.1)]'}`}>
                                            <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow-md transition-all ${activeLayers[layer.id as keyof ActiveLayers] ? 'right-0.5' : 'left-0.5'}`}></div>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Results Toggle */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    style={{ position: 'fixed', top: '110px', right: '20px', zIndex: 40 }}
                    className="panel-toggle p-4 glass-panel border-l-[3px] border-l-[#ef4444] text-[#ef4444] rounded-l-xl hover:bg-[rgba(239,68,68,0.1)]"
                >
                    <ChevronDown className="rotate-90" size={20} />
                </button>
            )}
        </>
    );
};

export default ResultsPanel;
