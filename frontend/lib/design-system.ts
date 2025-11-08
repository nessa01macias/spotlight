/**
 * Spotlight Design System
 * Lovably-inspired clean aesthetic with blue-purple gradient palette
 * Focus: Trust, explainability, generous spacing
 */

// ============================================
// COLOR PALETTE
// ============================================

/**
 * Blue-purple gradient (F2F7FF → 9D71E8)
 * Progressive gradient for backgrounds, interactive elements, and CTAs
 */
export const gradient = {
  50: '#F2F7FF',   // Page backgrounds, very light fills
  100: '#C9DCFF',  // Card backgrounds, light fills
  200: '#B2C9FF',  // Secondary interactive elements
  300: '#BE99FF',  // Accents, hover states
  400: '#9D71E8',  // Primary CTA, dark accents
} as const;

/**
 * Neutral scale for text and UI chrome
 * High contrast for WCAG AA compliance
 */
export const neutral = {
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
} as const;

/**
 * Semantic opportunity colors
 * For scoring, predictions, and status indicators
 */
export const opportunity = {
  high: '#10B981',    // Green - high opportunity
  medium: '#F59E0B',  // Amber - medium opportunity
  low: '#EF4444',     // Red - low opportunity
} as const;

/**
 * Confidence colors
 * Color-coded by confidence threshold
 */
export const confidence = {
  low: '#F59E0B',      // <0.6 - amber
  medium: '#10B981',   // 0.6-0.75 - green
  high: '#059669',     // 0.75-0.9 - emerald
  veryHigh: '#047857', // >0.9 - dark emerald
} as const;

/**
 * Get confidence color based on score
 */
export function getConfidenceColor(score: number): string {
  if (score < 0.6) return confidence.low;
  if (score < 0.75) return confidence.medium;
  if (score < 0.9) return confidence.high;
  return confidence.veryHigh;
}

// ============================================
// TYPOGRAPHY
// ============================================

/**
 * Font families
 * System fonts for performance and platform consistency
 */
export const fonts = {
  sans: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  mono: '"SF Mono", Monaco, "Cascadia Code", "Courier New", monospace',
} as const;

/**
 * Typography scale
 * Generous sizing for readability
 */
export const typography = {
  // Display text (hero sections)
  hero: {
    fontSize: '3rem',        // 48px
    fontWeight: '600',       // semibold
    lineHeight: '1.1',
    letterSpacing: '-0.02em',
  },
  // Page titles
  title: {
    fontSize: '2rem',        // 32px
    fontWeight: '600',
    lineHeight: '1.2',
    letterSpacing: '-0.01em',
  },
  // Section headings
  heading: {
    fontSize: '1.5rem',      // 24px
    fontWeight: '600',
    lineHeight: '1.3',
  },
  // Subheadings
  subheading: {
    fontSize: '1.125rem',    // 18px
    fontWeight: '500',
    lineHeight: '1.4',
  },
  // Body text
  body: {
    fontSize: '1rem',        // 16px
    fontWeight: '400',
    lineHeight: '1.5',
  },
  // Small text
  small: {
    fontSize: '0.875rem',    // 14px
    fontWeight: '400',
    lineHeight: '1.5',
  },
  // Tiny text (labels, captions)
  tiny: {
    fontSize: '0.75rem',     // 12px
    fontWeight: '400',
    lineHeight: '1.5',
  },
} as const;

// ============================================
// SPACING
// ============================================

/**
 * Spacing scale
 * Generous spacing for clean, breathable layouts
 */
export const spacing = {
  xs: '0.25rem',    // 4px
  sm: '0.5rem',     // 8px
  md: '1rem',       // 16px
  lg: '1.5rem',     // 24px
  xl: '2rem',       // 32px
  '2xl': '3rem',    // 48px
  '3xl': '4rem',    // 64px
  '4xl': '6rem',    // 96px
} as const;

/**
 * Layout-specific spacing
 */
export const layout = {
  page: 'px-8 py-12',           // Page padding
  section: 'space-y-8',          // Section spacing
  card: 'p-6',                   // Card padding
  cardLarge: 'p-8',              // Large card padding
  stack: 'space-y-4',            // Vertical stack spacing
  stackTight: 'space-y-2',       // Tight vertical spacing
  inline: 'space-x-4',           // Horizontal inline spacing
} as const;

