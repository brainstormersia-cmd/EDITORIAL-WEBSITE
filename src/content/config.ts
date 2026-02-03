import { defineCollection, z } from "astro:content";
import { SITE_CONFIG } from "../../apps/finance-rookie/src/site.config";


const categorySlugs = (SITE_CONFIG.categories?.map((c) => c.slug).filter(Boolean) ?? []) as string[];

// Se non hai categorie in config, non ti blocco la build:
const categorySchema =
  categorySlugs.length > 0
    ? z.enum(categorySlugs as [string, ...string[]])
    : z.string().min(1);

const articles = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string().min(1),
    description: z.string().min(1),

    // accetta "2024-10-02" e lo trasforma in Date
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),

    status: z.enum(["draft", "published"]).default("published"),

    // IMPORTANTE: qui voglio lo slug (es. "notizie"), non "Notizie"
    category: categorySchema,

    tags: z.array(z.string().min(1)).default([]),

    // per ora stringa (poi la trasformiamo in reference authors)
    author: z.string().min(1),

    // path in /public (consigliato per static): "/images/posts/xxx.jpg" oppure "/hero-news.svg"
    mainImage: z.string().optional(),

    // extra (per homepage)
    featured: z.boolean().default(false),
    editorsPick: z.boolean().default(false),
    trendingScore: z.number().optional()
  })
});

export const collections = { articles };
