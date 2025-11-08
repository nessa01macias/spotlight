import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Blue-purple gradient palette (F2F7FF → 9D71E8)
        gradient: {
          50: '#F2F7FF',   // Page backgrounds, very light fills
          100: '#C9DCFF',  // Card backgrounds, light fills
          200: '#B2C9FF',  // Secondary interactive elements
          300: '#BE99FF',  // Accents, hover states
          400: '#9D71E8',  // Primary CTA, dark accents
        },
        // Neutral scale for text and UI chrome
        neutral: {
          50: '#FAFAFA',
          100: '#F4F4F5',
          200: '#E4E4E7',
          300: '#D4D4D8',
          400: '#A1A1AA',
          500: '#71717A',
          600: '#52525B',
          700: '#3F3F46',
          800: '#27272A',
          900: '#18181B',
        },
        // Semantic opportunity colors
        opportunity: {
          high: '#10B981',    // Green
          medium: '#F59E0B',  // Amber
          low: '#EF4444',     // Red
        },
        // Confidence colors
        confidence: {
          low: '#F59E0B',      // <0.6 - amber
          medium: '#10B981',   // 0.6-0.75 - green
          high: '#059669',     // 0.75-0.9 - emerald
          veryHigh: '#047857', // >0.9 - dark emerald
        },
      },
      fontFamily: {
        sans: ['system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif'],
        mono: ['"SF Mono"', 'Monaco', '"Cascadia Code"', '"Courier New"', 'monospace'],
      },
      borderRadius: {
        'sm': '0.25rem',   // 4px
        'md': '0.5rem',    // 8px
        'lg': '0.75rem',   // 12px
        'xl': '1rem',      // 16px
        '2xl': '1.5rem',   // 24px
      },
      boxShadow: {
        'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        'inner': 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
      },
      transitionDuration: {
        '120': '120ms',
        '150': '150ms',
        '180': '180ms',
      },
    },
  },
  plugins: [],
};

export default config;
