import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import { SITE_CONFIG } from "../consts";

export async function GET() {
  const posts = await getCollection("articles");
  return rss({
    title: SITE_CONFIG.name,
    description: SITE_CONFIG.description,
    site: SITE_CONFIG.siteUrl,
    items: posts
      .filter((post) => !post.data.draft)
      .map((post) => ({
        title: post.data.title,
        pubDate: post.data.date,
        description: post.data.dek,
        link: `/article/${post.slug}`
      }))
  });
}
