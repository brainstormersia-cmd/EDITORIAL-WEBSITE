# FinanceRookie

Magazine editoriale statico costruito con Astro + Tailwind CSS, pensato per un brand minimal bianco/nero con accento lime.

## Stack
- Astro 4 + TypeScript
- Tailwind CSS + @tailwindcss/typography
- Content Collections (Markdown `.md`)
- SEO: OpenGraph/Twitter, JSON-LD NewsArticle, RSS, Sitemap
- Output statico per Cloudflare Pages

## Setup locale
```bash
npm install
npm run dev
```
Preview: <http://localhost:4321>

## Build produzione
```bash
npm run build
npm run preview
```

## Cloudflare Pages
- **Build command:** `npm run build`
- **Output directory:** `dist`
- **Node version:** >= 18

## Keyword highlight nel Markdown
Per evidenziare keyword in modo stabile senza MDX, usa la sintassi:

```
[[kw:parola chiave]]
```

Il plugin `src/utils/rehypeKwHighlight.ts` trasforma la sintassi in:

```html
<span class="kw">parola chiave</span>
```

Il plugin è registrato nella pipeline Markdown in `astro.config.ts`.
