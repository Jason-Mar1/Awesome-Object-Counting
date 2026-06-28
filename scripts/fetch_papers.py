#!/usr/bin/env python3
"""Update Awesome-Object-Counting with recent papers.

This script intentionally does not scrape Google Scholar. It uses programmatic
scholarly sources: OpenAlex and arXiv. Set OPENALEX_API_KEY as a GitHub Actions
secret for better OpenAlex quota. The secret may be either the raw key or a full
OpenAlex URL containing an api_key query parameter.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "search_config.json"
DATA_DIR = ROOT / "data"
README_PATH = ROOT / "README.md"
MARKER_START = "<!-- AUTO_PAPERS:START -->"
MARKER_END = "<!-- AUTO_PAPERS:END -->"
USER_AGENT = "Awesome-Object-Counting-Automation/1.0 (https://github.com/Jason-Mar1/Awesome-Object-Counting)"


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def clean(text: Any) -> str:
    if text is None:
        return ""
    return re.sub(r"\s+", " ", html.unescape(str(text))).strip()


def title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", clean(title).lower()).strip()


def md(text: Any) -> str:
    return clean(text).replace("|", "\\|")


def safe_date(value: Any) -> str:
    match = re.search(r"\d{4}-\d{2}-\d{2}", clean(value))
    if match:
        return match.group(0)
    match = re.search(r"\d{4}", clean(value))
    return match.group(0) if match else ""


def http_text(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def http_json(url: str, timeout: int = 30) -> dict[str, Any]:
    return json.loads(http_text(url, timeout=timeout))


def openalex_key_from_env() -> str:
    raw = os.getenv("OPENALEX_API_KEY", "").strip()
    if not raw:
        return ""
    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urllib.parse.urlsplit(raw)
        return dict(urllib.parse.parse_qsl(parsed.query)).get("api_key", "").strip()
    return raw


def mask_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    masked = [(k, "***" if k == "api_key" else v) for k, v in pairs]
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(masked), parsed.fragment))


def reconstruct_abstract(inverted: dict[str, list[int]] | None) -> str:
    if not inverted:
        return ""
    tokens: list[tuple[int, str]] = []
    for token, positions in inverted.items():
        for pos in positions:
            tokens.append((pos, token))
    return " ".join(token for _, token in sorted(tokens))


def openalex_url(query: str, cfg: dict[str, Any]) -> str:
    from_year = int(cfg.get("from_year", 2023))
    params = {
        "search": query,
        "filter": f"from_publication_date:{from_year}-01-01",
        "sort": "publication_date:desc",
        "per_page": str(int(cfg.get("max_results_per_query", 25))),
        "select": "id,doi,title,display_name,publication_year,publication_date,authorships,primary_location,open_access,abstract_inverted_index,cited_by_count,type",
    }
    api_key = openalex_key_from_env()
    if api_key:
        params["api_key"] = api_key
    return "https://api.openalex.org/works?" + urllib.parse.urlencode(params)


def fetch_openalex(query: str, cfg: dict[str, Any], dry_run: bool) -> list[dict[str, Any]]:
    url = openalex_url(query, cfg)
    if dry_run:
        print("[dry-run] OpenAlex:", mask_url(url))
        return []
    try:
        payload = http_json(url)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"[warn] OpenAlex failed for {query!r}: {exc}", file=sys.stderr)
        return []

    out: list[dict[str, Any]] = []
    for item in payload.get("results", []):
        title = clean(item.get("title") or item.get("display_name"))
        if not title:
            continue
        authors = []
        for authorship in item.get("authorships", [])[:12]:
            name = clean((authorship.get("author") or {}).get("display_name"))
            if name:
                authors.append(name)
        primary = item.get("primary_location") or {}
        source = primary.get("source") or {}
        oa = item.get("open_access") or {}
        out.append({
            "title": title,
            "authors": authors,
            "year": item.get("publication_year") or "",
            "date": safe_date(item.get("publication_date")),
            "venue": clean(source.get("display_name")) or clean(item.get("type")) or "OpenAlex",
            "doi": clean(item.get("doi")),
            "arxiv_id": "",
            "url": clean(primary.get("landing_page_url")) or clean(oa.get("oa_url")) or clean(item.get("id")),
            "pdf_url": clean(primary.get("pdf_url")) or clean(oa.get("oa_url")),
            "abstract": clean(reconstruct_abstract(item.get("abstract_inverted_index"))),
            "cited_by_count": item.get("cited_by_count", 0),
            "source_api": "OpenAlex",
            "source_query": query,
        })
    return out


def arxiv_url(query: str, cfg: dict[str, Any]) -> str:
    cats = cfg.get("arxiv_categories", ["cs.CV"])
    cat_query = "+OR+".join(f"cat:{cat}" for cat in cats)
    terms = [w for w in re.split(r"\s+", query.strip()) if w]
    all_terms = "+AND+".join("all:" + urllib.parse.quote(w) for w in terms)
    from_year = int(cfg.get("from_year", 2023))
    date_filter = f"submittedDate:[{from_year}01010000+TO+{now_utc().strftime('%Y%m%d%H%M')} ]".replace(" ", "")
    search_query = f"({all_terms})+AND+({cat_query})+AND+{date_filter}"
    params = {
        "search_query": search_query,
        "start": "0",
        "max_results": str(int(cfg.get("max_results_per_query", 25))),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    return "https://export.arxiv.org/api/query?" + "&".join(f"{k}={v}" for k, v in params.items())


def fetch_arxiv(query: str, cfg: dict[str, Any], dry_run: bool) -> list[dict[str, Any]]:
    url = arxiv_url(query, cfg)
    if dry_run:
        print("[dry-run] arXiv:", url)
        return []
    try:
        text = http_text(url)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"[warn] arXiv failed for {query!r}: {exc}", file=sys.stderr)
        return []
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        print(f"[warn] arXiv parse failed for {query!r}: {exc}", file=sys.stderr)
        return []

    out: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", ns):
        title = clean(entry.findtext("atom:title", default="", namespaces=ns))
        if not title:
            continue
        page_url = clean(entry.findtext("atom:id", default="", namespaces=ns))
        arxiv_id = page_url.rsplit("/", 1)[-1]
        pdf_url = ""
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                pdf_url = link.attrib.get("href", "")
            if link.attrib.get("rel") == "alternate":
                page_url = link.attrib.get("href", page_url)
        published = safe_date(entry.findtext("atom:published", default="", namespaces=ns))
        out.append({
            "title": title,
            "authors": [clean(a.findtext("atom:name", default="", namespaces=ns)) for a in entry.findall("atom:author", ns) if clean(a.findtext("atom:name", default="", namespaces=ns))],
            "year": int(published[:4]) if published[:4].isdigit() else "",
            "date": published,
            "venue": clean(entry.findtext("arxiv:journal_ref", default="", namespaces=ns)) or "arXiv",
            "doi": clean(entry.findtext("arxiv:doi", default="", namespaces=ns)),
            "arxiv_id": arxiv_id,
            "url": page_url,
            "pdf_url": pdf_url,
            "abstract": clean(entry.findtext("atom:summary", default="", namespaces=ns)),
            "cited_by_count": "",
            "source_api": "arXiv",
            "source_query": query,
        })
    return out


def classify(record: dict[str, Any]) -> str:
    text = f"{record.get('title','')} {record.get('abstract','')}".lower()
    if any(k in text for k in ["open-vocabulary", "open vocabulary", "text-guided", "language-guided", "multimodal", "multi-modal", "clip-count", "countgd"]):
        return "Multimodal / Open-Vocabulary"
    if "zero-shot" in text or "zero shot" in text:
        return "Zero-Shot Object Counting"
    if any(k in text for k in ["few-shot", "few shot", "class-agnostic", "class agnostic", "fsc-147", "fsc147"]):
        return "Few-Shot / Class-Agnostic"
    if "dataset" in text or "benchmark" in text:
        return "Dataset / Benchmark"
    return "General Object Counting"


def is_relevant(record: dict[str, Any], keywords: list[str]) -> bool:
    text = f"{record.get('title','')} {record.get('abstract','')}".lower()
    if any(k.lower() in text for k in keywords):
        return True
    return "count" in text and any(anchor in text for anchor in ["object", "few-shot", "zero-shot", "class-agnostic", "open-vocabulary", "text-guided", "clip", "fsc-147"])


def score(record: dict[str, Any], include: list[str], soft_exclude: list[str]) -> int:
    title = record.get("title", "").lower()
    text = f"{record.get('title','')} {record.get('abstract','')}".lower()
    val = 0
    for kw in include:
        kw = kw.lower()
        val += 8 if kw in title else 4 if kw in text else 0
    if "object" in text and "count" in text:
        val += 6
    if any(k in text for k in ["few-shot", "zero-shot", "class-agnostic", "open-vocabulary", "text-guided", "fsc-147"]):
        val += 5
    for kw in soft_exclude:
        kw = kw.lower()
        val -= 6 if kw in title else 3 if kw in text else 0
    return val


def dedupe(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for rec in records:
        doi = clean(rec.get("doi")).lower().replace("https://doi.org/", "")
        arxiv = clean(rec.get("arxiv_id")).lower()
        key = f"doi:{doi}" if doi else f"arxiv:{arxiv}" if arxiv else f"title:{title_key(rec.get('title',''))}"
        if key in {"doi:", "arxiv:", "title:"}:
            continue
        if key not in merged:
            rec = dict(rec)
            rec["sources"] = [rec.get("source_api", "unknown")]
            merged[key] = rec
            continue
        old = merged[key]
        old["sources"] = sorted(set(old.get("sources", [])) | {rec.get("source_api", "unknown")})
        for field in ["doi", "arxiv_id", "url", "pdf_url"]:
            if not old.get(field) and rec.get(field):
                old[field] = rec[field]
        if len(rec.get("abstract", "")) > len(old.get("abstract", "")):
            old["abstract"] = rec.get("abstract", "")
        if old.get("venue") in {"", "arXiv", "OpenAlex", "preprint"} and rec.get("venue"):
            old["venue"] = rec.get("venue")
    return list(merged.values())


def first_author(authors: list[str]) -> str:
    if not authors:
        return ""
    return authors[0] if len(authors) == 1 else f"{authors[0]} et al."


def paper_url(rec: dict[str, Any]) -> str:
    return rec.get("url") or rec.get("pdf_url") or rec.get("doi") or ""


def latest_md(records: list[dict[str, Any]], generated: str, limit: int = 30) -> str:
    lines = [
        "## Latest Auto-Discovered Papers",
        "",
        f"Generated at `{generated}` UTC. Updated automatically from arXiv and OpenAlex; Google Scholar is not scraped.",
        "",
        "| Date | Paper | Category | Venue/Source | Authors | Links |",
        "|---|---|---|---|---|---|",
    ]
    for rec in records[:limit]:
        links = []
        url = paper_url(rec)
        if url:
            links.append(f"[paper]({url})")
        if rec.get("pdf_url") and rec.get("pdf_url") != url:
            links.append(f"[pdf]({rec['pdf_url']})")
        if rec.get("doi"):
            links.append(f"DOI: `{md(str(rec['doi']).replace('https://doi.org/', ''))}`")
        if rec.get("arxiv_id"):
            links.append(f"arXiv: `{md(rec['arxiv_id'])}`")
        lines.append("| {date} | **{title}** | {category} | {venue} | {authors} | {links} |".format(
            date=md(rec.get("date") or rec.get("year") or ""),
            title=md(rec.get("title", "")),
            category=md(rec.get("category", "")),
            venue=md(rec.get("venue", "")),
            authors=md(first_author(rec.get("authors", []))),
            links="<br>".join(links),
        ))
    return "\n".join(lines) + "\n"


def digest_md(records: list[dict[str, Any]], generated: str, limit: int = 50) -> str:
    lines = ["# Object Counting Paper Digest", "", f"Generated at `{generated}` UTC.", "", "> Source: arXiv + OpenAlex metadata search. This is a reading queue, not a peer-reviewed survey.", ""]
    for i, rec in enumerate(records[:limit], 1):
        lines.append(f"## {i}. {rec.get('title', '')}")
        meta = [str(x) for x in [rec.get("date"), rec.get("venue"), rec.get("category")] if x]
        if meta:
            lines.append("**Meta:** " + " · ".join(md(x) for x in meta))
        authors = ", ".join(rec.get("authors", [])[:12])
        if authors:
            lines.append("**Authors:** " + md(authors))
        links = []
        if paper_url(rec):
            links.append(f"[paper]({paper_url(rec)})")
        if rec.get("pdf_url"):
            links.append(f"[pdf]({rec['pdf_url']})")
        if links:
            lines.append("**Links:** " + " · ".join(links))
        abstract = clean(rec.get("abstract", ""))
        if len(abstract) > 700:
            abstract = abstract[:700].rsplit(" ", 1)[0] + "..."
        if abstract:
            lines.append("**Abstract snippet:** " + md(abstract))
        lines.append("")
    return "\n".join(lines)


def write_csv(records: list[dict[str, Any]], path: Path) -> None:
    fields = ["title", "authors", "year", "date", "category", "venue", "doi", "arxiv_id", "url", "pdf_url", "cited_by_count", "score", "sources", "source_query", "abstract"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for rec in records:
            row = {field: rec.get(field, "") for field in fields}
            row["authors"] = "; ".join(rec.get("authors", []))
            row["sources"] = "; ".join(rec.get("sources", []))
            writer.writerow(row)


def update_readme(section: str) -> None:
    content = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else "# Awesome-Object-Counting\n"
    block = f"{MARKER_START}\n{section.strip()}\n{MARKER_END}"
    if MARKER_START in content and MARKER_END in content:
        content = re.sub(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), block, content, flags=re.S)
    else:
        content = content.rstrip() + "\n\n## Automated Paper Updates\n\nThis section is refreshed by GitHub Actions from arXiv and OpenAlex.\n\n" + block + "\n"
    README_PATH.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(CONFIG_PATH))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-openalex", action="store_true")
    parser.add_argument("--skip-arxiv", action="store_true")
    parser.add_argument("--no-readme", action="store_true")
    args = parser.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    all_records: list[dict[str, Any]] = []
    for query in cfg["queries"]:
        if not args.skip_openalex:
            all_records.extend(fetch_openalex(query, cfg, args.dry_run))
        if not args.skip_arxiv:
            all_records.extend(fetch_arxiv(query, cfg, args.dry_run))
            if not args.dry_run:
                time.sleep(3)
    if args.dry_run:
        return 0

    include = cfg.get("include_keywords", [])
    soft_exclude = cfg.get("soft_exclude_keywords", [])
    records = []
    for rec in dedupe(all_records):
        if not is_relevant(rec, include):
            continue
        rec["category"] = classify(rec)
        rec["score"] = score(rec, include, soft_exclude)
        records.append(rec)
    records.sort(key=lambda r: (r.get("date") or str(r.get("year") or ""), int(r.get("score", 0))), reverse=True)
    records = records[: int(cfg.get("keep_top_n", 80))]

    DATA_DIR.mkdir(exist_ok=True)
    generated = now_utc().strftime("%Y-%m-%d %H:%M:%S")
    payload = {"generated_at_utc": generated, "topic": cfg.get("topic", ""), "sources": ["OpenAlex", "arXiv"], "count": len(records), "papers": records}
    (DATA_DIR / "papers.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(records, DATA_DIR / "papers.csv")
    section = latest_md(records, generated)
    (DATA_DIR / "latest.md").write_text(section, encoding="utf-8")
    (DATA_DIR / "paper_digest.md").write_text(digest_md(records, generated), encoding="utf-8")
    if not args.no_readme:
        update_readme(section)
    print(f"Saved {len(records)} papers to {DATA_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
