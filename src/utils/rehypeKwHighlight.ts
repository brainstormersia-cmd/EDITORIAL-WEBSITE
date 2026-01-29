import type { Root, Text, Parent } from "hast";
import { visit } from "unist-util-visit";

const KW_REGEX = /\[\[kw:([^\]]+)\]\]/g;

export default function rehypeKwHighlight() {
  return (tree: Root) => {
    visit(tree, "text", (node: Text, index, parent: Parent | undefined) => {
      if (index === undefined || !parent) return;
      const value = node.value;
      if (!KW_REGEX.test(value)) return;

      KW_REGEX.lastIndex = 0;
      const parts: Array<Text | { type: "element"; tagName: "span"; properties: { className: string[] }; children: Text[] }> = [];
      let lastIndex = 0;
      let match: RegExpExecArray | null;

      while ((match = KW_REGEX.exec(value))) {
        const [fullMatch, keyword] = match;
        const start = match.index;
        const end = start + fullMatch.length;

        if (start > lastIndex) {
          parts.push({ type: "text", value: value.slice(lastIndex, start) });
        }

        parts.push({
          type: "element",
          tagName: "span",
          properties: { className: ["kw"] },
          children: [{ type: "text", value: keyword.trim() }]
        });

        lastIndex = end;
      }

      if (lastIndex < value.length) {
        parts.push({ type: "text", value: value.slice(lastIndex) });
      }

      parent.children.splice(index, 1, ...parts);
      return index + parts.length;
    });
  };
}
