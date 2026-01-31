import type { ImageMetadata } from "astro";

const images = import.meta.glob<{ default: ImageMetadata }>("../assets/*.{svg,png,jpg,jpeg}", {
  eager: true
});

export function getImageByName(name: string): ImageMetadata | undefined {
  const key = `../assets/${name}`;
  return images[key]?.default;
}
