import React from 'react'
import { useRouter } from 'next/router'
import { DocsThemeConfig, useConfig } from 'nextra-theme-docs'

const IDENTITY = 'Forward Deployed Engineer · Solutions Architect'
const DESCRIPTION =
  'James Aindow. Forward Deployed Engineer and solutions architect. Twenty years in engineering, twice CTO, currently contracting at Mastercard on MDES card tokenisation. Discovery to deployment, built with agentic AI tooling. Payments, blockchain and enterprise commerce.'
const SITE_URL = 'https://www.jamesaindow.co.uk'
const OG_IMAGE = `${SITE_URL}/og-image.png`

const personSchema = {
  '@context': 'https://schema.org',
  '@type': 'Person',
  name: 'James Aindow',
  jobTitle: IDENTITY,
  description: DESCRIPTION,
  url: SITE_URL,
  email: 'mailto:consult@jamesaindow.co.uk',
  image: OG_IMAGE,
  sameAs: [
    'https://www.linkedin.com/in/james-a-3988212aa/',
    'https://github.com/byzfault',
  ],
  knowsAbout: [
    'Forward deployed engineering',
    'Solutions architecture',
    'Technical discovery and scoping',
    'AI-assisted delivery',
    'Payments infrastructure',
    'Card tokenisation',
    'Blockchain and Layer 2 infrastructure',
    'Enterprise e-commerce',
  ],
}

const config: DocsThemeConfig = {
  logo: (
    <span>
      James Aindow{' '}
      <span style={{ opacity: 0.7 }}>· Forward Deployed Engineer</span>
    </span>
  ),

  project: {
    link: 'https://github.com/byzfault',
  },

  // next-seo owns title, description, Open Graph and Twitter, so those tags are
  // emitted once. `head` below carries only what next-seo does not handle.
  useNextSeoProps() {
    const { asPath } = useRouter()
    const { frontMatter, title } = useConfig()

    const description =
      (frontMatter?.description as string | undefined) || DESCRIPTION
    const pageTitle =
      asPath === '/' ? `James Aindow · ${IDENTITY}` : `${title} · James Aindow`
    const url = asPath === '/' ? SITE_URL : `${SITE_URL}${asPath}`

    return {
      // The home page h1 already carries the name, so only inner pages get it appended.
      titleTemplate: asPath === '/' ? '%s' : '%s · James Aindow',
      description,
      canonical: url,
      openGraph: {
        type: 'profile',
        siteName: 'James Aindow',
        title: pageTitle,
        description,
        url,
        images: [{ url: OG_IMAGE, width: 1200, height: 630, alt: 'James Aindow, Forward Deployed Engineer' }],
      },
      twitter: {
        cardType: 'summary_large_image',
      },
    }
  },

  footer: {
    text: 'Discovery to deployment. Payments, blockchain and enterprise commerce.',
  },

  feedback: {
    content: null, // removes "Question? Give us feedback"
  },

  editLink: {
    component: null, // removes "Edit this page"
  },

  // Per-page description and OG tags, falling back to the site defaults.
  head: function Head() {
    return (
      <>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="author" content="James Aindow" />

        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(personSchema) }}
        />

        {/* ---- Google Analytics ---- */}
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
    )
  },
}

export default config
