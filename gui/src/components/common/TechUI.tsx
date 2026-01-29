import { ChevronDown } from 'lucide-react';
import React from 'react';

// ============================================
// UI COMPONENTS
// ============================================

export const TechHeader: React.FC<{ title: string; icon?: React.ElementType }> = ({ title, icon: Icon }) => (
    <div className="flex items-center gap-3 mb-5 text-[#06b6d4] uppercase tracking-wider text-sm font-bold border-b border-[rgba(6,182,212,0.3)] pb-3">
        {Icon && <Icon size={16} strokeWidth={2.5} />}
        <span className="text-header-title">{title}</span>
        <div className="flex-1" />
        <div className="flex gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-[#06b6d4]"></div>
            <div className="w-1.5 h-1.5 rounded-full bg-[#06b6d4] opacity-50"></div>
            <div className="w-1.5 h-1.5 rounded-full bg-[#06b6d4] opacity-25"></div>
        </div>
    </div>
);

export const TechButton: React.FC<{
    children: React.ReactNode;
    onClick?: () => void;
    primary?: boolean;
    icon?: React.ElementType;
    disabled?: boolean;
}> = ({ children, onClick, primary, icon: Icon, disabled }) => (
    <button
        onClick={onClick}
        disabled={disabled}
        className={`
      w-full py-4 px-5 rounded-lg flex items-center justify-center gap-3 font-bold text-sm uppercase tracking-wider transition-all relative overflow-hidden
      ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-[1.02] active:scale-[0.98]'}
      ${primary
                ? 'bg-gradient-to-r from-[rgba(6,182,212,0.15)] to-[rgba(6,182,212,0.05)] border-2 border-[#06b6d4] text-[#06b6d4] hover:bg-[#06b6d4] hover:text-white btn-primary-glow'
                : 'bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.15)] text-[#94a3b8] hover:bg-[rgba(255,255,255,0.08)] hover:text-white hover:border-[rgba(255,255,255,0.3)]'}
    `}
    >
        {Icon && <Icon size={18} className={primary && !disabled ? "animate-pulse" : ""} />}
        <span>{children}</span>
        {primary && !disabled && (
            <div className="absolute inset-0 shimmer-effect pointer-events-none"></div>
        )}
    </button>
);

export const StatReadout: React.FC<{ label: string; value: string | number; unit?: string; color?: string }> = ({ label, value, unit, color = "#06b6d4" }) => (
    <div className="bg-[rgba(0,0,0,0.3)] p-4 rounded-lg border-l-3 border-[rgba(255,255,255,0.1)] hover:border-l-[#06b6d4] transition-all hover:bg-[rgba(0,0,0,0.4)] group" style={{ borderLeftWidth: '3px' }}>
        <div className="text-tech-label mb-2 group-hover:text-white transition-colors">{label}</div>
        <div className="font-mono text-2xl text-white flex items-baseline gap-2" style={{ textShadow: `0 0 15px ${color}50` }}>
            {value}
            {unit && <span className="text-xs font-semibold" style={{ color }}>{unit}</span>}
        </div>
    </div>
);

export const TechAccordion: React.FC<{ title: string; isOpen: boolean; onToggle: () => void; children: React.ReactNode }> = ({ title, isOpen, onToggle, children }) => (
    <div className="border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.02)] mb-3 rounded-lg overflow-hidden">
        <button
            onClick={onToggle}
            className={`accordion-header w-full flex items-center justify-between text-sm uppercase font-bold tracking-wider transition-all ${isOpen ? 'text-[#06b6d4] bg-[rgba(6,182,212,0.08)]' : 'text-[#94a3b8] hover:text-white hover:bg-[rgba(255,255,255,0.03)]'}`}
            style={{ padding: '14px 16px' }}
        >
            <span>{title}</span>
            <div className={`transition-transform duration-200 ${isOpen ? 'rotate-0' : '-rotate-90'}`}>
                <ChevronDown size={16} />
            </div>
        </button>
        <div className={`transition-all duration-300 ${isOpen ? 'max-h-[1200px] opacity-100' : 'max-h-0 opacity-0 overflow-hidden'}`}>
            <div className="accordion-content border-t border-[rgba(255,255,255,0.05)]" style={{ padding: '20px' }}>
                {children}
            </div>
        </div>
    </div>
);