// ============================================
// BORDER RADIUS
// ============================================

/**
 * Border radius scale
 * Reduced for enterprise vibes (not fully rounded)
 */
export const radius = {
  sm: '0.25rem',    // 4px
  md: '0.5rem',     // 8px  - Cards
  lg: '0.75rem',    // 12px - Buttons
  xl: '1rem',       // 16px - Large elements
  '2xl': '1.5rem',  // 24px - Hero sections
  full: '9999px',   // Fully rounded (chips, badges)
} as const;

// ============================================
// SHADOWS
// ============================================

/**
 * Shadow scale
 * Subtle shadows, not dramatic
 */
export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
} as const;

// ============================================
// MOTION
// ============================================

/**
 * Animation timing
 * Fast, smooth transitions
 */
export const motion = {
  duration: {
    fast: '120ms',
    normal: '150ms',
    slow: '180ms',
  },
  easing: {
    default: 'ease-out',
    in: 'ease-in',
    out: 'ease-out',
    inOut: 'ease-in-out',
  },
} as const;

/**
 * Common transition classes
 */
export const transitions = {
  default: 'transition-all duration-150 ease-out',
  colors: 'transition-colors duration-150 ease-out',
  transform: 'transition-transform duration-150 ease-out',
  opacity: 'transition-opacity duration-150 ease-out',
} as const;

// ============================================
// COMPONENT STYLES
// ============================================

/**
 * Button variants
 */
export const button = {
  base: 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-150 ease-out focus:outline-none focus:ring-2 focus:ring-offset-2',
  sizes: {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  },
  variants: {
    primary: 'text-white shadow-sm hover:shadow-md',
    secondary: 'border shadow-sm hover:shadow-md',
    tertiary: 'hover:underline',
  },
} as const;

/**
 * Input styles
 */
export const input = {
  base: 'w-full rounded-lg border transition-colors duration-150 ease-out focus:outline-none focus:ring-2',
  sizes: {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-base',
    lg: 'px-6 py-4 text-lg',
  },
} as const;

/**
 * Card styles
 */
export const card = {
  base: 'rounded-lg transition-shadow duration-150 ease-out',
  variants: {
    default: 'bg-white border shadow-sm hover:shadow-md',
    elevated: 'bg-white shadow-md hover:shadow-lg',
    flat: 'bg-white border',
  },
} as const;

// ============================================
// UTILITIES
// ============================================

/**
 * Format currency for Finnish locale
 * Uses thin space for thousands separator
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('fi-FI', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount).replace(/\s/g, '\u202F'); // Replace regular space with thin space
}

/**
 * Format area in square meters
 */
export function formatArea(sqm: number): string {
  return `${Math.round(sqm)} m²`;
}

/**
 * Format rent per square meter per month
 */
export function formatRent(eurPerSqmPerMonth: number): string {
  return `${Math.round(eurPerSqmPerMonth)} €/m²/month`;
}

/**
 * Get score color based on value (0-100)
 */
export function getScoreColor(score: number): string {
  if (score >= 80) return opportunity.high;
  if (score >= 60) return opportunity.medium;
  return opportunity.low;
}

/**
 * Format confidence as percentage with color
 */
export function formatConfidence(confidence: number): {
  value: string;
  color: string;
} {
  return {
    value: `${Math.round(confidence * 100)}%`,
    color: getConfidenceColor(confidence),
  };
}

/**
 * Calculate confidence band percentage
 */
export function getConfidenceBand(confidence: number): number {
  // Lower confidence = wider band
  if (confidence < 0.6) return 30;
  if (confidence < 0.75) return 20;
  if (confidence < 0.9) return 15;
  return 10;
}

/**
 * Grain texture background (subtle)
 * Use on page backgrounds only, never on maps
 */
export const grainTexture = {
  background: `
    radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.8) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.8) 0%, transparent 50%),
    url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.03'/%3E%3C/svg%3E")
  `,
  backgroundSize: '100% 100%, 100% 100%, 100px 100px',
} as const;
