# FinanceRookie

Magazine editoriale statico costruito con Astro + Tailwind CSS, pensato per un brand minimal bianco/nero con accento lime. Architettura monorepo, zero backend, deploy gratuito su Cloudflare Pages.

## Stack
- Astro 4 + TypeScript
- Tailwind CSS + @tailwindcss/typography
- Content Collections (Markdown `.md`)
- SEO: OpenGraph/Twitter, JSON-LD NewsArticle, RSS, Sitemap
- Output statico per Cloudflare Pages

## Struttura repo (scalabile)
```
apps/
  finance-rookie/          # app Astro (una app = un sito)
packages/
  theme/                   # componenti UI + stili condivisi
  content-schema/          # schema articoli
  scripts/                 # CLI editoriale (GitOps)
content/
  inbox/                   # JSON in ingresso (workflow ingest)
  processed/               # JSON archiviati
```

## Configurazione rapida
### 1) Site config
- `apps/finance-rookie/src/site.config.ts` → branding, autori, categorie, nav.
- `apps/finance-rookie/site.config.json` → default author + categorie per CLI.

### 2) Stili (token-driven)
Stile raggruppato in pochi file, modificabili in modo centralizzato:
- `packages/theme/styles/variables.css` → token (spacing, grid, typography, colori).
- `packages/theme/styles/global.css` → layout, header, grid, componenti UI.
- `packages/theme/styles/prose.css` → tipografia e contenuti editoriali.

**Regola:** niente padding ad-hoc, tutto usa `--container-pad`, `--grid-gap`, `--section-y`.

### 3) Content schema
- `packages/content-schema/index.ts` → campi richiesti e regole editoriali.
- `slug` **non** sta nel frontmatter: la source of truth è `entry.slug` (Astro).

## Setup locale
```bash
corepack enable
pnpm install
pnpm -C apps/finance-rookie dev
```
Preview: <http://localhost:4321>

## Build produzione
```bash
pnpm -C apps/finance-rookie build
pnpm -C apps/finance-rookie preview
```

## Cloudflare Pages (free)
- **Build command:** `corepack enable && pnpm install --frozen-lockfile && pnpm -C apps/finance-rookie build`
- **Output directory:** `apps/finance-rookie/dist`
- **Node version:** 20 LTS
- **Security headers:** `apps/finance-rookie/public/_headers`

## Workflow editoriale (GitOps)
### JSON → Markdown (manuale)
```bash
python packages/scripts/fr_cli.py import-json --input path/to/article.json
python packages/scripts/fr_cli.py validate --site finance-rookie
```

### JSON → Markdown → PR (automatico)
1. Carica JSON in `content/inbox/`.
2. Push su GitHub → workflow `content_ingest.yml`.
3. Il workflow genera i markdown, archivia i JSON in `content/processed/` e apre una PR.

### CLI disponibili
- `import-json` / `new-from-json` (alias)
- `publish-json` (richiede `published_at`)
- `validate`
- `publish`, `schedule`, `open-pr`

## CI (magazine-grade)
GitHub Actions valida contenuti + build:
- `python packages/scripts/fr_cli.py validate --site finance-rookie`
- `pnpm -C apps/finance-rookie build`

## Scalare a più siti (future `apps/*`)
1. Crea `apps/<nuovo-sito>` (clone della struttura dell’app).
2. Aggiungi `site.config.ts` e `site.config.json`.
3. Build: `pnpm -C apps/<nuovo-sito> build`.
4. Un progetto Cloudflare Pages per app.

## Diagnostica npm/pnpm 403
```bash
npm config get registry
pnpm config get registry
node -v
npm -v
```
Se serve:
```bash
pnpm config set registry https://registry.npmjs.org/
```

## Keyword highlight nel Markdown
Per evidenziare keyword senza MDX, usa:
```
[[kw:parola chiave]]
```
Il plugin `packages/theme/utils/rehypeKwHighlight.ts` genera:
```html
<span class="kw">parola chiave</span>
```

## Note operative
- Zero backend, zero DB, zero Workers.
- Costi = 0€ (Cloudflare Pages free + GitHub Actions free).
