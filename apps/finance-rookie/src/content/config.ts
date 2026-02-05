import { defineCollection, z } from "astro:content";
import { SITE_CONFIG } from "../site.config";

const ArticleCategorySchema =
  SITE_CONFIG.categories?.length
    ? z.enum(SITE_CONFIG.categories.map(c => c.slug) as [string, ...string[]])
    : z.string();

const articles = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    excerpt: z.string(),
    category: ArticleCategorySchema,
    tags: z.array(z.string()).default([]),

    author_id: z.string(),
    status: z.enum(["draft", "published"]).default("draft"),
    published_at: z.coerce.date(),
    updated_at: z.coerce.date().optional(),
    featured: z.boolean().optional(),
    breaking: z.boolean().optional(),
    breaking_until: z.coerce.date().optional(),
    is_live: z.boolean().optional(),
    live: z.boolean().optional(),
    live_started_at: z.coerce.date().optional(),
    live_ended_at: z.coerce.date().optional(),
    superseded_by: z.string().optional(),
    superseded_by_url: z.string().url().optional(),
    updates: z
      .array(
        z.object({
          title: z.string(),
          slug: z.string().optional(),
          date: z.string().optional()
        })
      )
      .optional(),

    hero_image: z.string().optional(),
    hero_alt: z.string().optional(),
    hero_caption: z.string().optional(),
    hero_source: z.string().url().optional(),

    takeaways: z.array(z.string()).optional(),
    impact: z.string().optional(),
    do_now: z.array(z.string()).optional(),
    rookie_lens: z.string().optional(),

    sources: z.array(
      z.object({
        title: z.string(),
        url: z.string().url(),
        date: z.string().optional(),
        publisher: z.string().optional()
      })
    ).optional()
  })
});

export const collections = { articles };
