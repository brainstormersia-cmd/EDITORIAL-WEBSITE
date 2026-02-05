import os
import re
import json
import time
import random
import hashlib
import unicodedata
from pathlib import Path
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Optional, Dict, Any, List, Tuple

from openai import OpenAI

# =========================
# CONFIG
# =========================
INPUT_FOLDER = Path("articoli_estratti/articoli_txt")
OUTPUT_FOLDER = Path("apps/finance-rookie/src/content/articles")

CACHE_FOLDER = Path(".cache_financerookie")
CACHE_FILE = CACHE_FOLDER / "processed.json"

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise RuntimeError("❌ Manca DEEPSEEK_API_KEY nell'env. Esempio: export DEEPSEEK_API_KEY=xxx")

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

MODEL = "deepseek-chat"

# Stile vs affidabilità (scrittura incollante ma controllata)
TEMPERATURE_MAIN = 0.65
TEMPERATURE_RETRY = 0.25
TEMPERATURE_REPAIR = 0.20

# Word range articolo
MIN_WORDS = 320
MAX_WORDS = 420

# Dedup
SIM_THRESHOLD = 0.78

# Rate limiting
SLEEP_BETWEEN_ARTICLES = 1.5  # “pausa di cortesia”
MAX_API_RETRIES = 4  # retry su 429/5xx con backoff


# =========================
# EXCEPTIONS
# =========================
class DeepSeekJSONError(Exception):
    """Errore di parsing/validazione JSON, ma con raw output disponibile."""

    def __init__(self, message: str, raw_output: str):
        super().__init__(message)
        self.raw_output = raw_output


# =========================
# UTILS
# =========================
def now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_text(s: str) -> str:
    s = s or ""
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def slugify(title: str) -> str:
    t = (title or "").strip().lower()
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^a-z0-9\s-]", "", t)
    t = re.sub(r"[\s-]+", "-", t).strip("-")
    t = t[:80] if len(t) > 80 else t
    return t or "articolo"


def yaml_escape(value: str) -> str:
    v = value or ""
    v = v.replace("\\", "\\\\").replace('"', '\\"')
    v = v.replace("\n", " ").replace("\r", " ")
    v = re.sub(r"\s+", " ", v).strip()
    return v


def yaml_list(key: str, items: List[str], indent: int = 0) -> str:
    pad = " " * indent
    out = [f"{pad}{key}:"]
    for it in items:
        out.append(f'{pad}  - "{yaml_escape(it)}"')
    return "\n".join(out)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def extract_first_url(text: str) -> Optional[str]:
    m = re.search(r"(https?://[^\s\]]+)", text)
    if m:
        return m.group(1).strip().rstrip(").,;]")
    return None


def extract_source_name(text: str) -> Optional[str]:
    for pat in [r"SORGENTE\s*:\s*(.+)", r"FONTE\s*:\s*(.+)", r"Fonte\s*:\s*(.+)"]:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            name = re.sub(r"https?://.*", "", name).strip()
            return name[:60] if name else None
    return None


def extract_raw_title(text: str) -> str:
    m = re.search(r"TITOLO\s*:\s*(.*)", text, flags=re.IGNORECASE)
    if m and m.group(1).strip():
        return m.group(1).strip()

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:25]:
        if len(line) < 18:
            continue
        if any(k in line.upper() for k in ["SORGENTE", "FONTE", "HASH", "URL", "AUTORE"]):
            continue
        if "http://" in line or "https://" in line:
            continue
        return line[:140].strip()

    return "Titolo sconosciuto"


def count_words(md: str) -> int:
    tokens = re.findall(r"\b[\wàèìòùÀÈÌÒÙ'-]+\b", md, flags=re.UNICODE)
    return len(tokens)


# =========================
# JSON EXTRACTION / VALIDATION
# =========================
def extract_first_json_object(s: str) -> str:
    """Estrae il primo oggetto JSON { ... } da una stringa con testo attorno."""
    if not s:
        raise ValueError("Empty model output")

    start = s.find("{")
    if start == -1:
        raise ValueError("No '{' found in model output")

    depth = 0
    in_str = False
    esc = False

    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return s[start:i + 1]

    raise ValueError("Unbalanced JSON braces")


ALLOWED_CATEGORIES = {"analisi", "mercati", "crypto", "tech", "risparmio", "energia"}

REQUIRED_KEYS = [
    # SEO
    "slug",
    "focus_keyword",
    "meta_description",
    # Editorial
    "title",
    "excerpt",
    "category",
    "tags",
    "rookie_lens",
    "takeaways",
    "impact",
    "do_now",
    "source_name",
    "source_url",
    "content_body",
]


