export type KwNode = {
  type: "text" | "mark";
  value: string;
};

const KW_PATTERN = /\[\[kw:(.+?)\]\]/g;

export const renderKw = (text: string = ""): KwNode[] => {
  const nodes: KwNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = KW_PATTERN.exec(text)) !== null) {
    if (match.index > lastIndex) {
      nodes.push({ type: "text", value: text.slice(lastIndex, match.index) });
    }

    const value = match[1]?.trim();
    if (value) {
      nodes.push({ type: "mark", value });
    }

    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    nodes.push({ type: "text", value: text.slice(lastIndex) });
  }

  return nodes;
};
