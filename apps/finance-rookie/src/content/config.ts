import { defineCollection } from "astro:content";
import { createArticleSchema } from "@content-schema/index";
import { SITE_CONFIG } from "../site.config";

const articles = defineCollection({
  type: "content",
  schema: createArticleSchema(SITE_CONFIG.categories.map((category) => category.slug))
});

export const collections = { articles };
