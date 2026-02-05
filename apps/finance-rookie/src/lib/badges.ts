type BadgeVariant = "breaking" | "live" | "recent" | "updated" | "important";

type ArticleData = {
  breaking_until?: Date;
  is_live?: boolean;
  live?: boolean;
  live_started_at?: Date;
  live_ended_at?: Date;
  published_at?: Date;
  updated_at?: Date;
  priority?: number;
};

export type ArticleBadge = {
  label: string;
  variant: BadgeVariant;
};

export const getArticleBadge = (article: { data: ArticleData }): ArticleBadge | null => {
  const now = new Date();
  const data = article?.data ?? {};

  if (data.breaking_until && data.breaking_until > now) {
    return { label: "Breaking", variant: "breaking" };
  }

  const isLive = data.is_live === true || data.live === true || (data.live_started_at && !data.live_ended_at);
  if (isLive) {
    return { label: "Live", variant: "live" };
  }

  if ((data.priority ?? 0) >= 70) {
    return { label: "Importante", variant: "important" };
  }

  if (data.published_at) {
    const publishedDiff = now.valueOf() - data.published_at.valueOf();
    if (publishedDiff <= 60 * 60 * 1000) {
      return { label: "Appena pubblicato", variant: "recent" };
    }
  }

  if (data.updated_at && data.published_at) {
    const updatedDiff = now.valueOf() - data.updated_at.valueOf();
    if (data.updated_at > data.published_at && updatedDiff <= 24 * 60 * 60 * 1000) {
      return { label: "Aggiornato", variant: "updated" };
    }
  }

  return null;
};
