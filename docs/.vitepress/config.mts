import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Phenotype Tooling",
  description: "Consolidated Rust workspace for Phenotype developer tooling.",
  base: process.env.GITHUB_PAGES === "true" ? "/phenotype-tooling/" : "/",
  cleanUrls: true,
  lastUpdated: true,
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
