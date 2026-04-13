import React from 'react'
import { DocsThemeConfig } from 'nextra-theme-docs'

const config: DocsThemeConfig = {
  logo: <span>James Aindow — Senior Technical Writer</span>,

  useNextSeoProps() {
    return {
      titleTemplate: '%s'
    }
  },

  footer: {
    text: 'Bridging the gap between technical and non technical',
  },

  feedback: {
    content: null  // This removes "Question? Give us feedback"
  },

  editLink: {
    component: null  // This removes "Edit this page"
  },

  // ---- Add Google Analytics here ----
  head: (
    <>
      <script
        async
        src="https://www.googletagmanager.com/gtag/js?id=G-B5TMY3QM7J"
      />
      <script
        dangerouslySetInnerHTML={{
          __html: `
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-B5TMY3QM7J');
          `,
        }}
      />
    </>
  ),
}

export default config