// Enhanced Slider Component
export const TechSlider: React.FC<{
    label: string;
    value: number;
    onChange: (val: number) => void;
    min: number;
    max: number;
    step: number;
    unit?: string;
    disabled?: boolean;
}> = ({ label, value, onChange, min, max, step, unit, disabled }) => {
    const percentage = ((value - min) / (max - min)) * 100;

    return (
        <div className={`mb-6 ${disabled ? 'opacity-50 pointer-events-none' : ''}`}>
            <div className="flex justify-between items-center mb-3">
                <span className="text-tech-label">{label}</span>
                <div className="flex items-center gap-2">
                    <span className="text-tech-value text-lg">{value.toLocaleString()}</span>
                    {unit && <span className="text-xs text-[#475569]">{unit}</span>}
                </div>
            </div>
            <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={value}
                onChange={(e) => onChange(parseInt(e.target.value))}
                disabled={disabled}
                style={{ '--value-percent': `${percentage}%` } as React.CSSProperties}
            />
            <div className="flex justify-between text-[10px] text-[#475569] mt-2">
                <span>{min.toLocaleString()}</span>
                <span>{max.toLocaleString()}</span>
            </div>
        </div>
    );
};

// Toggle Switch Component
export const TechToggle: React.FC<{ label: string; checked: boolean; onChange: () => void }> = ({ label, checked, onChange }) => (
    <button
        onClick={onChange}
        className="w-full flex items-center justify-between p-3 bg-[rgba(255,255,255,0.02)] rounded-lg border border-[rgba(255,255,255,0.05)] hover:border-[rgba(255,255,255,0.15)] transition-all"
    >
        <span className="text-sm uppercase text-[#94a3b8] tracking-wide">{label}</span>
        <div className={`w-12 h-6 rounded-full relative transition-all ${checked ? 'bg-[#06b6d4]' : 'bg-[rgba(255,255,255,0.1)]'}`}>
            <div className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow-lg transition-all ${checked ? 'right-1' : 'left-1'}`}></div>
        </div>
    </button>
);
// Input Component
export const TechInput: React.FC<{
    label: string;
    value: string | number;
    onChange: (val: string) => void;
    type?: string;
    placeholder?: string;
    disabled?: boolean;
}> = ({ label, value, onChange, type = "text", placeholder, disabled }) => (
    <div className={`mb-6 ${disabled ? 'opacity-50 pointer-events-none' : ''}`}>
        <span className="text-tech-label block mb-3">{label}</span>
        <input
            type={type}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            disabled={disabled}
            placeholder={placeholder}
            className="w-full bg-[rgba(0,0,0,0.3)] border border-[rgba(255,255,255,0.1)] rounded-lg py-3 px-4 text-white font-mono text-sm focus:outline-none focus:border-[#06b6d4] transition-all disabled:cursor-not-allowed"
        />
    </div>
);

// Select Component
export const TechSelect: React.FC<{
    label: string;
    value: string;
    onChange: (val: string) => void;
    options: { value: string; label: string }[];
    disabled?: boolean;
}> = ({ label, value, onChange, options, disabled }) => (
    <div className={`mb-6 ${disabled ? 'opacity-50 pointer-events-none' : ''}`}>
        <span className="text-tech-label block mb-3">{label}</span>
        <div className="relative">
            <select
                value={value}
                onChange={(e) => onChange(e.target.value)}
                disabled={disabled}
                className="w-full appearance-none bg-[rgba(0,0,0,0.3)] border border-[rgba(255,255,255,0.1)] rounded-lg py-3 px-4 text-white font-mono text-sm focus:outline-none focus:border-[#06b6d4] transition-all disabled:cursor-not-allowed"
            >
                {options.map((opt) => (
                    <option key={opt.value} value={opt.value} className="bg-[#0f172a] text-white">
                        {opt.label}
                    </option>
                ))}
            </select>
            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-[#94a3b8]">
                <ChevronDown size={16} />
            </div>
        </div>
    </div>
);
