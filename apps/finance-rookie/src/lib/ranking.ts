import type { CollectionEntry } from "astro:content";

type ArticleEntry = CollectionEntry<"articles">;

const getDateValue = (value?: Date) => (value && !Number.isNaN(value.valueOf()) ? value : undefined);

export const getArticleDate = (article: ArticleEntry) => {
  const data = article.data;
  return (
    getDateValue(data.updatedAt) ??
    getDateValue(data.updated_at) ??
    getDateValue(data.published_at) ??
    new Date()
  );
};

export const isPinnedActive = (article: ArticleEntry, now = new Date()) => {
  const pinnedUntil = getDateValue(article.data.pinnedUntil);
  return Boolean(pinnedUntil && pinnedUntil.valueOf() >= now.valueOf());
};

const getFreshnessScore = (date: Date, now: Date) => {
  const daysSince = Math.floor((now.valueOf() - date.valueOf()) / (1000 * 60 * 60 * 24));
  return Math.max(0, 30 - daysSince);
};

export const scoreArticle = (article: ArticleEntry, now = new Date()) => {
  const data = article.data;
  let score = data.priority ?? 0;

  if (data.featured) {
    score += 30;
  }

  if (isPinnedActive(article, now)) {
    score += 50;
  }

  const freshnessDate = getArticleDate(article);
  score += getFreshnessScore(freshnessDate, now);

  if (data.evergreen) {
    score += 10;
  }

  return score;
};

export const rankArticles = (articles: ArticleEntry[], now = new Date()) => {
  return [...articles].sort((a, b) => {
    const scoreDiff = scoreArticle(b, now) - scoreArticle(a, now);
    if (scoreDiff !== 0) {
      return scoreDiff;
    }
    return getArticleDate(b).valueOf() - getArticleDate(a).valueOf();
  });
};

const getDayOfYear = (date: Date) => {
  const start = new Date(Date.UTC(date.getUTCFullYear(), 0, 0));
  const diff = date.valueOf() - start.valueOf();
  return Math.floor(diff / (1000 * 60 * 60 * 24));
};

export const selectHeroArticles = (articles: ArticleEntry[], now = new Date(), size = 3) => {
  const ranked = rankArticles(articles, now);
  const pinned = ranked.filter((article) => isPinnedActive(article, now));
  const pool = (pinned.length ? pinned : ranked).slice(0, Math.max(size, 5));
  const rotationSeed = getDayOfYear(now) * 24 + now.getUTCHours();
  const rotationIndex = pool.length ? rotationSeed % pool.length : 0;
  const primary = pool[rotationIndex] ?? ranked[0];
  const secondary = ranked.filter((article) => article.slug !== primary?.slug).slice(0, size - 1);

  return {
    ranked,
    primary,
    secondary
  };
};
