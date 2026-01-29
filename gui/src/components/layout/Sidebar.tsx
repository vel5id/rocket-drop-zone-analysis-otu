import React from 'react';
import { Grid, Play, Target, Leaf, ChevronRight } from 'lucide-react';
import { TechAccordion, TechSlider, TechToggle, TechButton } from '../common/TechUI';
import { SimulationConfig } from '../../types';

interface SidebarProps {
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;
    activeSection: string | null;
    setActiveSection: (section: string | null) => void;
    simConfig: SimulationConfig;
    setSimConfig: (config: SimulationConfig) => void;
    runSimulation: () => void;
    isSimulating: boolean;
    progress: number;
}

const Sidebar: React.FC<SidebarProps> = ({
    isOpen,
    setIsOpen,
    activeSection,
    setActiveSection,
    simConfig,
    setSimConfig,
    runSimulation,
    isSimulating,
    progress
}) => {
    return (
        <>
            <aside style={{ position: 'fixed', top: '110px', left: '40px', width: '340px', zIndex: 40 }}
                className={`transition-all duration-300 ${isOpen ? 'translate-x-0 opacity-100' : '-translate-x-[400px] opacity-0'}`}>
                <div className="glass-panel rounded-2xl border border-[rgba(255,255,255,0.1)] border-l-[3px] border-l-[#06b6d4]">
                    {/* Panel Header */}
                    <div className="px-5 py-4 bg-[rgba(0,0,0,0.3)] flex justify-center items-center border-b border-[rgba(255,255,255,0.05)] rounded-t-2xl relative">
                        <h2 className="text-[#06b6d4] text-lg font-bold uppercase tracking-wider flex items-center gap-3">
                            <Grid size={18} /> Configuration
                        </h2>
                        <div className="absolute right-5 text-[10px] text-[#475569] font-mono bg-[rgba(0,0,0,0.3)] px-2 py-1 rounded">SYS.01</div>
                    </div>
                    {/* Panel Content */}
                    <div className="p-5 max-h-[calc(100vh-220px)] overflow-y-auto">
                        <TechAccordion title="Monte Carlo Simulation" isOpen={activeSection === 'monte'} onToggle={() => setActiveSection(activeSection === 'monte' ? null : 'monte')}>
                            <TechSlider
                                label="Iterations"
                                value={simConfig.iterations}
                                onChange={(val) => setSimConfig({ ...simConfig, iterations: val })}
                                min={100}
                                max={10000}
                                step={100}
                            />
                            <TechToggle
                                label="GPU Acceleration"
                                checked={simConfig.use_gpu}
                                onChange={() => setSimConfig({ ...simConfig, use_gpu: !simConfig.use_gpu })}
                            />
                            <div className="mt-5">
                                <TechButton primary onClick={runSimulation} disabled={isSimulating} icon={Play}>
                                    {isSimulating ? `Processing ${progress}%` : 'Initiate Simulation'}
                                </TechButton>
                            </div>
                        </TechAccordion>

                        <TechAccordion title="Ecological Assessment" isOpen={activeSection === 'otu'} onToggle={() => setActiveSection(activeSection === 'otu' ? null : 'otu')}>
                            <div className="text-sm text-[#64748b] mb-4 flex items-center gap-2">
                                <Target size={14} /> Date: <span className="text-[#06b6d4] font-mono">2024-09-09</span>
                            </div>
                            <TechButton icon={Leaf}>Calculate OTU Index</TechButton>
                        </TechAccordion>
                    </div>
                </div>
            </aside>

            {/* Sidebar Toggle */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    style={{ position: 'fixed', top: '110px', left: '20px', zIndex: 40 }}
                    className="panel-toggle p-4 glass-panel border-r-[3px] border-r-[#06b6d4] text-[#06b6d4] rounded-r-xl hover:bg-[rgba(6,182,212,0.1)]"
                >
                    <ChevronRight size={20} />
                </button>
            )}
        </>
    );
};

export default Sidebar;