def validate_article_payload(
    d: Dict[str, Any], fallback_source_name: str, fallback_source_url: Optional[str]
) -> Dict[str, Any]:
    if not isinstance(d, dict):
        raise ValueError("JSON is not an object")

    missing = [k for k in REQUIRED_KEYS if k not in d]
    if missing:
        raise ValueError(f"Missing keys: {missing}")

    # --- SEO ---
    if not isinstance(d["slug"], str) or not d["slug"].strip():
        d["slug"] = slugify(d.get("title", "articolo"))
    d["slug"] = slugify(d["slug"])

    if not isinstance(d["focus_keyword"], str) or not d["focus_keyword"].strip():
        # fallback semplice: prime 3-5 parole del title
        t = normalize_text(str(d.get("title", "")))
        d["focus_keyword"] = " ".join(t.split()[:4]).lower() if t else "finanza"
    d["focus_keyword"] = normalize_text(d["focus_keyword"]).lower()
    # evita keyword troppo lunga
    if len(d["focus_keyword"].split()) > 7:
        d["focus_keyword"] = " ".join(d["focus_keyword"].split()[:7])

    if not isinstance(d["meta_description"], str) or not d["meta_description"].strip():
        d["meta_description"] = normalize_text(str(d.get("excerpt", "")))[:160]
    d["meta_description"] = normalize_text(d["meta_description"])
    # range SERP “buono” (taglio soft, niente loop)
    if len(d["meta_description"]) > 165:
        d["meta_description"] = d["meta_description"][:162].rstrip() + "…"

    # --- Editorial ---
    if not isinstance(d["title"], str) or not d["title"].strip():
        raise ValueError("Invalid title")
    d["title"] = normalize_text(d["title"])
    if len(d["title"]) > 90:
        d["title"] = d["title"][:90]

    if not isinstance(d["excerpt"], str) or not d["excerpt"].strip():
        raise ValueError("Invalid excerpt")
    d["excerpt"] = normalize_text(d["excerpt"])

    cat = (d["category"] or "").strip().lower()
    d["category"] = cat if cat in ALLOWED_CATEGORIES else "analisi"

    if not isinstance(d["tags"], list):
        raise ValueError("tags must be a list")
    d["tags"] = [normalize_text(str(t)).lower() for t in d["tags"] if normalize_text(str(t))][:6]

    if not isinstance(d["takeaways"], list):
        raise ValueError("takeaways must be a list")
    d["takeaways"] = [normalize_text(str(t)) for t in d["takeaways"] if normalize_text(str(t))][:5]

    if not isinstance(d["do_now"], list):
        raise ValueError("do_now must be a list")
    d["do_now"] = [normalize_text(str(t)) for t in d["do_now"] if normalize_text(str(t))][:5]

    for k in ["rookie_lens", "impact"]:
        if not isinstance(d[k], str) or not d[k].strip():
            d[k] = "Non specificato nel testo"
        d[k] = normalize_text(d[k])

    # Fonte: preferisci fallback realistico invece di “Non specificato”
    if not isinstance(d["source_name"], str) or not d["source_name"].strip():
        d["source_name"] = fallback_source_name or "Agenzie / Web"
    d["source_name"] = normalize_text(d["source_name"])

    if d["source_url"] is not None and not isinstance(d["source_url"], str):
        d["source_url"] = None
    if isinstance(d["source_url"], str):
        d["source_url"] = d["source_url"].strip()[:400]
    if not d["source_url"] and fallback_source_url:
        d["source_url"] = fallback_source_url

    if not isinstance(d["content_body"], str) or not d["content_body"].strip():
        raise ValueError("Invalid content_body")
    d["content_body"] = d["content_body"].strip()

    return d


