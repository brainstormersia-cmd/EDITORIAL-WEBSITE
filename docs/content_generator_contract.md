# Content Generator Contract

Il generatore LLM deve emettere JSON con la seguente struttura:

```json
{
  "site": "finance-rookie",
  "slug": "opzionale-se-manca-deriva-dal-titolo",
  "title": "Titolo articolo",
  "excerpt": "Sintesi 40–180 caratteri",
  "category": "finanza",
  "tags": ["tag1", "tag2"],
  "author_id": "redazione",
  "status": "draft",
  "published_at": "2026-02-01T09:00:00Z",
  "hero_image": "/images/hero-finanza.svg",
  "hero_alt": "Descrizione immagine",
  "hero_caption": "Caption breve",
  "hero_source": "https://example.com",
  "takeaways": ["Punto 1", "Punto 2"],
  "impact": "Target",
  "do_now": ["Azione 1", "Azione 2"],
  "rookie_lens": "Nota editoriale",
  "sources": [{ "title": "Fonte", "url": "https://..." }],
  "methodology_note": "Nota opzionale",
  "body_md": "Markdown del contenuto"
}
```

## Regole
- `sources` **obbligatorio** (minimo 1).
- `excerpt` tra 40–180 caratteri.
- `category` deve appartenere al set del sito.
- Se `status = published` → `published_at` obbligatorio.
- `slug` opzionale: se assente, viene derivato dal titolo.
