import React from 'react'
import { useRouter } from 'next/router'
import { DocsThemeConfig } from 'nextra-theme-docs'
import { Logo, Main } from './components/banner'

const IDENTITY = 'Solutions Architect · AI Enablement · CTO'
const DESCRIPTION =
  'James Aindow. Solutions architect and twice agency CTO with 20 years in enterprise commerce and card payments. Recent work: an agentic content designer in production at a global financial services company. I read and review code. I ship with agentic tooling.'
const SITE_URL = 'https://jamesaindow.co.uk'

const personSchema = {
  '@context': 'https://schema.org',
  '@type': 'Person',
  name: 'James Aindow',
  jobTitle: IDENTITY,
  description: DESCRIPTION,
  url: SITE_URL,
  email: 'mailto:consult@jamesaindow.co.uk',
  sameAs: ['https://www.linkedin.com/in/james-aindow'],
  knowsAbout: [
    'Solutions architecture',
    'AI enablement',
    'Agentic tooling',
    'Agent skills and evals',
    'Engineering leadership',
    'Enterprise e-commerce',
    'Payments infrastructure',
    'Card tokenisation',
    'RAG content design',
  ],
}

const config: DocsThemeConfig = {
  logo: <Logo />,

  // Signal Blue #2F4BFF on Mist, Glow #7B93FF on Ink
  primaryHue: { light: 233, dark: 229 },
  primarySaturation: 100,

  // Every page opens with its banner
  main: Main,

  useNextSeoProps() {
    const { asPath } = useRouter()
    // The home page h1 already carries the name, so only inner pages get it appended.
    return {
      titleTemplate: asPath === '/' ? '%s' : '%s · James Aindow',
      description: DESCRIPTION,
    }
  },

  footer: {
    text: 'Solutions architecture, AI enablement and technical leadership for commerce and payments',
  },

  feedback: {
    content: null, // This removes "Question? Give us feedback"
  },

  editLink: {
    component: null, // This removes "Edit this page"
  },

  head: (
    <>
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta name="description" content={DESCRIPTION} />
      <meta name="author" content="James Aindow" />
      <meta name="theme-color" content="#11151C" />
      <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
      <link rel="icon" type="image/svg+xml" href="/brand/icon-dark.svg" />
      <link rel="apple-touch-icon" href="/apple-touch-icon.png" />

      <meta property="og:type" content="profile" />
      <meta property="og:site_name" content="James Aindow" />
      <meta property="og:title" content={`James Aindow · ${IDENTITY}`} />
      <meta property="og:description" content={DESCRIPTION} />
      <meta property="og:url" content={SITE_URL} />

      <meta name="twitter:card" content="summary" />
      <meta name="twitter:title" content={`James Aindow · ${IDENTITY}`} />
      <meta name="twitter:description" content={DESCRIPTION} />

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
  ),
}

export default config