# =========================
# PROMPTS (SEO + Screen Glue)
# =========================
def build_prompt(raw_text: str, filename: str, fallback_source_name: str, fallback_source_url: Optional[str]) -> str:
    fallback_url_str = fallback_source_url if fallback_source_url else "null"

    return f"""
Sei l'Editor-in-Chief di FinanceRookie (Italia). Scrivi per un lettore ambizioso: vuole capire e agire, non “leggere news”.

REGOLE (OBBLIGATORIE):
- Lingua: ITALIANO.
- Usa SOLO info presenti nel TESTO GREZZO. Se un dato non c'è, scrivi “Non specificato nel testo”.
- Vietato inventare numeri, date, dichiarazioni, cause-effetto.
- Output: SOLO JSON valido. Niente testo extra, niente backticks.

STILE “SCREEN GLUE”:
- HOOK iniziale 2-3 frasi: tensione + perché conta.
- Paragrafi corti (1-2 frasi). Ritmo.
- Usa **grassetto** 6-10 volte nel body.
- Inserisci 1 pattern interrupt:
  > ⚡ Una cosa che molti stanno sbagliando: ...
- Sezioni (H2) nell’ordine fisso:
  1) ## Cosa sta succedendo
  2) ## Perché ti riguarda davvero
  3) ## Chi paga il conto (e chi incassa)
  4) ## Cosa fare adesso (senza farsi fregare)
- Lunghezza content_body: {MIN_WORDS}-{MAX_WORDS} parole.

SEO ON-PAGE (OBBLIGATORIO):
- focus_keyword: 2-6 parole (es: "tassi BCE", "spread BTP", "Bitcoin ETF").
- slug: corto, descrittivo, senza stopword inutili (es: "tassi-bce-mutui" non "ecco-cosa-succede-ai-mutui-oggi").
- meta_description: 140-165 caratteri, diversa dall'excerpt, orientata al click SERP (chiaro beneficio/urgenza).

SCHEMA JSON (rigoroso):
{{
  "slug": "slug-ottimizzato",
  "focus_keyword": "keyword principale",
  "meta_description": "Meta description SEO",
  "title": "Titolo magnetico (max 60 char)",
  "excerpt": "Sottotesto potente (max 180 char)",
  "category": "Una sola tra: analisi, mercati, crypto, tech, risparmio, energia",
  "tags": ["tag1","tag2","tag3","tag4"],
  "rookie_lens": "Analogia brillante per un bimbo di 10 anni (1-2 frasi)",
  "takeaways": ["Punto secco 1","Punto secco 2","Punto secco 3"],
  "impact": "Chi viene colpito?",
  "do_now": ["Azione pratica 1 (imperativo)","Azione pratica 2 (imperativo)"],
  "source_name": "Se nel testo non c'è, usa: {fallback_source_name}",
  "source_url": "Se nel testo non c'è, usa: {fallback_url_str}",
  "content_body": "Markdown dell'articolo"
}}

CONTESTO FILE: {filename}

TESTO GREZZO:
{raw_text[:9000]}
""".strip()


def build_retry_prompt(original_prompt: str, reason: str) -> str:
    return f"""
Hai fallito nel produrre JSON valido. Motivo: {reason}

RIPROVA ORA seguendo queste regole:
- Output SOLO JSON valido (un singolo oggetto).
- Nessun testo prima/dopo.
- Rispetta lo schema e le regole "niente invenzioni".

PROMPT ORIGINALE:
{original_prompt}
""".strip()


def build_repair_prompt(bad_output: str, error: str, raw_text_context: str) -> str:
    return f"""
Il testo seguente doveva essere un JSON conforme a uno schema ma è rotto/contaminato.
Errore: {error}

ISTRUZIONI:
- Restituisci SOLO JSON valido.
- Mantieni i contenuti del JSON dove possibile.
- Se manca qualche campo richiesto, aggiungilo con “Non specificato nel testo”.
- NON inventare fatti: se un dettaglio non è nel contesto, usa “Non specificato nel testo”.

OUTPUT ROTTO DA RIPARARE:
{bad_output}

CONTESTO (per evitare invenzioni):
{raw_text_context[:4000]}
""".strip()


def build_resize_prompt(article_json: Dict[str, Any]) -> str:
    return f"""
Hai questo JSON già valido. Devi SOLO modificare "content_body" per stare tra {MIN_WORDS} e {MAX_WORDS} parole,
mantenendo i fatti e lo stile. Non cambiare gli altri campi.

Output: SOLO JSON valido.

JSON:
{json.dumps(article_json, ensure_ascii=False)}
""".strip()


# =========================
# API CALL WRAPPER (retry/backoff)
# =========================
def call_deepseek(messages: List[Dict[str, str]], temperature: float) -> str:
    last_err = None
    for attempt in range(1, MAX_API_RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=temperature,
            )
            return (resp.choices[0].message.content or "")
        except Exception as e:
            last_err = e
            # backoff progressivo con jitter
            sleep_s = (2 ** (attempt - 1)) + random.uniform(0.0, 0.6)
            print(f"⚠️ API error (tentativo {attempt}/{MAX_API_RETRIES}): {e}. Sleep {sleep_s:.2f}s")
            time.sleep(sleep_s)
    raise last_err


