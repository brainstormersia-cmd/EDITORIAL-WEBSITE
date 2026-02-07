# FinanceRookie — Manuale operativo

Questo README descrive **come è organizzato il repo**, dove intervenire per contenuti/asset, e **i punti unici** in cui modificare logo e padding senza toccare più file.  
Tutti i path indicati sono reali nel repo; se nel tuo caso sono diversi, usa i comandi di ricerca in fondo.

## Struttura cartelle (panoramica)
```
apps/
  finance-rookie/
    public/                 # asset statici (logo, immagini raggiungibili via /...)
    src/
      assets/               # asset interni all’app (se importati da codice)
      components/           # componenti Astro dell’app
      config/               # config centralizzata (site, costanti)
      content/
        articles/           # articoli markdown (content collections)
      layouts/              # layout pagina
      lib/                  # utility (ranking, badge, ecc.)
      pages/                # routes Astro (home, categorie, articoli, rss)
      site.config.ts        # re-export config (compatibilità import)
packages/
  theme/                    # componenti UI + stili condivisi
content/
  inbox/                    # JSON in ingresso (workflow ingest)
  processed/                # JSON archiviati
docs/                       # documentazione operativa
```

## Dove inserire articoli
**Cartella**: `apps/finance-rookie/src/content/articles/`  
Ogni file `.md` diventa `/article/<slug>` dove `<slug>` è il nome del file.

### Schema e categorie (enum)
Lo schema è definito in:
- `apps/finance-rookie/src/content/config.ts` (schema Astro per build).  

Le categorie ammesse sono lette da:
- `apps/finance-rookie/src/config/site.ts` (vedi `SITE_CONFIG.categories`).  

> Se una categoria non è presente in `SITE_CONFIG.categories`, Astro genera errore di enum.

## Dove mettere le immagini degli articoli
**Cartella consigliata**: `apps/finance-rookie/public/images/`  
Referenzia le immagini con path assoluto:
```
hero_image: "/images/hero-analisi.svg"
```
Questo path funziona perché i file in `public/` vengono serviti alla root (`/`).

## Dove mettere il logo e come cambiarlo
**Logo attivo**: `apps/finance-rookie/public/logo1.svg`  
Usato in:
- `apps/finance-rookie/src/components/Header.astro` (logo in header).  
- `apps/finance-rookie/src/layouts/ArticleLayout.astro` (JSON-LD).  

### Cambiare logo
Sostituisci il file `public/logo1.svg` oppure cambia il path nello `Header.astro`.

### Cambiare dimensione logo
Nel header modifica **solo**:
```astro
<img class="h-8 w-auto" ... />
```
File: `apps/finance-rookie/src/components/Header.astro`.

## Config centrale (site config)
**Singolo punto**: `apps/finance-rookie/src/config/site.ts`  
Contiene:
- nome, descrizione, colori
- nav (menu)
- categories (enum)
- authors (avatar/nomi)

> `apps/finance-rookie/src/site.config.ts` è solo un re-export per compatibilità.

## Padding laterale del sito (punto unico)
Il padding orizzontale è controllato da **una sola variabile**:
```
--container-pad
```
File: `packages/theme/styles/variables.css`  
Modifica lì per cambiare il padding globale senza toccare layout o componenti.

## Comandi principali
```bash
pnpm install
pnpm -C apps/finance-rookie dev
pnpm -C apps/finance-rookie build
pnpm -C apps/finance-rookie preview
```

## Checklist “quando qualcosa non si vede”
1. **Path immagine**: controlla che stia in `public/` e usi `/images/...`.
2. **Schema categorie**: se nuova categoria, aggiungila in `SITE_CONFIG.categories`.
3. **Cache browser**: hard refresh (Cmd+Shift+R / Ctrl+Shift+R).
4. **Frontmatter**: verifica `status: "published"` e `published_at` valido.
5. **Content Collection**: errori di build spesso indicano frontmatter non conforme.

## Convenzioni consigliate
- **Naming articoli**: `categoria-tema.md` (es. `analisi-tassi-bce.md`).
- **Slug**: deriva dal nome file (evita spazi e maiuscole).
- **Immagini**: `hero-<tema>.svg` o `.jpg` dentro `/public/images/`.

## Se il path è diverso nel tuo repo
Usa questi comandi per trovare i file:
```bash
rg -n "SITE_CONFIG" apps/finance-rookie/src
rg -n "content/collections|defineCollection|content/config" apps/finance-rookie/src
rg -n "logo1.svg|logo.svg" apps/finance-rookie/src apps/finance-rookie/public
rg -n "--container-pad|--gutter" packages/theme/styles
```
