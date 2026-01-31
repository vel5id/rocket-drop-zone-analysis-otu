import { Globe, Moon, Rocket, Settings } from 'lucide-react';
import React from 'react';

interface HeaderProps {
    isSimulating: boolean;
    simDone: boolean;
    progress: number;
    progressMessage: string;
    isDemoMode: boolean;
    baseLayer: 'satellite' | 'dark' | 'terrain' | 'streets';
    setBaseLayer: (layer: 'satellite' | 'dark' | 'terrain' | 'streets') => void;
}

const Header: React.FC<HeaderProps> = ({
    isSimulating,
    simDone,
    progress,
    progressMessage,
    isDemoMode,
    baseLayer,
    setBaseLayer
}) => {
    return (
        <header style={{ position: 'fixed', top: '28px', left: '50%', transform: 'translateX(-50%)', width: '92%', maxWidth: '1000px', height: '60px', zIndex: 50 }}
            className="glass-panel rounded-full flex items-center justify-between px-8">
            <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#06b6d4] to-[#0891b2] flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.4)]">
                    <Rocket className="text-white rotate-45" size={22} />
                </div>
                <div>
                    <h1 className="text-white font-bold tracking-tight text-xl leading-none uppercase text-header-title">
                        Orbital <span className="text-[#06b6d4]">Command</span>
                    </h1>
                    <div className="text-[11px] text-[#64748b] tracking-[0.2em] uppercase font-mono mt-0.5">Mission Control v2.0</div>
                </div>
            </div>

            <div className="flex items-center gap-5">
                {/* Status Badge */}
                <div className="px-4 py-2 rounded-full border border-[rgba(255,255,255,0.1)] text-xs font-mono uppercase bg-[rgba(0,0,0,0.3)] flex items-center gap-3">
                    <div className={`w-2.5 h-2.5 rounded-full ${simDone ? 'bg-green-500 status-ready' : isSimulating ? 'bg-amber-500 status-computing' : 'bg-slate-500'}`}></div>
                    <span className="text-[#94a3b8]">{isSimulating ? progressMessage : simDone ? 'READY' : 'IDLE'}</span>
                    {isSimulating && <span className="text-[#06b6d4] font-bold">{progress}%</span>}
                </div>

                {/* Demo Mode Badge */}
                {isDemoMode && (
                    <div className="px-3 py-1 rounded-full border border-amber-500/30 text-xs font-mono uppercase bg-amber-500/10 flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-amber-500"></div>
                        <span className="text-amber-300">DEMO</span>
                    </div>
                )}

                <div className="h-8 w-px bg-[rgba(255,255,255,0.1)]"></div>

                {/* Layer Buttons */}
                <div className="flex items-center gap-1">
                    <button onClick={() => setBaseLayer('satellite')} className={`p-2.5 rounded-lg transition-all ${baseLayer === 'satellite' ? 'text-[#06b6d4] bg-[rgba(6,182,212,0.15)]' : 'text-[#64748b] hover:text-white hover:bg-[rgba(255,255,255,0.05)]'}`} title="Satellite">
                        <Globe size={18} />
                    </button>
                    <button onClick={() => setBaseLayer('dark')} className={`p-2.5 rounded-lg transition-all ${baseLayer === 'dark' ? 'text-[#06b6d4] bg-[rgba(6,182,212,0.15)]' : 'text-[#64748b] hover:text-white hover:bg-[rgba(255,255,255,0.05)]'}`} title="Dark">
                        <Moon size={18} />
                    </button>
                    <button className="p-2.5 rounded-lg text-[#64748b] hover:text-white hover:bg-[rgba(255,255,255,0.05)] transition-all" title="Settings">
                        <Settings size={18} />
                    </button>
                </div>
            </div>
        </header>
    );
};

export default Header;
