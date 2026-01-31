import type { Config } from "tailwindcss";
import typography from "@tailwindcss/typography";

export default {
  content: [
    "./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}",
    "../../packages/theme/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}"
  ],
  theme: {
    container: {
      center: true,
      padding: "1.5rem",
      screens: {
        lg: "72rem"
      }
    },
    extend: {
      colors: {
        bg: "var(--color-bg)",
        fg: "var(--color-fg)",
        accent: "var(--color-accent)",
        muted: "var(--color-muted)",
        border: "var(--color-border)",
        "bg-alt": "var(--color-bg-alt)"
      },
      fontFamily: {
        heading: "var(--font-heading)",
        body: "var(--font-body)"
      }
    }
  },
  plugins: [typography]
} satisfies Config;
