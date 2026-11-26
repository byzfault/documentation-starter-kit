import React from 'react'
import { useRouter } from 'next/router'

// One generated banner per page, drawn by scripts/banners.py into public/banners.
const PAGES = new Set([
  'index', 'quick-start', 'agentic-content-designer', 'ai-enablement', 'trafficcount',
  'projects', 'architecture', 'case-studies', 'tools', 'delivery', 'history',
  'mastercard', 'starknet', 'writing', 'known-issues', 'faq', 'contact',
])

export function Banner() {
  const { asPath } = useRouter()
  const slug = asPath.split(/[?#]/)[0].replace(/^\/|\/$/g, '') || 'index'
  if (!PAGES.has(slug)) return null
  const home = slug === 'index'
  return (
    <div className={home ? 'ja-banner ja-banner-home' : 'ja-banner'}>
      {/* Decorative, so the alt text is empty. */}
      <img src={`/banners/${slug}.webp`} alt="" width={1800} height={600} decoding="async" />
      {home && (
        <>
          <img
            className="ja-banner-lockup ja-banner-lockup-detailed"
            src="/brand/james-aindow-detailed-horizontal-dark.svg"
            alt="James Aindow, AI Consultancy"
          />
          <img
            className="ja-banner-lockup ja-banner-lockup-simple"
            src="/brand/james-aindow-horizontal-dark.svg"
            alt="James Aindow, AI Consultancy"
          />
        </>
      )}
    </div>
  )
}

export function Main({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Banner />
      {children}
    </>
  )
}

export function Logo() {
  return (
    <span className="ja-logo">
      <img className="ja-logo-light" src="/brand/james-aindow-horizontal-light.svg" alt="James Aindow, AI Consultancy" width={180} height={33} />
      <img className="ja-logo-dark" src="/brand/james-aindow-horizontal-dark.svg" alt="James Aindow, AI Consultancy" width={180} height={33} />
    </span>
  )
}
