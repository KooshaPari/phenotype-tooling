/**
 * Phenotype Design System — Keycap Palette Tokens
 * @phenotype/design v1.0.0
 *
 * Typed programmatic access to design tokens.
 * For CSS usage, import the CSS files directly.
 *
 * Usage:
 *   import { keycap, glass, typography } from '@phenotype/design'
 */

export const keycap = {
  accent: '#7ebab5',
  accentHover: '#95ccc8',
  accentActive: '#6aa8a3',
  accentDim: '#569691',
  accentContrast: '#4a9c97',
  slate: '#353a40',

  dark: {
    bg: '#090a0c',
    bgAlt: '#0e1014',
    bgSoft: '#14171b',
    bgElv: '#1a1e24',
    text1: '#f6f5f5',
    text2: '#a8adb5',
    text3: '#6b7280',
    divider: '#1f2329',
    gutter: '#0c0d0f',
    codeBlockBg: '#060708',
  },

  light: {
    bg: '#f8f9fa',
    bgAlt: '#f0f1f3',
    bgSoft: '#e8eaed',
    bgElv: '#ffffff',
    text1: '#1a1c1e',
    text2: '#4a4f57',
    text3: '#6b7280',
    divider: '#d4d7dc',
    gutter: '#e8eaed',
    codeBlockBg: '#f0f1f3',
  },
} as const

export type KeycapTokens = typeof keycap

/** Glass recipe numeric values — mirror glass.css --glass-* vars */
export const glass = {
  neo: {
    blur: 16,
    saturate: 1.1,
    fillOpacityLight: 0.72,
    fillOpacityDark: 0.72,
    borderOpacityLight: 0.45,
    borderOpacityDark: 0.08,
    specularOpacityLight: 0.70,
    specularOpacityDark: 0.12,
    borderRadius: 16,
  },
  liquid: {
    blur: 20,
    saturate: 1.4,
    fillOpacityLight: 0.60,
    fillOpacityDark: 0.60,
    borderOpacityLight: 0.55,
    borderOpacityDark: 0.10,
    specularOpacityLight: 0.70,
    specularOpacityDark: 0.12,
    borderRadius: 14,
    /** Top-edge specular gradient stops in px */
    specularGradientHeight: '8%',
  },
  mica: {
    blur: 40,
    saturate: 1.8,
    fillOpacityLight: 0.82,
    fillOpacityDark: 0.85,
    borderOpacityLight: undefined, // uses --kc-divider
    borderOpacityDark: undefined,  // uses --kc-divider
    borderRadius: 8,
    accentTintOpacity: 0.06,
  },
  nav: {
    blur: 14,
    saturate: 1.2,
    fillOpacity: 0.88,
  },
  badge: {
    blur: 4,
    fillOpacityDark: 0.50,
    fillOpacityLight: 0.70,
  },
} as const

export type GlassTokens = typeof glass

/** Typography stacks */
export const typography = {
  fontDisplay: "'Bricolage Grotesque', 'Montserrat', sans-serif",
  fontBase: "'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  fontMono: "'JetBrains Mono', ui-monospace, 'Cascadia Code', monospace",

  scale: {
    display: { size: 96, weight: 700, letterSpacing: '-0.045em', lineHeight: 0.95, opsz: 96 },
    h1:      { size: 56, weight: 700, letterSpacing: '-0.035em', lineHeight: 1.0,  opsz: 56 },
    h2:      { size: 36, weight: 800, letterSpacing: '-0.03em',  lineHeight: 1.1 },
    h3:      { size: 22, weight: 600, letterSpacing: '-0.015em', lineHeight: 1.25 },
    body:    { size: 16, weight: 400, letterSpacing: '0',        lineHeight: 1.7 },
    small:   { size: 13, weight: 500, letterSpacing: '0.01em',   lineHeight: 1.5 },
    mono:    { size: 13, weight: 500, letterSpacing: '0',        lineHeight: 1.6 },
    eyebrow: { size: 11, weight: 600, letterSpacing: '0.18em',   lineHeight: 1.4 },
  },
} as const

export type TypographyTokens = typeof typography
