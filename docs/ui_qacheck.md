# Alignment QA checklist (one left edge)

1. **Allineamento**: container e grid sono token-driven (`--container-pad`, `--grid-gap`), niente padding ad hoc.
2. **Logo left-edge**: la “F” del logo allinea il bordo sinistro con hero, cards e article.
3. **Header baseline**: logo, nav e search sono allineati sulla stessa linea orizzontale senza micro-shift.
4. **Tipografia**: H1/H2 e dek rispettano gerarchie e line-height (`--lh-tight`, `--lh-body`).
5. **Prose width**: max-width coerente (non oltre `--prose-max`).
6. **Hero**: titolo, dek e CTA iniziano dallo stesso x del logo.
7. **Cards**: titolo card e kicker allineati al bordo sinistro del container.
8. **Collapsible**: un solo pattern UI condiviso (TOC/Takeaways/Sources), mai invasivo.
9. **Accessibilità**: focus visibile, aria-label sulle icone, contrasto sufficiente.
10. **Performance**: immagini lazy, niente JS superfluo, niente overlay/sticky che coprono testo.
