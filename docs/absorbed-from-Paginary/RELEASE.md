# Paginary Release Process

## Versioning Scheme

Paginary uses **Semantic Versioning (SemVer)** for the monorepo and each package:
- Major: Breaking changes to site structure, theme, or deployment
- Minor: New documentation apps, feature additions, layout changes
- Patch: Content updates, bug fixes, CSS refinements

Current version: `0.0.1` (pre-release)

## Publish Targets

All packages target **npm** for distribution:

| Package | Status | Target | Type |
|---------|--------|--------|------|
| @paginary/handbook | alpha | npm | VitePress app |
| @paginary/specs | alpha | npm | VitePress app |
| @paginary/xdd | stub | npm | VitePress app |
| @paginary/journeys | alpha | npm | VitePress app |
| @paginary/theme | beta | npm | VitePress theme |

## Release Registry

The authoritative registry is maintained in:
- **Location**: `./release-registry.toml` (this directory)
- **Format**: TOML monorepo manifest with per-package metadata and publish targets
- **Schema**: Conforms to `docs/governance/release_registry_schema.md`

## Publish Process

1. **Build all apps**: `bun run build`
2. **Type-check**: `bun run type-check`
3. **Update versions** in all `package.json` files and `release-registry.toml`
4. **Update CHANGELOG.md** with content and feature changes
5. **Commit and tag**: `git tag v<version>`
6. **Publish to npm**:
   ```bash
   cd packages/paginary-theme && npm publish --access public
   cd apps/handbook && npm publish --access public
   # ... repeat for all apps with @paginary/ scope
   ```

## Release Registry Location

- **File**: `release-registry.toml` (repository root)
- **Format**: TOML
- **Contents**: Monorepo metadata, all 5 documentation packages with npm publish targets
- **Update**: When adding new documentation apps or updating publishing configuration

## Additional Resources

- **VitePress**: https://vitepress.dev/guide/getting-started
- **Bun**: https://bun.sh/docs
- **Turbo**: https://turbo.build/repo/docs
- **npm Publishing**: https://docs.npmjs.com/cli/publish
- **Theme Guide**: See `packages/paginary-theme/README.md`

## Content Consolidation

Paginary federates content from multiple source repositories. See `docs/CONSOLIDATION.md` for:
- Source repository mappings
- Content pull workflow
- Sync schedules
