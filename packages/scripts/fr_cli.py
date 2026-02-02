from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import typer
import yaml

from md_writer import now_iso, slugify, write_markdown
from validators import load_site_config, parse_frontmatter, validate_article, validate_article_dates


app = typer.Typer(help="FinanceRookie editorial CLI")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def articles_dir(site: str) -> Path:
    return repo_root() / "apps" / site / "src" / "content" / "articles"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_iso_date(value: str) -> str:
    if not value:
        return value
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return f"{value}T00:00:00Z"
    if value.endswith("Z"):
        return value
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except ValueError:
        return value


def normalize_sources(raw_sources: list) -> list:
    if not isinstance(raw_sources, list) or not raw_sources:
        raise typer.BadParameter("sources deve essere una lista con almeno 1 elemento")
    normalized = []
    for source in raw_sources:
        title = source.get("title") or source.get("label")
        url = source.get("url")
        if not title or not url:
            raise typer.BadParameter("sources deve contenere title/label e url")
        normalized.append(
            {
                "title": title,
                "url": url,
                "publisher": source.get("publisher"),
                "date": source.get("date"),
            }
        )
    return normalized


def ensure_takeaways(payload: dict) -> None:
    if payload.get("takeaways"):
        return
    excerpt = payload.get("excerpt", "").strip()
    if excerpt:
        payload["takeaways"] = [excerpt[:160]]
    else:
        payload["takeaways"] = ["Sintesi in arrivo: aggiungi i punti chiave."]


def validate_required_fields(payload: dict, require_published_at: bool) -> None:
    required_fields = ["title", "category", "excerpt", "author_id", "status"]
    if require_published_at:
        required_fields.append("published_at")
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        raise typer.BadParameter(f"Campi obbligatori mancanti: {', '.join(missing)}")


@app.command()
def new(
    title: str,
    site: str = typer.Option("finance-rookie", "--site", help="Site slug"),
):
    """Create a draft markdown with valid frontmatter."""
    config = load_site_config(repo_root(), site)
    slug = slugify(title)
    payload = {
        "title": title,
        "slug": slug,
        "excerpt": "Completa questo estratto (40-180 caratteri).",
        "category": config["categories"][0],
        "tags": [],
        "author_id": config["default_author_id"],
        "status": "draft",
        "sources": [],
        "body_md": "Scrivi qui il contenuto.",
    }
    destination = articles_dir(site) / f"{slug}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(payload, destination)
    typer.echo(f"Draft creato: {destination}")


def collect_json_files(paths: list[Path]) -> list[Path]:
    json_files: list[Path] = []
    for path in paths:
        if path.is_dir():
            json_files.extend(path.glob("*.json"))
        else:
            json_files.append(path)
    return json_files


def ingest_payload(
    payload: dict,
    config: dict,
    destination: Path,
    dry_run: bool,
    validate_only: bool,
    require_published_at: bool,
) -> None:
    payload.setdefault("site", config.get("site", "finance-rookie"))
    payload.setdefault("excerpt", payload.get("excerpt", "")[:180])
    payload.setdefault("author_id", payload.get("author_id", config["default_author_id"]))
    payload.setdefault("status", "draft")
    payload["published_at"] = normalize_iso_date(payload.get("published_at")) if payload.get("published_at") else None
    payload["sources"] = normalize_sources(payload.get("sources", []))
    ensure_takeaways(payload)
    validate_required_fields(payload, require_published_at=require_published_at)
    if validate_only:
        typer.echo(f"Validato: {destination}")
        return
    if dry_run:
        typer.echo(f"Dry-run: {destination}")
        return
    write_markdown(payload, destination)
    typer.echo(f"Creato: {destination}")


