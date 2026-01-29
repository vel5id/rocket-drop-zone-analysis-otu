import React from 'react';

export const GlobalStyles = () => (
    <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;700&family=Rajdhani:wght@500;600;700&display=swap');

    :root {
      --bg-space: #050a10;
      --bg-glass: rgba(13, 20, 30, 0.85);
      --bg-glass-heavy: rgba(13, 20, 30, 0.95);
      --text-bright: #ffffff;
      --text-dim: #94a3b8;
      --text-muted: #475569;
      --accent-cyan: #06b6d4;
      --accent-green: #10b981;
      --accent-red: #ef4444;
      --accent-amber: #f59e0b;
      --border-glass: rgba(255, 255, 255, 0.1);
      --font-main: 'Inter', sans-serif;
      --font-tech: 'Rajdhani', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-space);
      color: var(--text-bright);
      font-family: var(--font-main);
      overflow: hidden;
    }

    .glass-panel {
      background: var(--bg-glass);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--border-glass);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }

    /* Inputs, Buttons, Scrollbars */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.02); border-radius: 3px; }
    ::-webkit-scrollbar-thumb { background: rgba(6, 182, 212, 0.3); border-radius: 3px; }

    input[type="range"] {
      -webkit-appearance: none; width: 100%; height: 6px;
      background: linear-gradient(to right, var(--accent-cyan) 0%, var(--accent-cyan) var(--value-percent, 10%), rgba(255, 255, 255, 0.1) 100%);
      border-radius: 3px; outline: none; cursor: pointer; margin: 12px 0;
    }
    input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none; width: 20px; height: 20px; background: var(--bg-space);
      border: 3px solid var(--accent-cyan); border-radius: 50%; cursor: grab;
      box-shadow: 0 0 12px rgba(6, 182, 212, 0.5); transition: all 0.2s ease;
    }

    button { font-family: var(--font-tech); transition: all 0.2s ease; }
    button:active:not(:disabled) { transform: scale(0.98); }

    @keyframes subtle-pulse { 0%, 100% { box-shadow: 0 0 15px rgba(6, 182, 212, 0.3); } 50% { box-shadow: 0 0 25px rgba(6, 182, 212, 0.5); } }
    .btn-primary-glow { animation: subtle-pulse 2s infinite; }

    /* Typography & Utils */
    .text-tech-label { font-family: var(--font-tech); font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; color: var(--text-dim); }
    .text-tech-value { font-family: var(--font-mono); font-size: 14px; color: var(--accent-cyan); font-weight: 600; }
    .text-header-title { font-family: var(--font-tech); font-weight: 700; letter-spacing: 0.02em; }

    .bg-grid {
      background-size: 50px 50px;
      background-image: linear-gradient(to right, rgba(6, 182, 212, 0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(6, 182, 212, 0.05) 1px, transparent 1px);
    }

    /* Map Tooltip for SVG Fallback */
    .map-tooltip {
      position: absolute; background: rgba(13, 20, 30, 0.95); border: 1px solid var(--accent-cyan);
      color: #fff; padding: 8px 12px; border-radius: 6px; font-family: var(--font-mono); font-size: 12px;
      pointer-events: none; z-index: 100; box-shadow: 0 4px 12px rgba(0,0,0,0.5); transform: translate(-50%, -120%);
    }

    /* Leaflet overrides */
    .leaflet-container { background: transparent !important; }
    .leaflet-popup-content-wrapper { background: rgba(13, 20, 30, 0.95) !important; color: white !important; border: 1px solid var(--accent-cyan); }
    .leaflet-popup-tip { background: rgba(13, 20, 30, 0.95) !important; }
  `}</style>
);
