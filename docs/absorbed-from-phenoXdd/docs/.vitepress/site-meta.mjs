export function createSiteMeta({ base = '/' } = {}) {
  return {
    base,
    title: 'phenotype-xdd',
    description: 'xDD Methodologies Compendium',
    themeConfig: {
      nav: [
        { text: 'Home', link: base || '/' },
        { text: 'Guide', link: '/guide/' },
        { text: 'Reference', link: '/reference/' },
      ],
    },
  }
}
