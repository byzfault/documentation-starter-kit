import React from 'react'
import { useRouter } from 'next/router'
import { DocsThemeConfig } from 'nextra-theme-docs'

const IDENTITY = 'Senior Technical Leader · Programme Delivery & Solutions Architecture'
const DESCRIPTION =
  'James Aindow. Twenty years in enterprise e-commerce and payments engineering. Two CTO roles, distributed teams of up to 20, platform architecture and delivery ownership. Recent work on Mastercard MDES tokenisation and Starknet infrastructure.'
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
    'Programme delivery',
    'Solutions architecture',
    'Payments infrastructure',
    'Card tokenisation',
    'Stablecoin infrastructure',
    'Enterprise e-commerce',
  ],
}

const config: DocsThemeConfig = {
  logo: (
    <span>
      James Aindow{' '}
      <span style={{ opacity: 0.7 }}>· Delivery &amp; Solutions Architecture</span>
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
    text: 'Delivery and architecture for payments and blockchain infrastructure',
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
