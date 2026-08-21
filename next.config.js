const withNextra = require('nextra')({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.tsx',
})

module.exports = withNextra({
  async redirects() {
    return [
      // Lanes: pages re-homed during the 4.0 repositioning
      { source: '/delivery', destination: '/technical-programme-manager', permanent: true },
      { source: '/technical-lead', destination: '/technical-programme-manager', permanent: true },
      { source: '/architecture', destination: '/solutions-architect', permanent: true },
      { source: '/writing', destination: '/documentation-lead', permanent: true },
      { source: '/quick-start', destination: '/', permanent: true },

      // Pages re-homed during the 3.0 restructure
      { source: '/case-studies', destination: '/mastercard', permanent: true },
      { source: '/writing-samples', destination: '/documentation-lead', permanent: true },
      { source: '/approach', destination: '/documentation-lead', permanent: true },

      // Retired earlier still, kept so old links land somewhere sensible
      { source: '/experience', destination: '/technical-programme-manager', permanent: true },
      { source: '/skills', destination: '/tools', permanent: true },
      { source: '/about', destination: '/', permanent: true },
    ]
  },
})
