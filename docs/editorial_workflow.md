# Editorial Workflow (GitOps) — “Publish in 60s”

## Flusso (60s)
1. **LLM genera JSON** secondo il contratto (slug opzionale: se manca, viene derivato dal titolo).
2. **Import**
   ```bash
   python packages/scripts/fr_cli.py import-json --input path/to/article.json
   ```
   (alias) `python packages/scripts/fr_cli.py new-from-json --input path/to/article.json`
3. **Publish JSON (opzionale)**
   ```bash
   python packages/scripts/fr_cli.py publish-json --input path/to/article.json
   ```
4. **Validate**
   ```bash
   python packages/scripts/fr_cli.py validate
   ```
5. **Open PR**
   ```bash
   python packages/scripts/fr_cli.py open-pr <slug>
   ```
6. **Merge PR → Deploy**
   - Merge su `main` → Cloudflare Pages build automatico.

## Ingest automatico via GitHub Actions
- Carica JSON in `content/inbox/` e fai push.
- Il workflow `content_ingest.yml` genera i Markdown, sposta i JSON in `content/processed/` e apre una PR.

## Esempio JSON (minimo)
```json
{
  "title": "Tassi BCE: cosa cambia per i risparmiatori",
  "excerpt": "La BCE lascia i tassi fermi: cosa significa per mutui e conti.",
  "category": "analisi",
  "tags": ["tassi", "bce", "mutui"],
  "author_id": "redazione",
  "status": "draft",
  "published_at": "2024-10-12",
  "hero_image": "/images/hero-analisi.svg",
  "hero_alt": "Grafico dei tassi",
  "takeaways": [
    "La BCE mantiene i tassi, ma i mutui restano più cari.",
    "Le banche aggiornano l’offerta nei prossimi 30-60 giorni."
  ],
  "sources": [
    {
      "title": "ECB Monetary Policy Statement",
      "url": "https://www.ecb.europa.eu/press/pr/date/2024/html/index.en.html",
      "publisher": "ECB",
      "date": "2024-10-12"
    }
  ]
}
```

## Regole editoriali
- Contenuti originali, con **Fonti & Metodologia** obbligatori.
- `status` = `draft|review|published`.
- `published_at` richiesto per pubblicati.
- Nessun backend: solo markdown versionato.
