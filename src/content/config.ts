import { defineCollection, z } from "astro:content";

const articles = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    dek: z.string(),
    date: z.date(),
    category: z.object({
      label: z.string(),
      slug: z.string()
    }),
    author: z.object({
      name: z.string(),
      avatarUrl: z.string()
    }),
    readTime: z.number(),
    heroImage: z.object({
      src: z.string(),
      alt: z.string(),
      caption: z.string(),
      sourceUrl: z.string().url().optional()
    }),
    whyItMatters: z.array(z.string()).max(3),
    impact: z.string(),
    doNow: z.array(z.string()).max(2),
    rookieLens: z.string(),
    keywords: z.array(z.string()),
    sources: z.array(
      z.object({
        title: z.string(),
        url: z.string().url(),
        date: z.string()
      })
    ),
    featured: z.boolean(),
    draft: z.boolean()
  })
});

export const collections = { articles };