@app.command("import-json")
def import_json(
    inputs: list[Path] = typer.Option(..., "--input", help="JSON file(s) or directory"),
    site: str = typer.Option("finance-rookie", "--site", help="Site slug"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not write markdown files"),
    validate_only: bool = typer.Option(False, "--validate-only", help="Only validate JSON payloads"),
):
    """Import JSON output from the content generator and create markdown."""
    config = load_site_config(repo_root(), site)
    json_files = collect_json_files(inputs)
    for json_file in json_files:
        payload = load_json(json_file)
        slug = payload.get("slug") or slugify(payload["title"])
        destination = articles_dir(site) / f"{slug}.md"
        ingest_payload(payload, config, destination, dry_run, validate_only, require_published_at=False)


@app.command("new-from-json")
def new_from_json(
    inputs: list[Path] = typer.Option(..., "--input", help="JSON file(s) or directory"),
    site: str = typer.Option("finance-rookie", "--site", help="Site slug"),
):
    """Alias for import-json (create markdown from generator JSON)."""
    import_json(inputs, site)


@app.command("publish-json")
def publish_json(
    inputs: list[Path] = typer.Option(..., "--input", help="JSON file(s) or directory"),
    site: str = typer.Option("finance-rookie", "--site", help="Site slug"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not write markdown files"),
    validate_only: bool = typer.Option(False, "--validate-only", help="Only validate JSON payloads"),
):
    """Publish JSON by validating required fields and writing markdown."""
    config = load_site_config(repo_root(), site)
    json_files = collect_json_files(inputs)
    for json_file in json_files:
        payload = load_json(json_file)
        payload.setdefault("status", "published")
        if payload.get("status") == "published" and not payload.get("published_at"):
            payload["published_at"] = now_iso()
        slug = payload.get("slug") or slugify(payload["title"])
        destination = articles_dir(site) / f"{slug}.md"
        ingest_payload(payload, config, destination, dry_run, validate_only, require_published_at=True)


@app.command()
def validate(site: str = typer.Option("finance-rookie", "--site", help="Site slug")):
    """Validate frontmatter across all articles."""
    config = load_site_config(repo_root(), site)
    errors_count = 0
    for md_file in articles_dir(site).glob("*.md"):
        frontmatter = parse_frontmatter(md_file)
        errors = validate_article(frontmatter, config["categories"])
        warnings = validate_article_dates(frontmatter)
        if errors:
            errors_count += 1
            typer.echo(f"{md_file} ❌")
            for error in errors:
                typer.echo(f"  - {error}")
        if warnings:
            typer.echo(f"{md_file} ⚠️")
            for warning in warnings:
                typer.echo(f"  - {warning}")
    if errors_count:
        raise typer.Exit(code=1)
    typer.echo("Validazione completata ✅")


@app.command()
def publish(slug: str, site: str = typer.Option("finance-rookie", "--site", help="Site slug")):
    """Publish an article by setting status and published_at."""
    md_file = articles_dir(site) / f"{slug}.md"
    frontmatter = parse_frontmatter(md_file)
    frontmatter["status"] = "published"
    frontmatter["published_at"] = now_iso()
    body = md_file.read_text(encoding="utf-8").split("---", 2)[2].lstrip()
    yaml_block = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    md_file.write_text(f"---\n{yaml_block}\n---\n\n{body}", encoding="utf-8")
    typer.echo(f"Pubblicato: {md_file}")


@app.command()
def schedule(
    slug: str,
    at: str = typer.Option(..., "--at", help="ISO date, es. 2026-02-01T09:00:00Z"),
    site: str = typer.Option("finance-rookie", "--site", help="Site slug"),
):
    """Schedule an article by setting status=published and published_at."""
    md_file = articles_dir(site) / f"{slug}.md"
    frontmatter = parse_frontmatter(md_file)
    frontmatter["status"] = "published"
    frontmatter["published_at"] = at
    body = md_file.read_text(encoding="utf-8").split("---", 2)[2].lstrip()
    yaml_block = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    md_file.write_text(f"---\n{yaml_block}\n---\n\n{body}", encoding="utf-8")
    typer.echo(f"Pianificato: {md_file}")


@app.command("open-pr")
def open_pr(site: str = typer.Option("finance-rookie", "--site", help="Site slug")):
    """Stub for opening a PR via local git + GH CLI."""
    typer.echo("Usa: git checkout -b publish/<slug> && git commit -am 'Publish: <title>'")
    typer.echo("Poi esegui: gh pr create --title \"Publish: <title>\" --body \"Auto-generated\"")


@app.command()
def preview(site: str = typer.Option("finance-rookie", "--site", help="Site slug")):
    """Print preview instructions for the local dev server."""
    typer.echo("npm run dev -w @financerookie/app")
    typer.echo("Apri http://localhost:4321 o /article/<slug>")


if __name__ == "__main__":
    app()
