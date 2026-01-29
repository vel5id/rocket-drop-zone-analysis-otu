/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                main: ['Inter', 'sans-serif'],
                tech: ['Rajdhani', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            colors: {
                space: '#050a10',
                'glass': 'rgba(13, 20, 30, 0.85)',
                'accent-cyan': '#06b6d4',
                'accent-green': '#10b981',
                'accent-red': '#ef4444',
                'accent-amber': '#f59e0b',
            },
        },
    },
    plugins: [],
}
