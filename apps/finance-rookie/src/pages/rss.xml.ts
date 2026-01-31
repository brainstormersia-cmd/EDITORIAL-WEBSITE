import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import { SITE_CONFIG } from "../site.config";

export async function GET() {
  const posts = await getCollection("articles");
  return rss({
    title: SITE_CONFIG.name,
    description: SITE_CONFIG.description,
    site: SITE_CONFIG.siteUrl,
    items: posts
      .filter((post) => post.data.status === "published")
      .filter((post) => !post.data.published_at || new Date(post.data.published_at) <= new Date())
      .map((post) => ({
        title: post.data.title,
        pubDate: new Date(post.data.published_at ?? new Date()),
        description: post.data.excerpt,
        link: `/article/${post.slug}`
      }))
  });
}
