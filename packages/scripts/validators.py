from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict, List

import yaml


STATUSES = {"draft", "review", "published"}


def load_site_config(repo_root: Path, site: str) -> Dict[str, Any]:
    config_path = repo_root / "apps" / site / "site.config.json"
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def parse_frontmatter(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise ValueError(f"{path}: frontmatter mancante")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path}: frontmatter non valido")
    frontmatter = yaml.safe_load(parts[1]) or {}
    return frontmatter


def validate_article(frontmatter: Dict[str, Any], categories: List[str]) -> List[str]:
    errors: List[str] = []
    title = frontmatter.get("title", "")
    if not (10 <= len(title) <= 120):
        errors.append("title fuori range 10-120")
    excerpt = frontmatter.get("excerpt", "")
    if not (40 <= len(excerpt) <= 180):
        errors.append("excerpt fuori range 40-180")
    category = frontmatter.get("category")
    if category not in categories:
        errors.append("category non valida")
    tags = frontmatter.get("tags", [])
    if len(tags) > 8:
        errors.append("troppe tags (max 8)")
    author_id = frontmatter.get("author_id")
    if not author_id:
        errors.append("author_id mancante")
    status = frontmatter.get("status")
    if status not in STATUSES:
        errors.append("status non valido")
    published_at = frontmatter.get("published_at")
    if status == "published" and not published_at:
        errors.append("published_at richiesto quando status=published")
    sources = frontmatter.get("sources", [])
    if not sources:
        errors.append("sources deve avere almeno 1 elemento")
    return errors


def validate_article_dates(frontmatter: Dict[str, Any]) -> List[str]:
    warnings: List[str] = []
    published_at = frontmatter.get("published_at")
    if published_at:
        try:
            parsed = dt.datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            if parsed > dt.datetime.now(dt.timezone.utc):
                warnings.append("published_at nel futuro (ok per scheduling)")
        except ValueError:
            warnings.append("published_at non è ISO valido")
    return warnings
