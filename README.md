# FinanceRookie

Magazine editoriale statico (Astro + Tailwind) pensato per un brand minimal bianco/nero con accento lime. Monorepo, nessun backend, deploy gratuito su Cloudflare Pages: tutto GitOps, contenuti in Markdown e build totalmente statica.

## Senso del progetto
FinanceRookie è un magazine che traduce finanza, macro e mercati in articoli sintetici, pragmatici e “actionable”. La struttura è costruita per:
- **pubblicare in modo scalabile** (contenuti come file, validazione automatica, build veloce);
- **mantenere qualità editoriale** (schema dei campi, fonti obbligatorie, tag e takeaways);
- **ridurre costi/complessità** (zero DB, zero backend, hosting statico).

## Stack
- Astro 4 + TypeScript
- Tailwind CSS + @tailwindcss/typography
- Content Collections (Markdown `.md`)
- SEO: OpenGraph/Twitter, JSON-LD NewsArticle, RSS, Sitemap
- Output statico (Cloudflare Pages)

## Struttura repo (pulita)
Tutto il codice applicativo vive in `apps/finance-rookie`: il root contiene solo tooling, contenuti e documentazione.
```
apps/
  finance-rookie/           # app Astro (un sito)
    public/                 # asset statici (immagini, headers)
    src/
      assets/               # asset interni all’app
      content/
        articles/           # articoli markdown
      layouts/              # layout pagina
      pages/                # routes Astro (home, categorie, articoli, rss)
      site.config.ts        # config brand/categorie/autori
packages/
  theme/                    # componenti UI + stili condivisi
  content-schema/           # schema editoriale (validazione contenuti)
  scripts/                  # CLI editoriale (GitOps)
content/
  inbox/                    # JSON in ingresso (workflow ingest)
  processed/                # JSON archiviati
docs/                       # documentazione operativa
```

## Configurazione
### 1) Site config
- `apps/finance-rookie/src/site.config.ts` → branding, autori, categorie, nav.
- `apps/finance-rookie/site.config.json` → default author + categorie per CLI.

### 2) Stili (token-driven)
Stile centralizzato in:
- `packages/theme/styles/variables.css` → token (spacing, grid, typography, colori).
- `packages/theme/styles/global.css` → layout, header, grid, componenti UI.
- `packages/theme/styles/prose.css` → tipografia e contenuti editoriali.

**Regola:** niente padding ad-hoc, tutto usa `--container-pad`, `--grid-gap`, `--section-y`.

### 3) Content schema
- `packages/content-schema/index.ts` → schema completo e regole editoriali.
- `apps/finance-rookie/src/content/config.ts` → schema Astro usato in build.

## Struttura articoli
Gli articoli sono file Markdown in `apps/finance-rookie/src/content/articles/`.  
Il **slug** è derivato dal nome file (es. `tassi-bce.md` → `/article/tassi-bce`).

### Frontmatter (completo)
Campi completi previsti (vedi schema completo nei file sopra):
- `title` (string, 10–120) – titolo editoriale.
- `excerpt` (string, 40–180) – sottotesto/riassunto.
- `category` (enum) – slug categoria da `site.config.ts`.
- `tags` (array) – massimo 8.
- `author_id` (string) – autore da `site.config.ts`.
- `status` (`draft` | `published`).
- `published_at` (date ISO) – obbligatoria per `published`.
- `updated_at` (date ISO, opzionale) – ultima modifica.
- `hero_image` (string, opzionale) – immagine principale (path in `public/` o URL).
- `hero_alt` (string, opzionale) – alt text immagine.
- `hero_caption` (string, opzionale) – didascalia immagine.
- `hero_source` (URL, opzionale) – fonte immagine.
- `takeaways` (max 3), `impact`, `do_now` (max 2), `rookie_lens`.
- `sources` (array) – almeno 1 fonte (title + url).
- `featured` (boolean).

### Esempio completo
```md
---
title: "Titolo articolo"
excerpt: "Sottotesto/riassunto in 1-2 frasi."
category: "analisi"
tags: ["tassi", "macro"]
author_id: "redazione"
status: "published"
published_at: "2024-06-08T00:00:00Z"
updated_at: "2024-06-10T00:00:00Z"
hero_image: "/images/hero-analisi.svg"
hero_alt: "Grafico tassi e spread"
hero_caption: "La politica monetaria entra nelle scelte quotidiane."
hero_source: "https://www.ecb.europa.eu/"
takeaways:
  - Il costo del denaro condiziona mutui e prestiti.
  - I tassi reali cambiano il rendimento atteso.
impact: "Mutui, Imprese, Investitori"
do_now:
  - Ricalibra il budget sui nuovi livelli di rata.
  - Confronta tassi fissi e variabili.
rookie_lens: "Se la rata pesa troppo, rivedi prima il budget e poi il tasso."
sources:
  - title: "Fonte ufficiale"
    url: "https://example.com"
---

Testo dell’articolo...
```

### Struttura contenuto (nel body)
Nel corpo dell’articolo puoi aggiungere:
- **Heading** (H2/H3) per sezioni logiche.
- **Paragrafi** sintetici e orientati all’azione.
- **Keyword highlight** con `[[kw:parola chiave]]`.

### Componenti editoriali (come usarli)
- **Titolo**: deve comunicare il tema principale e il contesto.
- **Sottotesto (excerpt)**: 1–2 frasi di posizionamento.
- **Autore**: usa `author_id` presente in `site.config.ts`.
- **Immagine**: usa `hero_image` se disponibile (consigliato).
- **Rookie lens**: una frase che traduce l’impatto per un lettore non esperto.
- **Takeaways + Do now**: liste brevi per valore immediato.

## Come aggiungere un articolo
### Opzione A — manuale (Markdown)
1. Crea un file in `apps/finance-rookie/src/content/articles/`.
2. Compila frontmatter e contenuto Markdown.
3. Verifica localmente e committa.

### Opzione B — workflow JSON (GitOps)
1. Carica un JSON in `content/inbox/`.
2. Push su GitHub → workflow `content_ingest.yml`.
3. Il workflow genera Markdown, archivia in `content/processed/` e apre una PR.

### CLI utili
```bash
python packages/scripts/fr_cli.py import-json --input path/to/article.json
python packages/scripts/fr_cli.py validate --site finance-rookie
```
Comandi disponibili:
- `import-json` / `new-from-json` (alias)
- `publish-json` (richiede `published_at`)
- `validate`, `publish`, `schedule`, `open-pr`

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

## Cloudflare Pages
- **Build command:** `corepack enable && pnpm install --frozen-lockfile && pnpm -C apps/finance-rookie build`
- **Output directory:** `apps/finance-rookie/dist`
- **Node version:** 20 LTS
- **Security headers:** `apps/finance-rookie/public/_headers`

## CI
GitHub Actions valida contenuti + build:
- `python packages/scripts/fr_cli.py validate --site finance-rookie`
- `pnpm -C apps/finance-rookie build`

## Scalare a più siti (future `apps/*`)
1. Crea `apps/<nuovo-sito>` (clone della struttura).
2. Aggiungi `site.config.ts` e `site.config.json`.
3. Build: `pnpm -C apps/<nuovo-sito> build`.
4. Un progetto Cloudflare Pages per app.

## Keyword highlight nel Markdown
Per evidenziare keyword senza MDX:
```
[[kw:parola chiave]]
```
Il plugin `packages/theme/utils/rehypeKwHighlight.ts` genera:
```html
<span class="kw">parola chiave</span>
```

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

## Note operative
- Zero backend, zero DB, zero Workers.
- Costi = 0€ (Cloudflare Pages free + GitHub Actions free).
