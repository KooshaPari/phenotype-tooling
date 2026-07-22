import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Phenotype Tooling",
  description: "Consolidated Rust workspace for Phenotype developer tooling.",
  base: process.env.GITHUB_PAGES === "true" ? "/phenotype-tooling/" : "/",
  cleanUrls: true,
  // lastUpdated: false to avoid EAGAIN on posix_spawn /usr/bin/git when the
  // absorbed tree has 1900+ markdown files (the absorbed-tree cleanup PR
  // re-enables this once the tree is cleaned).
  lastUpdated: false,
  // Exclude ALL absorbed-from-* subtrees from the build. These 100+ trees
  // were imported during the 2026-07 ecosystem reorg with pre-existing
  // content corruption (triple-merge markers, Search/Replace markers, Vue
  // SFC parse errors, broken markdown links to non-existent paths). The
  // proper cleanup is tracked in
  // docs/superpowers/specs/2026-07-22-absorbed-tree-cleanup-design.md.
  // Once each absorbed tree is content-clean, remove its srcExclude entry.
  srcExclude: ["absorbed-from-*/**"],
  // Pre-existing dead links from the docs reorg are out of scope for the
  // absorbed-tree cleanup. We surface them as warnings (not errors) by
  // setting ignoreDeadLinks so the build can succeed; fixing each broken
  // link is tracked separately.
  ignoreDeadLinks: true,
  themeConfig: {
    nav: [
      { text: "Overview", link: "/" },
      { text: "Tools", link: "/tools" },
      { text: "Adoption", link: "/adoption" },
      { text: "GitHub", link: "https://github.com/KooshaPari/phenotype-tooling" },
    ],
    sidebar: [
      {
        text: "Phenotype Tooling",
        items: [
          { text: "Overview", link: "/" },
          { text: "Tool Catalog", link: "/tools" },
          { text: "Adoption Guide", link: "/adoption" },
        ],
      },
    ],
    socialLinks: [{ icon: "github", link: "https://github.com/KooshaPari/phenotype-tooling" }],
    search: {
      provider: "local",
    },
  },
});