# =========================
# PIPELINE: raw -> parse/validate (con error carrying raw)
# =========================
def deepseek_json(prompt: str, fallback_source_name: str, fallback_source_url: Optional[str]) -> Tuple[str, Dict[str, Any]]:
    raw = call_deepseek([{"role": "user", "content": prompt}], temperature=TEMPERATURE_MAIN)

    try:
        obj_text = extract_first_json_object(raw)
        data = json.loads(obj_text)
        data = validate_article_payload(data, fallback_source_name, fallback_source_url)
        return raw, data
    except Exception as e:
        raise DeepSeekJSONError(f"JSON Error: {e}", raw_output=raw)


def deepseek_repair_json(
    bad_output: str,
    error: str,
    raw_text_context: str,
    fallback_source_name: str,
    fallback_source_url: Optional[str],
) -> Dict[str, Any]:
    prompt = build_repair_prompt(bad_output=bad_output, error=error, raw_text_context=raw_text_context)
    raw = call_deepseek([{"role": "user", "content": prompt}], temperature=TEMPERATURE_REPAIR)

    obj_text = extract_first_json_object(raw)
    data = json.loads(obj_text)
    return validate_article_payload(data, fallback_source_name, fallback_source_url)


def deepseek_retry_json(
    original_prompt: str,
    reason: str,
    fallback_source_name: str,
    fallback_source_url: Optional[str],
) -> Tuple[str, Dict[str, Any]]:
    prompt = build_retry_prompt(original_prompt, reason=reason)
    raw = call_deepseek([{"role": "user", "content": prompt}], temperature=TEMPERATURE_RETRY)

    obj_text = extract_first_json_object(raw)
    data = json.loads(obj_text)
    data = validate_article_payload(data, fallback_source_name, fallback_source_url)
    return raw, data


def enforce_word_range(
    data: Dict[str, Any], fallback_source_name: str, fallback_source_url: Optional[str]
) -> Dict[str, Any]:
    wc = count_words(data["content_body"])
    if MIN_WORDS <= wc <= MAX_WORDS:
        return data

    raw = call_deepseek([{"role": "user", "content": build_resize_prompt(data)}], temperature=0.25)
    obj_text = extract_first_json_object(raw)
    resized = json.loads(obj_text)
    return validate_article_payload(resized, fallback_source_name, fallback_source_url)


# =========================
# FRONTMATTER BUILDER (SEO fields inclusi)
# =========================
def build_markdown(data: Dict[str, Any], published_iso: str) -> str:
    tags = data.get("tags", [])
    takeaways = data.get("takeaways", [])
    do_now = data.get("do_now", [])

    source_name = data.get("source_name") or "Agenzie / Web"
    source_url = data.get("source_url") or "https://finance-rookie.com"

    fm_lines = [
        "---",
        f'slug: "{yaml_escape(data["slug"])}"',
        f'focus_keyword: "{yaml_escape(data["focus_keyword"])}"',
        f'meta_description: "{yaml_escape(data["meta_description"])}"',
        f'title: "{yaml_escape(data["title"])}"',
        f'excerpt: "{yaml_escape(data["excerpt"])}"',
        f'category: "{yaml_escape(data["category"])}"',
        yaml_list("tags", tags),
        'author_id: "redazione"',
        'status: "published"',
        f'published_at: "{published_iso}"',
        'hero_image: "/images/hero-finanza.svg"',
        f'hero_alt: "Immagine {yaml_escape(data["category"])}"',
        f'rookie_lens: "{yaml_escape(data["rookie_lens"])}"',
        yaml_list("takeaways", takeaways),
        f'impact: "{yaml_escape(data["impact"])}"',
        yaml_list("do_now", do_now),
        "sources:",
        f'  - title: "{yaml_escape(source_name)}"',
        f'    url: "{yaml_escape(source_url)}"',
        "featured: false",
        "---",
        "",
        data["content_body"].strip(),
        "",
    ]
    return "\n".join(fm_lines)


def unique_output_path(slug: str) -> Path:
    p = OUTPUT_FOLDER / f"{slug}.md"
    if not p.exists():
        return p
    i = 2
    while True:
        p2 = OUTPUT_FOLDER / f"{slug}-{i}.md"
        if not p2.exists():
            return p2
        i += 1


def load_existing_index() -> Dict[str, Any]:
    titles, urls, slugs = [], [], []
    if OUTPUT_FOLDER.exists():
        for md in OUTPUT_FOLDER.glob("*.md"):
            txt = read_text(md)

            mt = re.search(r'^\s*title:\s*"(.*)"\s*$', txt, flags=re.MULTILINE)
            if mt:
                titles.append(mt.group(1))

            ms = re.search(r'^\s*slug:\s*"(.*)"\s*$', txt, flags=re.MULTILINE)
            if ms:
                slugs.append(ms.group(1))

            mu = re.search(r'^\s*url:\s*"(.*)"\s*$', txt, flags=re.MULTILINE)
            if mu:
                urls.append(mu.group(1))
    return {"titles": titles, "urls": urls, "slugs": slugs}


