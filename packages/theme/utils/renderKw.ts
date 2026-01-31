const KW_REGEX = /\[\[kw:([^\]]+)\]\]/g;

export function renderKw(text: string = ""): string {
  return text.replace(KW_REGEX, (_, keyword) => `<span class="kw">${keyword.trim()}</span>`);
}
