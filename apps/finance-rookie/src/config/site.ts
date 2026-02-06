export const SITE_CONFIG = {
  name: "FinanceRookie",
  description: "Finanza ed economia spiegate bene: notizie, analisi e trend per rookie ambiziosi.",
  mainColor: "#BEF264",
  secondaryColor: "#000000",
  logoText: "FinanceRookie",
  logoParts: {
    primary: "Finance",
    accent: "Rookie"
  },
  locale: "it-IT",
  siteUrl: "https://example.pages.dev", // Ricordati di cambiarlo quando vai in produzione

  // 1. NAVIGAZIONE (Cosa appare nel menu in alto)
  // Ho selezionato le più importanti per non affollare il menu
  nav: [
    { label: "Mercati", href: "/category/mercati" },
    { label: "Tech", href: "/category/tech" },
    { label: "Crypto", href: "/category/crypto" },
    { label: "Energia", href: "/category/energia" },
    { label: "Risparmio", href: "/category/risparmio" },
    { label: "Analisi", href: "/category/analisi" }
  ],

  // 2. CATEGORIE (Tutte quelle ammesse dal sistema)
  // Deve includere TUTTO ciò che esce dallo script Python per evitare errori "Invalid enum"
  categories: [
    // --- Categorie generate da DeepSeek ---
    { label: "Mercati", slug: "mercati" },
    { label: "Tech", slug: "tech" },
    { label: "Crypto", slug: "crypto" },
    { label: "Energia", slug: "energia" },
    { label: "Risparmio", slug: "risparmio" },
    { label: "Analisi", slug: "analisi" },

    // --- Categorie Legacy / Geniche (per sicurezza o uso manuale) ---
    { label: "Finanza", slug: "finanza" },
    { label: "Economia", slug: "economia" },
    { label: "Notizie", slug: "notizie" },
    { label: "Trending", slug: "trending" }
  ],
  authors: {
    redazione: {
      name: "Redazione FinanceRookie",
      avatarUrl: "/images/avatar-redazione.svg"
    }
  }
} as const;

export type SiteConfig = typeof SITE_CONFIG;
