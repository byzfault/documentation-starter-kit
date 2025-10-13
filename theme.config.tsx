import React from 'react'
import { DocsThemeConfig } from 'nextra-theme-docs'

const config: DocsThemeConfig = {
  logo: <span>James Aindow — Technical Writer</span>,
  useNextSeoProps() {
    return {
      titleTemplate: '%s'
    }
  },
  footer: {
    text: 'Bridging the gap between technical and non technical',
  },
}

export default config