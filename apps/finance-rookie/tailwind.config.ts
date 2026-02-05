import type { Config } from "tailwindcss";
import typography from "@tailwindcss/typography";

export default {
  content: [
    "./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}",

    // Theme: limita ai file che contengono markup/classi Tailwind
    "../../packages/theme/components/**/*.{astro,html,js,jsx,ts,tsx}",
    "../../packages/theme/layouts/**/*.{astro,html,js,jsx,ts,tsx}",
    "../../packages/theme/pages/**/*.{astro,html,js,jsx,ts,tsx}",

    // Se nel theme hai markdown con classi (raro), lascia questa:
    "../../packages/theme/content/**/*.{md,mdx}",

    // CSS non serve in content, ma non fa danni se vuoi essere esplicito
    // "../../packages/theme/styles/**/*.css",
  ],
  theme: {
    container: {
      center: true,
      padding: {
        DEFAULT: "1rem",
        md: "1.5rem"
      },
      screens: {
        lg: "75rem"
      },
    },
    extend: {
      colors: {
        bg: "var(--color-bg)",
        fg: "var(--color-fg)",
        accent: "var(--color-accent)",
        muted: "var(--color-muted)",
        border: "var(--color-border)",
        "bg-alt": "var(--color-bg-alt)",
      },
      fontFamily: {
        heading: "var(--font-heading)",
        body: "var(--font-body)",
      },
    },
  },
  plugins: [typography],
} satisfies Config;
