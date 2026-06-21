import { defineConfig } from 'vitepress';
import { createSiteMeta } from './site-meta.mjs';

const siteMeta = createSiteMeta();

export default defineConfig({
  title: 'phenotype-xdd',
  description: 'xDD Methodologies Compendium',
  lang: 'en-US',
  srcDir: '.',
  cleanUrls: true,
  lastUpdated: true,
  themeConfig: {
    siteTitle: 'phenotype-xdd',
    nav: [
      { text: 'Guide', link: '/guide/' },
      { text: 'Reference', link: '/reference/' },
      { text: 'Governance', link: '/reference/prd' },
    ],
    sidebar: {
      '/guide/': [
        { text: 'Guide', items: [{ text: 'Overview', link: '/guide/' }] },
      ],
      '/reference/': [
        {
          text: 'Reference',
          items: [
            { text: 'Overview', link: '/reference/' },
            { text: 'Product', link: '/reference/prd' },
            { text: 'Architecture Decisions', link: '/reference/adr' },
            { text: 'Requirements', link: '/reference/requirements' },
          ],
        },
      ],
      '/zh-CN/': [{ text: 'Chinese', items: [{ text: 'Overview', link: '/zh-CN/' }] }],
      '/zh-TW/': [{ text: 'Traditional Chinese', items: [{ text: 'Overview', link: '/zh-TW/' }] }],
      '/fa/': [{ text: 'Persian', items: [{ text: 'Overview', link: '/fa/' }] }],
      '/fa-Latn/': [{ text: 'Persian Latin', items: [{ text: 'Overview', link: '/fa-Latn/' }] }],
    },
    socialLinks: [{ icon: 'github', link: 'https://github.com/KooshaPari/phenotype-xdd' }],
    search: { provider: 'local' },
    footer: {
      message: 'xDD methodology reference hub',
      copyright: 'Phenotype',
    },
    outline: { level: [2, 3] },
    docFooter: { prev: 'Previous page', next: 'Next page' },
  },
  markdown: { lineNumbers: true },
  ignoreDeadLinks: true,
  locales: siteMeta.locales,
});
