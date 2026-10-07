import React from 'react'
import { useRouter } from 'next/router'
import { DocsThemeConfig } from 'nextra-theme-docs'

const IDENTITY = 'AI Enablement & Technical Delivery Lead · ex-agency CTO · Mastercard, StarkWare'
const DESCRIPTION =
  'James Aindow. I help teams adopt AI inside complex technical environments. Twenty years across enterprise e-commerce, blockchain infrastructure and card payments. Twice agency CTO, with teams of 12 to 20+. Recent work on Mastercard MDES and Starknet. I read and review code; I ship with agentic tooling.'
const SITE_URL = 'https://jamesaindow.co.uk'

const personSchema = {
  '@context': 'https://schema.org',
  '@type': 'Person',
  name: 'James Aindow',
  jobTitle: IDENTITY,
  description: DESCRIPTION,
  url: SITE_URL,
  email: 'mailto:consult@jamesaindow.co.uk',
  sameAs: ['https://www.linkedin.com/in/james-a-3988212aa/'],
  knowsAbout: [
    'AI enablement',
    'Agentic tooling',
    'RAG content design',
    'Engineering leadership',
    'Technical delivery',
    'Payments infrastructure',
    'Card tokenisation',
    'Ethereum Layer 2',
    'Enterprise e-commerce',
  ],
}

const config: DocsThemeConfig = {
  logo: (
    <span>
      James Aindow{' '}
      <span style={{ opacity: 0.7 }}>· AI Enablement &amp; Technical Delivery</span>
    </span>
  ),

  useNextSeoProps() {
    const { asPath } = useRouter()
    // The home page h1 already carries the name, so only inner pages get it appended.
    return {
      titleTemplate: asPath === '/' ? '%s' : '%s · James Aindow',
      description: DESCRIPTION,
    }
  },

  footer: {
    text: 'AI enablement and technical delivery for payments and blockchain infrastructure',
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
