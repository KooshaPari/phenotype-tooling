# Research

- Root `package.json` uses Bun workspaces and has no existing `overrides` block.
- The requested versions are transitive resolution targets for the workspace toolchain, so a root override is the direct place to pin them.
- `bun install` is the package-manager command aligned with the repo's `packageManager` setting.
- `@vitepress/theme-default` is not published on npm; the repository needed to use `vitepress/theme` instead to make install resolvable.
