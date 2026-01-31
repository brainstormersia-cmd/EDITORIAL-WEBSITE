# Deploy su Cloudflare Pages (Free)

## Configurazione consigliata (monorepo)
- **Root directory:** repo root (`/`).
- **Build command:** `corepack enable && pnpm install --frozen-lockfile && pnpm -C apps/finance-rookie build`
- **Output directory:** `apps/finance-rookie/dist`
- **Node version:** 20 LTS

## Alternativa semplice (root = app)
- **Root directory:** `apps/finance-rookie`
- **Build command:** `corepack enable && pnpm install --frozen-lockfile && pnpm build`
- **Output directory:** `dist`

## Per ogni sito (scaling fino a 10 siti)
- Un progetto Cloudflare Pages per app (`apps/<nome-app>`).
- Stessi script root con workspace (es. `pnpm -C apps/<nome-app> build`).
- Stesso output: `apps/<nome-app>/dist`.

## Note
- Nessun Workers/D1/R2: il progetto è static-first e a costo 0€.
- Il deploy è GitOps: merge su `main` → build → deploy.
- Security headers: usa `apps/finance-rookie/public/_headers` (Cloudflare Pages).
- Preview deployments: attivi per ogni PR collegata (staging automatico).
