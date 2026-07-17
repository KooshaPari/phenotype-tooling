# Comprehensive UI Design Principles and Standards Reference

> A comprehensive reference for LLM-generated interfaces, compiled from authoritative sources including Nielsen's Usability Heuristics, WCAG Accessibility Guidelines, and established design systems.

---

## Table of Contents

1. [Core UI Principles](#core-ui-principles)
2. [Layout Standards](#layout-standards)
3. [Component Design](#component-design)
4. [Color & Typography](#color--typography)
5. [Accessibility Requirements](#accessibility-requirements)
6. [Quick Reference Summary](#quick-reference-summary)

---

## Core UI Principles

### 1. Visibility of System Status

**The design should always keep users informed about what is going on, through appropriate feedback within reasonable time.**

- Show progress indicators for async operations
- Display current state of any processing
- Use loading spinners, progress bars, or skeleton screens
- Provide confirmation messages after actions complete

### 2. Match Between System and Real World

**Use words, phrases, and concepts familiar to the user, rather than internal jargon. Follow real-world conventions.**

- Use familiar icons (envelope = email, gear = settings)
- Organize information in natural, logical order
- Match UI controls to corresponding objects (stovetop knobs match burner layout)
- Test terminology with actual users

### 3. User Control and Freedom

**Users need a clearly marked "emergency exit" to leave unwanted actions without extended process.**

- Provide undo/redo functionality
- Clear cancel buttons on all dialogs
- Breadcrumb navigation for hierarchical flows
- Back button behavior that matches expectations

### 4. Consistency and Standards

**Users should not wonder whether different words, situations, or actions mean the same thing.**

- Follow platform conventions (iOS vs Android patterns)
- Maintain consistent button styles, colors, and placement
- Use standard icons for common actions
- Apply Jakob's Law: users spend most time on OTHER products

### 5. Error Prevention

**Eliminate error-prone conditions, or check for them and present confirmation options.**

- Input constraints (limit character count, validate formats)
- Confirmation dialogs for destructive actions
- Auto-save draft content
- Constraint examples: guard rails on mountain roads

### 6. Recognition Rather Than Recall

**Minimize memory load by making elements, actions, and options visible.**

- Recent items/搜索 history
- Visible labels (don't hide them in tooltips only)
- Visual categories and groupings
- Progressive disclosure for complex forms

### 7. Flexibility and Efficiency of Use

**Allow users to tailor frequent actions; provide shortcuts for experts.**

- Keyboard shortcuts for power users
- Customizable dashboards
- Default settings that can be overridden
- Quick actions (right-click context menus)

### 8. Aesthetic and Minimalist Design

**Every extra unit of information competes with relevant information.**

- Remove unnecessary visual elements
- Focus on essential content
- Use white space strategically
- Prioritize content over decoration

### 9. Help Users Recognize and Recover from Errors

**Error messages should be in plain language, precisely indicate the problem, and suggest solutions.**

- No error codes visible to users
- Constructive, actionable messages
- Visual treatments that ensure visibility
- Example: "Wrong way" signs with clear direction

### 10. Help and Documentation

**System should not need explanation, but documentation should be available if needed.**

- Contextual help near complex features
- Searchable documentation
- Concise, task-focused instructions
- Concrete steps, not conceptual explanations

---

## Layout Standards

### Grid Systems

#### 8-Point Grid System (Industry Standard)

| Token | Value |
|-------|-------|
| `xxs` | 4px |
| `xs` | 8px |
| `sm` | 12px |
| `md` | 16px |
| `lg` | 24px |
| `xl` | 32px |
| `xxl` | 48px |
| `xxxl` | 64px |

**Rules:**
- All spacing divisible by 4 or 8
- Components align to grid
- Margins/padding use 4px baseline

#### Column Grid

| Breakpoint | Columns | Gutter | Max Width |
|------------|---------|--------|-----------|
| Mobile (<768px) | 4 | 16px | 100% |
| Tablet (768-1024px) | 8 | 24px | 720px |
| Desktop (1024-1440px) | 12 | 24px | 960px |
| Large (>1440px) | 12 | 32px | 1280px |

### Spacing Scale

**Base spacing unit: 4px**

```
4px → 8px → 12px → 16px → 24px → 32px → 48px → 64px → 96px
```

**Component Spacing Guidelines:**
- Button padding: 12px horizontal, 8px vertical
- Card padding: 16px or 24px
- Form field gap: 16px
- Section spacing: 48px or 64px

### Responsive Breakpoints

```
Mobile:      0 - 479px
Phablet:     480 - 767px
Tablet:      768 - 1023px
Desktop:     1024 - 1279px
Wide:        1280 - 1535px
Ultra-wide:  1536px+
```

### Alignment Principles

- **Vertical alignment**: Top, middle, bottom
- **Horizontal alignment**: Left, center, right
- **Text alignment**: Left (default for LTR languages)
- **Baseline alignment**: Align text on common baseline
- **Edge alignment**: Align to container edges, not arbitrary positions

---

## Component Design

### Buttons

#### Button Hierarchy

| Type | Use Case | Visual Weight |
|------|----------|---------------|
| Primary | Main action | High (solid fill) |
| Secondary | Alternative action | Medium (outlined) |
| Tertiary | Minor actions | Low (text only) |
| Destructive | Delete/remove | High (red) |

#### Button Metrics

- **Min touch target**: 44x44px (iOS), 48x48px (Android)
- **Padding**: 16px horizontal, 8px vertical
- **Border radius**: 4px (small), 8px (medium), 12px (large)
- **Icon buttons**: 40x40px minimum
- **Gap between buttons**: 8px or 12px

### Forms

#### Input Field Standards

| Element | Standard |
|---------|----------|
| Height | 40px (single line), variable (multiline) |
| Padding | 12px horizontal |
| Border radius | 4px |
| Label position | Above input (preferred) |
| Helper text | Below input, smaller font |
| Error state | Red border, error message below |

#### Form Layout

- Labels visible (not placeholder-only)
- Required fields marked with asterisk
- Group related fields together
- Logical tab order
- Error summary at top of form

### Navigation

#### Navigation Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| Tab bar | Primary navigation | Bottom nav (mobile) |
| Sidebar | Secondary navigation | Dashboard apps |
| Breadcrumb | Hierarchical navigation | E-commerce |
| Menu | Context-specific actions | Dropdown menus |

#### Navigation Sizing

- **Nav items**: 44px minimum height
- **Active state**: Visual indicator (background, border, icon)
- **Hover state**: Subtle background change
- **Spacing between items**: 4px or 8px

### Modals/Dialogs

#### Modal Standards

| Element | Standard |
|---------|----------|
| Max width | 560px (standard), 720px (large) |
| Padding | 24px |
| Border radius | 12px or 16px |
| Backdrop | Semi-transparent overlay (rgba(0,0,0,0.5)) |
| Close button | Top right, 44x44px hit area |
| Action buttons | Right-aligned at bottom |

#### Modal Behavior

- Focus trapped within modal
- ESC key closes modal
- Click outside closes (unless destructive)
- Scroll locked on body

### Cards

#### Card Metrics

| Element | Standard |
|---------|----------|
| Padding | 16px or 24px |
| Border radius | 8px or 12px |
| Shadow | Subtle elevation (0 2px 4px rgba(0,0,0,0.1)) |
| Gap between cards | 16px or 24px |

#### Card Structure

- Visual hierarchy: Title → Content → Actions
- Optional image/header area
- Consistent action placement

### Tables

#### Table Standards

| Element | Standard |
|---------|----------|
| Row height | 44px or 52px |
| Header height | 48px |
| Cell padding | 12px or 16px |
| Border | 1px solid, subtle |
| Alternating rows | Optional (subtle) |

#### Table Features

- Sortable column headers
- Sticky header on scroll
- Responsive: horizontal scroll or card transformation
- Row hover state
- Selection checkboxes

---

## Color & Typography

### Color Theory Basics

#### Color Roles

| Role | Purpose | Usage |
|------|---------|-------|
| Primary | Brand identity | Main actions, links, highlights |
| Secondary | Support brand | Secondary actions, accents |
| Neutral | Content | Body text, backgrounds |
| Success | Positive feedback | Confirmations, success states |
| Warning | Caution | Alerts, important notices |
| Error | Negative feedback | Errors, destructive actions |

#### Color Accessibility

**WCAG Contrast Ratios:**

| Level | Normal Text | Large Text | UI Components |
|-------|-------------|------------|----------------|
| AA (Minimum) | 4.5:1 | 3:1 | 3:1 |
| AAA (Enhanced) | 7:1 | 4.5:1 | 3:1 |

**Definitions:**
- Normal text: <18pt regular or <14pt bold
- Large text: >=18pt regular or >=14pt bold
- UI components: Buttons, inputs, icons

### Typography Scale

#### Type Scale (Major Third - 1.25)

| Level | Size | Line Height | Usage |
|-------|------|-------------|-------|
| Display | 48px | 1.2 | Hero headlines |
| H1 | 36px | 1.25 | Page titles |
| H2 | 30px | 1.3 | Section headings |
| H3 | 24px | 1.35 | Subsection headings |
| H4 | 20px | 1.4 | Card titles |
| Body Large | 18px | 1.5 | Lead paragraphs |
| Body | 16px | 1.5 | Body text |
| Body Small | 14px | 1.5 | Secondary text |
| Caption | 12px | 1.4 | Labels, captions |

#### Typeface Selection

- **Sans-serif**: Roboto, Inter, SF Pro, Segoe UI
- **Serif**: Merriweather, Georgia (limited use)
- **Monospace**: Roboto Mono, Fira Code (code blocks)

#### Readability Guidelines

- Body text: 16px minimum
- Line length: 45-75 characters (ideal: 65)
- Line height: 1.4-1.6 for body
- Paragraph spacing: 0.5-1em
- Letter spacing: -0.02em to 0.02em for body

---

## Accessibility Requirements

### WCAG 2.1 Quick Reference

#### Perceivable

| Criterion | Requirement |
|-----------|-------------|
| 1.1.1 | Non-text content has text alternative |
| 1.3.1 | Info and relationships programmatically determined |
| 1.4.1 | Color not sole means of conveying info |
| 1.4.3 | Contrast 4.5:1 (text), 3:1 (graphics) |
| 1.4.4 | Text resizable to 200% |
| 1.4.10 | Content reflows at 320px width |
| 1.4.11 | Non-text contrast 3:1 |

#### Operable

| Criterion | Requirement |
|-----------|-------------|
| 2.1.1 | All functionality keyboard accessible |
| 2.1.2 | No keyboard traps |
| 2.4.1 | Bypass blocks (skip links) |
| 2.4.2 | Page titled meaningfully |
| 2.4.3 | Focus order logical |
| 2.4.6 | Headings and labels descriptive |
| 2.4.7 | Focus visible |

#### Understandable

| Criterion | Requirement |
|-----------|-------------|
| 3.1.1 | Page language defined |
| 3.2.1 | No unexpected context changes |
| 3.2.2 | No unexpected form submissions |
| 3.3.1 | Error identification clear |
| 3.3.2 | Labels and instructions provided |

#### Robust

| Criterion | Requirement |
|-----------|-------------|
| 4.1.1 | Valid HTML |
| 4.1.2 | Name, role, value available |

### Focus States

- **Visible focus indicator**: 2px solid outline
- **Focus not obscured**: Minimum AA (entire indicator visible)
- **Focus appearance**: 2px minimum thickness, contrast 3:1
- **Focus trap**: Modal dialogs

### Target Sizes

| Level | Minimum Size |
|-------|--------------|
| AAA (Enhanced) | 44x44px |
| AA (Minimum) | 24x24px |

### Motion & Animation

- Respect `prefers-reduced-motion`
- No flashing content (>3 flashes/second)
- Pause, stop, hide controls for auto-playing content

---

## Quick Reference Summary

### Design Checklist

- [ ] Contrast ratios meet WCAG AA (4.5:1 text, 3:1 UI)
- [ ] Touch targets minimum 44x44px
- [ ] Focus states visible and keyboard accessible
- [ ] Error messages are actionable and clear
- [ ] Consistent terminology throughout
- [ ] Primary action clearly distinguished
- [ ] Form labels always visible
- [ ] Sufficient white space (8px grid)
- [ ] Responsive at all breakpoints
- [ ] Readable at 16px body text

### Key Metrics Reference

| Category | Value |
|----------|-------|
| Min contrast (AA) | 4.5:1 |
| Min contrast (AAA) | 7:1 |
| Min touch target | 44x44px |
| Base spacing unit | 4px or 8px |
| Body text size | 16px minimum |
| Line length | 45-75 characters |
| Line height | 1.4-1.6 |
| Modal max width | 560px |
| Button border radius | 4-8px |
| Card border radius | 8-12px |

### Resources

- [Nielsen Norman Group - 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design Guidelines](https://m3.material.io/)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
- [Microsoft Fluent Design](https://fluent2.microsoft.design/)

---

*Document compiled from authoritative UI/UX sources for LLM-generated interface reference.*
