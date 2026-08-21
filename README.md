# jamesaindow.co.uk

Personal site for James Aindow: Forward Deployed Engineer and solutions architect.
Built with [Nextra](https://nextra.site) on Next.js, deployed on Vercel.

## Local development

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
```

## Structure

- `pages/` MDX content, one file per route. `pages/_meta.json` controls the sidebar
- `components/project-card.tsx` portfolio cards
- `public/` OG image, robots.txt, sitemap.xml
- `next.config.js` redirects for every URL the site has ever served
- `theme.config.tsx` nav, footer, per-page meta and OG tags

## Shipping a portfolio project

Cards default to "In build" with no demo link. To mark one live, change the
call site in `pages/portfolio.mdx`:

```diff
-    status="build"
+    status="live"
+    url="https://example.com"
```

The status pill, the demo link and the "No public demo yet" note all follow from
those two props. Nothing else needs touching.

## Adding a page

1. Create `pages/<slug>.mdx` with `title` and `description` front matter
2. Add the slug to `pages/_meta.json`
3. Add the URL to `public/sitemap.xml`
