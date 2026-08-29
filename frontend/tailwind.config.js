/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          base: '#FFFFFF',
          surface: '#F8FAFC',
          tintBlue: '#EFF6FF',
          tintViolet: '#F5F3FF',
          tintAmber: '#FFFBEB',
          tintEmerald: '#ECFDF5',
          tintRose: '#FFF1F2',
        },
        primary: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
        accent: {
          violet: '#7C3AED',
          amber: '#F59E0B',
          red: '#EF4444',
          emerald: '#10B981',
          pink: '#EC4899',
          cyan: '#06B6D4',
        },
        govNavy: {
          50: '#f0f4f8',
          100: '#d9e2ec',
          500: '#134074',
          800: '#0B2545',
          900: '#081D35',
        },
        govSaffron: {
          50: '#fffaf0',
          500: '#DD6B20',
          600: '#C05621',
        },
        govGreen: {
          50: '#f0fff4',
          500: '#2F855A',
          600: '#276749',
        },
        govRed: {
          50: '#fff5f5',
          500: '#C53030',
          600: '#9B2C2C',
        },
      },
      borderRadius: {
        'card': '24px',
        'pill': '9999px',
        '2xl': '20px',
        '3xl': '28px',
      },
      boxShadow: {
        'tinted-blue': '0 12px 32px -8px rgba(37, 99, 235, 0.22)',
        'tinted-violet': '0 12px 32px -8px rgba(124, 58, 237, 0.22)',
        'tinted-emerald': '0 12px 32px -8px rgba(16, 185, 129, 0.22)',
        'tinted-amber': '0 12px 32px -8px rgba(245, 158, 11, 0.22)',
        'tinted-red': '0 12px 32px -8px rgba(239, 68, 68, 0.22)',
        'soft': '0 8px 24px -6px rgba(15, 23, 42, 0.07), 0 2px 6px -2px rgba(15, 23, 42, 0.04)',
        'soft-lg': '0 16px 40px -10px rgba(15, 23, 42, 0.10), 0 4px 12px -3px rgba(15, 23, 42, 0.05)',
        'clay': '0 20px 40px -15px rgba(0, 0, 0, 0.07), inset 0 1px 0 rgba(255, 255, 255, 0.8)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Space Grotesk', 'Sora', 'Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'float': 'float 4s ease-in-out infinite',
        'shimmer': 'shimmer 2.5s linear infinite',
        'pulse-subtle': 'pulseSubtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 8s linear infinite',
        'scan-line': 'scanLine 2.5s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.85', transform: 'scale(1.02)' },
        },
        scanLine: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
      },
    },
  },
  plugins: [],
}
