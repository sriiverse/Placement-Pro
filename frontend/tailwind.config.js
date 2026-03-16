/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#030712', // Very dark blue/black
        surface: '#080e1e',    // Slightly lighter dark
        panel: 'rgba(8, 14, 30, 0.7)',
        neon: {
          cyan: '#00f3ff',
          blue: '#3b82f6',
          purple: '#b537f2',
          pink: '#f12c8a'
        },
        primary: {
          DEFAULT: '#00f3ff',
          foreground: '#000000'
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace', 'ui-monospace'],
        sans: ['"Inter"', 'sans-serif'],
      },
      animation: {
        'scanline': 'scanline 8s linear infinite',
        'pulse-fast': 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 8s linear infinite',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' }
        },
        pulseGlow: {
          '0%': { opacity: '0.8', filter: 'brightness(1) drop-shadow(0 0 5px rgba(0, 243, 255, 0.5))' },
          '100%': { opacity: '1', filter: 'brightness(1.2) drop-shadow(0 0 15px rgba(0, 243, 255, 0.8))' }
        }
      }
    },
  },
  plugins: [],
}
