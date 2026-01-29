import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";
import sitemap from "@astrojs/sitemap";
import { SITE_CONFIG } from "./src/consts";
import rehypeKwHighlight from "./src/utils/rehypeKwHighlight";

export default defineConfig({
  site: SITE_CONFIG.siteUrl,
  output: "static",
  integrations: [tailwind(), sitemap()],
  markdown: {
    rehypePlugins: [rehypeKwHighlight]
  }
});
