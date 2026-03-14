/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Syne"', 'sans-serif'],
        body: ['"DM Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        ink: {
          DEFAULT: '#0D0D0F',
          soft: '#1A1A1F',
          muted: '#2C2C35',
        },
        slate: {
          edge: '#3D3D4A',
          mid: '#6B6B7E',
          soft: '#9898A8',
          ghost: '#C4C4D0',
          pale: '#EBEBF0',
          white: '#F7F7FA',
        },
        signal: {
          blue: '#4F7FFF',
          'blue-dim': '#1A3A8F',
          green: '#2ECC8A',
          'green-dim': '#0D4A30',
          amber: '#F5A623',
          'amber-dim': '#5C3A00',
          red: '#FF4F6A',
          'red-dim': '#5C0A1A',
          purple: '#A855F7',
          'purple-dim': '#3B1A6E',
        },
      },
      animation: {
        'fade-up': 'fadeUp 0.4s ease forwards',
        'fade-in': 'fadeIn 0.3s ease forwards',
        'slide-in': 'slideIn 0.35s ease forwards',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
        'shimmer': 'shimmer 1.5s ease-in-out infinite',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-12px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
