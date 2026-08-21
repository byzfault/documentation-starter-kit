const withNextra = require('nextra')({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.tsx',
})

module.exports = withNextra({
  async redirects() {
    return [
      // Pages re-homed during the 3.0 restructure
      { source: '/case-studies', destination: '/mastercard', permanent: true },
      { source: '/writing-samples', destination: '/writing', permanent: true },
      { source: '/approach', destination: '/writing', permanent: true },
    ]
  },
})
