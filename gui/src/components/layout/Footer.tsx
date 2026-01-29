import React from 'react';
import { Crosshair } from 'lucide-react';

interface FooterProps {
    cursorCoords: { lat: number; lng: number };
    mapZoom: number;
}

const Footer: React.FC<FooterProps> = ({ cursorCoords, mapZoom }) => {
    return (
        <footer style={{ position: 'fixed', bottom: '28px', left: '50%', transform: 'translateX(-50%)', zIndex: 50 }}
            className="glass-panel rounded-full px-6 py-3 flex items-center gap-6 text-xs uppercase font-mono tracking-wider">
            <div className="coord-group flex items-center gap-2">
                <Crosshair size={14} className="text-[#06b6d4]" />
                <span className="text-[#64748b]">LAT:</span>
                <span className="coord-value">{cursorCoords.lat.toFixed(5)}</span>
            </div>
            <div className="w-px h-4 bg-[rgba(255,255,255,0.15)]"></div>
            <div className="coord-group flex items-center gap-2">
                <Crosshair size={14} className="text-[#06b6d4]" />
                <span className="text-[#64748b]">LON:</span>
                <span className="coord-value">{cursorCoords.lng.toFixed(5)}</span>
            </div>
            <div className="w-px h-4 bg-[rgba(255,255,255,0.15)]"></div>
            <div className="flex items-center gap-2">
                <span className="text-[#64748b]">ZOOM:</span>
                <span className="coord-value">{String(mapZoom).padStart(2, '0')}X</span>
            </div>
        </footer>
    );
};

export default Footer;
