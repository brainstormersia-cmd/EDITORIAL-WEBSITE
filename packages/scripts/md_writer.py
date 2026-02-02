from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict

import yaml


def slugify(value: str) -> str:
    return (
        value.lower()
        .strip()
        .replace("’", "")
        .replace("'", "")
        .replace(":", "")
        .replace(",", "")
        .replace(".", "")
        .replace(" ", "-")
    )


def build_frontmatter(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": payload["title"],
        "excerpt": payload["excerpt"],
        "category": payload["category"],
        "tags": payload.get("tags", [])[:8],
        "author_id": payload["author_id"],
        "status": payload.get("status", "draft"),
        "published_at": payload.get("published_at"),
        "updated_at": payload.get("updated_at"),
        "hero_image": payload.get("hero_image"),
        "hero_alt": payload.get("hero_alt"),
        "hero_caption": payload.get("hero_caption"),
        "hero_source": payload.get("hero_source"),
        "takeaways": payload.get("takeaways"),
        "impact": payload.get("impact"),
        "do_now": payload.get("do_now"),
        "rookie_lens": payload.get("rookie_lens"),
        "sources": payload.get("sources", []),
        "methodology_note": payload.get("methodology_note"),
        "featured": payload.get("featured"),
    }


def write_markdown(payload: Dict[str, Any], destination: Path) -> Path:
    frontmatter = build_frontmatter(payload)
    body = payload.get("body_md", "").strip()
    yaml_block = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    content = f"---\n{yaml_block}\n---\n\n{body}\n"
    destination.write_text(content, encoding="utf-8")
    return destination


def now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
