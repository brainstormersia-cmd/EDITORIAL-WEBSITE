import { z } from "astro:content";

export const ARTICLE_STATUSES = ["draft", "review", "published"] as const;

export const createArticleSchema = (categories: readonly string[]) =>
  z
    .object({
      title: z.string().min(10).max(120),
      excerpt: z.string().min(40).max(180),
      category: z.enum(categories as [string, ...string[]]),
      tags: z.array(z.string()).max(8),
      author_id: z.string().min(1),
      status: z.enum(ARTICLE_STATUSES),
      published_at: z.string().datetime().optional(),
      updated_at: z.string().datetime().optional(),
      hero_image: z.string().optional(),
      hero_alt: z.string().optional(),
      hero_caption: z.string().optional(),
      hero_source: z.string().url().optional(),
      takeaways: z.array(z.string()).max(3).optional(),
      impact: z.string().optional(),
      do_now: z.array(z.string()).max(2).optional(),
      rookie_lens: z.string().optional(),
      sources: z
        .array(
          z.object({
            title: z.string(),
            url: z.string().url(),
            publisher: z.string().optional(),
            date: z.string().optional()
          })
        )
        .min(1),
      methodology_note: z.string().optional(),
      featured: z.boolean().optional()
    })
    .superRefine((data, ctx) => {
      if (data.status === "published" && !data.published_at) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: "published_at è obbligatorio quando status=published",
          path: ["published_at"]
        });
      }
    });