def load_cache() -> Dict[str, Any]:
    CACHE_FOLDER.mkdir(parents=True, exist_ok=True)
    if CACHE_FILE.exists():
        try:
            return json.loads(read_text(CACHE_FILE))
        except Exception:
            return {"seen_hashes": [], "seen_urls": []}
    return {"seen_hashes": [], "seen_urls": []}


def save_cache(cache: Dict[str, Any]) -> None:
    write_text(CACHE_FILE, json.dumps(cache, ensure_ascii=False, indent=2))


def is_duplicate(
    raw_title: str,
    source_url: Optional[str],
    content_hash: str,
    run_titles: List[str],
    existing_index: Dict[str, Any],
    cache: Dict[str, Any],
) -> bool:
    if source_url and (source_url in cache.get("seen_urls", []) or source_url in existing_index.get("urls", [])):
        return True
    if content_hash in cache.get("seen_hashes", []):
        return True

    candidates = run_titles + existing_index.get("titles", [])
    tnorm = normalize_text(raw_title).lower()
    for t in candidates:
        if similarity(tnorm, normalize_text(t).lower()) >= SIM_THRESHOLD:
            return True
    return False


# =========================
# MAIN
# =========================
def main() -> None:
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    files = sorted([p for p in INPUT_FOLDER.glob("*.txt")])
    print(f"📂 Trovati {len(files)} file grezzi in: {INPUT_FOLDER}")

    existing_index = load_existing_index()
    cache = load_cache()
    run_titles: List[str] = []

    published_iso = now_iso_utc()

    for path in files:
        full_text = read_text(path)
        raw_title = extract_raw_title(full_text)

        source_url = extract_first_url(full_text)
        source_name = extract_source_name(full_text) or "Agenzie / Web"

        normalized_body = normalize_text(full_text.lower())
        content_hash = sha256(normalized_body[:12000])

        if is_duplicate(raw_title, source_url, content_hash, run_titles, existing_index, cache):
            print(f"💰 DUP SKIP: '{raw_title[:60]}' ({path.name})")
            continue

        run_titles.append(raw_title)

        prompt = build_prompt(full_text, path.name, source_name, source_url)

        print(f"🔥 DeepSeek scrive: {path.name} | titolo grezzo: {raw_title[:50]}...")

        try:
            _, data = deepseek_json(prompt, fallback_source_name=source_name, fallback_source_url=source_url)

        except DeepSeekJSONError as e:
            print(f"⚠️ JSON FAIL: {e}. Provo REPAIR sul RAW (corretto)...")
            try:
                data = deepseek_repair_json(
                    bad_output=e.raw_output,  # ✅ RAW dell'AI, non full_text
                    error=str(e),
                    raw_text_context=full_text,  # contesto per NON inventare
                    fallback_source_name=source_name,
                    fallback_source_url=source_url,
                )
            except Exception as e2:
                print(f"⚠️ REPAIR FAIL: {e2}. Provo RETRY pulito...")
                try:
                    _, data = deepseek_retry_json(
                        original_prompt=prompt,
                        reason=f"{e} | repair_failed: {e2}",
                        fallback_source_name=source_name,
                        fallback_source_url=source_url,
                    )
                except Exception as e3:
                    print(f"❌ RETRY FAIL ({path.name}): {e3}")
                    continue

        except Exception as e:
            print(f"❌ API/Other FAIL ({path.name}): {e}")
            continue

        # Ensure word range (non loop infinito)
        try:
            data = enforce_word_range(data, fallback_source_name=source_name, fallback_source_url=source_url)
        except Exception as e:
            print(f"⚠️ Resize FAIL: {e} (vado avanti senza resize)")

        md = build_markdown(data, published_iso)

        out_slug = data.get("slug") or slugify(data["title"])
        out_slug = slugify(out_slug)

        out_path = unique_output_path(out_slug)
        write_text(out_path, md)

        # Cache
        if source_url:
            cache.setdefault("seen_urls", []).append(source_url)
        cache.setdefault("seen_hashes", []).append(content_hash)
        save_cache(cache)

        print(f"✨ Creato: {out_path}")

        # Rate limiting courtesy
        time.sleep(SLEEP_BETWEEN_ARTICLES)

    print(f"\n🚀 Fatto. Articoli in: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()
