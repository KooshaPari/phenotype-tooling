# Paginary — Claude Code Instructions

## Project Overview

- **Name**: Paginary
- **Description**: Federated documentation hub — handbooks, specs, X-driven dev, user journeys
- **Type**: VitePress 1.6+ monorepo (Bun workspaces, Turbo orchestration)
- **Language Stack**: TypeScript, Vue 3, CSS (no backend)
- **Deployment**: Static site (Vercel, Netlify, or GitHub Pages)

## AgilePlus Mandate

All work MUST be tracked in AgilePlus:
- Reference: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
- CLI: `cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus && agileplus <command>`

## Work Requirements

1. **Check for AgilePlus spec before implementing**
2. **Create spec for new work**: `agileplus specify --title "<feature>" --description "<desc>"`
3. **Update work package status**: `agileplus status <feature-id> --wp <wp-id> --state <state>`
4. **No code without corresponding AgilePlus spec**

## Stack & Commands

### Build System

- **Package Manager**: Bun (`bun install`, `bun run <script>`)
- **Monorepo Orchestration**: Turbo (`turbo run <task>`)
- **Site Generator**: VitePress 1.6+
- **Runtime**: Node.js (Bun runtime)

### Key Commands

```bash
# From repo root: /Users/kooshapari/CodeProjects/Phenotype/repos/Paginary

bun install              # Install all dependencies
bun run dev              # Start dev (hot reload, all apps)
bun run build            # Build all sites
bun run preview          # Serve built sites locally
bun run clean            # Clean dist directories

# Individual app commands (cd into app first)
cd apps/handbook && bun run dev
cd apps/specs && bun run build
```

### Local Quality Checks

```bash
# Type-check all apps
bun run type-check

# Lint (add if eslint configured)
bun run lint

# Verify build
bun run build
```

## Structure

```
Paginary/
  apps/
    handbook/             → PhenoHandbook (playbooks, governance)
    specs/                → PhenoSpecs (feature specs, ADRs, design)
    xdd/                  → X-driven dev (TDD, BDD, QA governance)
    journeys/             → phenotype-journeys (user flows, personas)
  packages/
    paginary-theme/       → Shared VitePress theme + impeccable CSS
  vitepress.config.ts     → Root VitePress config (federation index)
  turbo.json              → Turbo monorepo config
  package.json            → Bun workspaces manifest
  docs/
    CONSOLIDATION.md      → Source repo mapping and content strategy
```

## Content Sources & Consolidation

Paginary is a **read-only federation** — content is copied (not moved) from source repos.

| App | Source Repo | Content Type | Status |
|-----|-------------|--------------|--------|
| handbook | PhenoHandbook | Playbooks, governance guides | ⧖ Pending pull |
| specs | PhenoSpecs | Feature specs, ADRs, design docs | ⧖ Pending pull |
| xdd | phenoXdd | TDD/BDD, QA governance, smart contracts | ⧖ Pending pull |
| journeys | phenotype-journeys | User flows, personas, workflows | ⧖ Pending pull |

**Content Pull Workflow**:
```bash
# Example: sync handbook
cp -r /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoHandbook/docs/* \
  apps/handbook/
```

See `docs/CONSOLIDATION.md` for full details.

## Theme & Design

- **Shared Theme**: `packages/paginary-theme/`
- **CSS Baseline**: impeccable (github.com/pbakaus/impeccable)
- **Fonts**: Inter (UI) + JetBrains Mono (code)
- **Color Scheme**: Dark mode first, light mode optional
- **Accessibility**: WCAG 2.1 AA baseline

### Adding Theme Changes

1. Edit `packages/paginary-theme/style.css` or `index.ts`
2. Hot reload in dev mode — all apps see changes immediately
3. Rebuild to verify: `bun run build`

## Development Workflow

### Adding a Page

1. Create `.md` file in `apps/<app>/`
2. Update sidebar in `vitepress.config.ts` if new section
3. Changes hot-reload in dev mode
4. Verify: Open local URL in browser
5. Build to confirm: `bun run build`

### Adding a Sub-App

1. Create `apps/newapp/` with `package.json`, `index.md`
2. Update root `package.json` workspaces
3. Update `vitepress.config.ts` nav and sidebar
4. Verify: `bun install && bun run build`

## Deployment

### Build

```bash
# Build all sites (outputs to apps/*/‌.vitepress/dist/)
bun run build
```

### Environment Variables

```bash
VITEPRESS_SITE_URL=https://phenotype.dev/paginary  # Deployment URL
VITEPRESS_THEME=paginary-theme                     # Theme name
```

### Hosting Options

1. **Vercel**: Connect repo, set base URL, auto-deploy on push
2. **Netlify**: Same as Vercel
3. **GitHub Pages**: Configure GH Actions to build and push to `gh-pages` branch
4. **Self-hosted**: Serve `apps/*/‌.vitepress/dist/` via nginx/Apache

## Documentation Standards

- **Format**: GFM (GitHub Flavored Markdown)
- **Code Blocks**: Language-tagged (e.g., ` ```typescript `)
- **Images**: Max width 100%, lazy-loaded by VitePress
- **Diagrams**: Mermaid (embedded) or SVG
- **Links**: Relative paths preferred
- **Encoding**: UTF-8 (required)

## Git & Versioning

- **Repo Path**: `/Users/kooshapari/CodeProjects/Phenotype/repos/Paginary`
- **Main Branch**: `main`
- **Version**: Semantic versioning (starts at 0.0.1)
- **Changelog**: `CHANGELOG.md` (Keep a Changelog format)
- **Commits**: Feature-based with AgilePlus references

### Commit Pattern

```bash
git add <specific files>
git -c commit.gpgsign=false commit -m "feat(Paginary): <description>"
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Build fails | Check sidebar entries in `vitepress.config.ts`, verify relative links |
| Hot reload not working | Restart dev: `Ctrl+C` then `bun run dev` |
| Type errors | Run `bun run type-check` |
| Theme not updating | `bun run clean && bun install && bun run build` |
| Port conflicts | Change in `vitepress.config.ts` via `vite.server.port` |

## References

- **VitePress**: https://vitepress.dev/
- **Turbo**: https://turbo.build/
- **Bun**: https://bun.sh/
- **impeccable CSS**: https://github.com/pbakaus/impeccable
- **AGENTS.md**: See local AGENTS.md for agent-specific instructions

## Key Policies

1. **No content moves** — Copy from source repos only
2. **Read-only federation** — Paginary reflects sources exactly
3. **Shared theme first** — Update theme in `paginary-theme/`, not per-app
4. **Turbo for all builds** — Use `bun run <script>` for orchestration
5. **Type safety** — All TypeScript files must pass `type-check`

## Related Repositories

- **PhenoHandbook**: `/Users/kooshapari/CodeProjects/Phenotype/repos/PhenoHandbook`
- **PhenoSpecs**: `/Users/kooshapari/CodeProjects/Phenotype/repos/PhenoSpecs`
- **phenoXdd**: (location TBD — may be in thegent or AgilePlus)
- **phenotype-journeys**: `/Users/kooshapari/CodeProjects/Phenotype/repos/phenotype-journeys`
- **Parent Workspace**: `/Users/kooshapari/CodeProjects/Phenotype/repos/CLAUDE.md`

## Contact & Escalation

For clarifications, refer to parent workspace CLAUDE.md or project owner.
