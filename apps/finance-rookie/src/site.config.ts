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
  siteUrl: "https://example.pages.dev",
  nav: [
    { label: "Finanza", href: "/category/finanza" },
    { label: "Economia", href: "/category/economia" },
    { label: "Notizie", href: "/category/notizie" },
    { label: "Analisi", href: "/category/analisi" },
    { label: "Trending", href: "/category/trending" }
  ],
  categories: [
    { label: "Finanza", slug: "finanza" },
    { label: "Economia", slug: "economia" },
    { label: "Notizie", slug: "notizie" },
    { label: "Analisi", slug: "analisi" },
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
