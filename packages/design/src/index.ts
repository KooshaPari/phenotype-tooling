/**
 * @phenotype/design — Phenotype Design System
 *
 * Main entry point. Re-exports all typed tokens.
 * For CSS, import individual CSS files via package exports.
 */

export { keycap, glass, typography } from './tokens.js'
export type { KeycapTokens, GlassTokens, TypographyTokens } from './tokens.js'
export { vitepressConfig, vitepressMarkdownTheme } from './vitepress.js'
