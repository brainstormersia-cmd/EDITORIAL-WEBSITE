import { SITE_CONFIG } from "../site.config";

export function GET() {
  const body = `User-agent: *\nAllow: /\n\nSitemap: ${SITE_CONFIG.siteUrl}/sitemap-index.xml\n`;
  return new Response(body, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8"
    }
  });
}
