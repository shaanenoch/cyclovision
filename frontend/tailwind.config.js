/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#060b17',
          900: '#0a1226',
          850: '#0f1b38',
          800: '#14254c',
          750: '#193060',
          700: '#1e3b75',
          600: '#2c53a3',
        },
        cyan: {
          glow: '#22d3ee',
          bright: '#06b6d4',
          dark: '#0891b2',
        },
        cyclone: {
          low: '#38bdf8',       // Low Pressure
          dep: '#34d399',       // Depression
          deep: '#facc15',      // Deep Depression
          storm: '#fb923c',     // Cyclonic Storm
          severe: '#f97316',    // Severe Cyclonic Storm
          vsevere: '#ef4444',   // Very Severe
          esevere: '#dc2626',   // Extremely Severe
          super: '#b91c1c',     // Super Cyclone
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
      },
      boxShadow: {
        'glow-cyan': '0 0 20px -5px rgba(6, 182, 212, 0.3)',
        'glow-blue': '0 0 20px -5px rgba(37, 99, 235, 0.3)',
        'glow-red': '0 0 20px -5px rgba(239, 68, 68, 0.4)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 12s linear infinite',
      }
    },
  },
  plugins: [],
}
