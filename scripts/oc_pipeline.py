#!/usr/bin/env python3
"""Self-contained daily pipeline for GitHub Actions.

Fetches recent Object Counting papers from OpenAlex (no API key required) and
rebuilds the frontend dashboard (radar/data/dashboard.json + .js and the docs
mirror). Standard library only.

It does NOT call any paid LLM/image API — that enrichment stays in the local
backend. Any existing AI summaries / images already present in dashboard.json
are PRESERVED across runs (matched by paper title).
"""

import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUTPUTS = [
    os.path.join(ROOT, "radar", "data", "dashboard.json"),
    os.path.join(ROOT, "docs", "radar", "data", "dashboard.json"),
]
PRIMARY = OUTPUTS[0]

OPENALEX_BASE = "https://api.openalex.org/works"
OPENALEX_API_KEY = os.environ.get("OPENALEX_API_KEY", "")
OPENALEX_MAILTO = os.environ.get("OPENALEX_MAILTO", "")
FROM_DATE = os.environ.get("OPENALEX_FROM_DATE", "2022-01-01")

SEARCH_TERMS = [
    "object counting", "class-agnostic counting", "few-shot counting",
    "zero-shot counting", "open-vocabulary counting", "text-guided counting",
]

RELEVANCE_INCLUDE = ["counting", "crowd", "density estimation", "density map"]
RELEVANCE_EXCLUDE = [
    "cross-lingual", "named entity", "machine translation", "speech recognition",
    "language model", "sentiment", "retrieval-augmented", "question answering",
]

PINNED = ["rt-counter", "mambacount", "ovid"]
CURATED_PINNED = {
    "rt-counter": {
        "id": "rt-counter", "title": "RT-Counter: Real-Time Object Counting",
        "abstract": "A real-time object counting framework targeting low-latency, "
                    "high-FPS density estimation for streaming and edge deployment.",
        "authors": [], "year": 2025, "publication_date": "2025-01-01",
        "venue": "arXiv", "concepts": ["real-time", "object counting", "efficiency"],
        "url": "https://arxiv.org/search/?searchtype=all&query=RT-Counter+object+counting",
    },
}

CATEGORY_RULES = [
    ("Open-Vocabulary Counting", ["open-vocabulary", "open vocabulary", "open-world"]),
    ("Zero-Shot Counting", ["zero-shot", "zero shot"]),
    ("Few-Shot Counting", ["few-shot", "few shot", "exemplar", "fsc-147", "class-agnostic"]),
    ("Text-Guided Counting", ["text-guided", "language-guided", "text prompt", "referring"]),
    ("Training-Free Counting", ["training-free", "training free"]),
    ("Remote Sensing Counting", ["remote sensing", "aerial", "satellite", "drone", "uav"]),
    ("Vehicle Counting", ["vehicle", "car counting", "carpk", "traffic"]),
    ("Foundation Model Counting", ["foundation model", "segment anything", "clip", "dino", "llm"]),
    ("Real-Time Counting", ["real-time", "real time", "lightweight", "efficient"]),
    ("Crowd Counting", ["crowd", "pedestrian", "density estimation"]),
]
TOPIC_KEYWORDS = {
    "Mamba": ["mamba", "state space"], "Open-Vocabulary": ["open-vocabulary", "open vocabulary"],
    "Real-Time": ["real-time", "real time", "efficient"], "DINO": ["dino"],
    "SAM": ["segment anything"], "CLIP": ["clip"], "Training-Free": ["training-free"],
    "Few-Shot": ["few-shot", "few shot"], "Zero-Shot": ["zero-shot", "zero shot"],
    "Density Map": ["density map", "density-map"], "Transformer": ["transformer"],
    "Diffusion": ["diffusion"], "Foundation Model": ["foundation model"],
}
BENCHMARKS = ["FSC-147", "CARPK", "ShanghaiTech", "UCF-QNRF", "NWPU-Crowd",
              "JHU-Crowd++", "JHU-Crowd", "DroneCrowd", "VisDrone"]
SOTA_PHRASES = ["state-of-the-art", "state of the art", "sota", "outperform", "surpass", "new benchmark"]
FRONTIER_PHRASES = ["mamba", "state space", "open-vocabulary", "foundation model", "diffusion",
                    "segment anything", "dino", "llm", "zero-shot", "open-world", "real-time"]

VENUE_RULES = [
    (r"pattern analysis and machine intelligence|\btpami\b", "TPAMI"),
    (r"international journal of computer vision|\bijcv\b", "IJCV"),
    (r"transactions on image processing|\btip\b", "TIP"),
    (r"transactions on multimedia|\btmm\b", "TMM"),
    (r"transactions on circuits and systems for video|\btcsvt\b", "TCSVT"),
    (r"computer vision and pattern recognition|\bcvpr\b", "CVPR"),
    (r"international conference on computer vision|\biccv\b", "ICCV"),
    (r"european conference on computer vision|\beccv\b", "ECCV"),
    (r"neural information processing systems|neurips|\bnips\b", "NeurIPS"),
    (r"learning representations|\biclr\b", "ICLR"),
    (r"international conference on machine learning|\bicml\b", "ICML"),
    (r"aaai conference|\baaai\b", "AAAI"),
    (r"winter conference on applications|\bwacv\b", "WACV"),
    (r"british machine vision|\bbmvc\b", "BMVC"),
    (r"acm multimedia|\bacmmm\b", "ACM MM"),
    (r"pattern recognition\b", "Pattern Recognition"),
    (r"neurocomputing", "Neurocomputing"),
]
_REPO_RE = r"zenodo|figshare|dryad|\bssrn\b"
_ARXIV_RE = r"arxiv|cornell university|preprint"


# ---------------- OpenAlex fetch (urllib) ----------------
def _reconstruct_abstract(inv):
    if not inv:
        return ""
    pos = []
    for word, idxs in inv.items():
        for i in idxs:
            pos.append((i, word))
    pos.sort(key=lambda x: x[0])
    return " ".join(w for _, w in pos)


def _short_id(v):
    return (v or "").rstrip("/").rsplit("/", 1)[-1]


def _fetch_term(term, per_page=25):
    filters = ["title.search:%s" % term]
    if FROM_DATE:
        filters.append("from_publication_date:%s" % FROM_DATE)
    params = {"filter": ",".join(filters), "sort": "publication_date:desc", "per-page": per_page}
    if OPENALEX_API_KEY:
        params["api_key"] = OPENALEX_API_KEY
    if OPENALEX_MAILTO:
        params["mailto"] = OPENALEX_MAILTO
    url = OPENALEX_BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "awesome-object-counting-action/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    out = []
    for w in data.get("results", []):
        primary = w.get("primary_location") or {}
        source = primary.get("source") or {}
        out.append({
            "id": _short_id(w.get("id")),
            "title": w.get("display_name") or "Untitled",
            "abstract": _reconstruct_abstract(w.get("abstract_inverted_index")),
            "authors": [(a.get("author") or {}).get("display_name") for a in (w.get("authorships") or []) if (a.get("author") or {}).get("display_name")],
            "year": w.get("publication_year"),
            "publication_date": w.get("publication_date") or "",
            "venue": source.get("display_name") or "",
            "doi": w.get("doi"),
            "url": primary.get("landing_page_url") or w.get("doi") or w.get("id"),
            "concepts": [c.get("display_name") for c in (w.get("concepts") or []) if c.get("display_name")][:8],
        })
    return out


def _is_relevant(p):
    blob = (p.get("title", "") + " " + (p.get("abstract") or "")).lower()
    if not any(k in blob for k in RELEVANCE_INCLUDE):
        return False
    if any(k in blob for k in RELEVANCE_EXCLUDE):
        return False
    return True


def fetch_recent():
    seen, titles = {}, set()
    for term in SEARCH_TERMS:
        try:
            for p in _fetch_term(term):
                tkey = " ".join((p.get("title") or "").lower().split())
                if p["id"] and p["id"] not in seen and tkey not in titles:
                    seen[p["id"]] = p
                    titles.add(tkey)
        except Exception as exc:  # noqa: BLE001
            print("[openalex] term '%s' failed: %s" % (term, exc))
        time.sleep(1)
    papers = [p for p in seen.values() if _is_relevant(p)]
    papers.sort(key=lambda p: p.get("publication_date") or "", reverse=True)
    return papers


# ---------------- dashboard building ----------------
def _blob(p):
    return (p.get("title", "") + " " + (p.get("abstract") or "")).lower()


def _classify(p):
    b = _blob(p)
    for name, kws in CATEGORY_RULES:
        if any(k in b for k in kws):
            return name
    return "Object Counting"


def _topics(b):
    return [t for t, kws in TOPIC_KEYWORDS.items() if any(k in b for k in kws)]


def _benchmarks(b):
    out, seen = [], set()
    for x in BENCHMARKS:
        if x.lower() in b:
            name = "JHU-Crowd++" if x.startswith("JHU") else x
            if name not in seen:
                seen.add(name); out.append(name)
    return out


def _recency(pub):
    try:
        d = datetime.fromisoformat((pub or "")[:10]).replace(tzinfo=timezone.utc)
    except Exception:
        return 55
    age = (datetime.now(timezone.utc) - d).days
    for lim, sc in [(7, 100), (30, 92), (90, 80), (180, 68), (365, 52)]:
        if age <= lim:
            return sc
    return 35


def _venue(p):
    src = (p.get("venue") or "").strip()
    low = src.lower()
    is_ws = "workshop" in low
    for pat, acro in VENUE_RULES:
        if re.search(pat, low):
            if is_ws and acro in ("CVPR", "ICCV", "ECCV", "NeurIPS", "ICLR", "ICML", "AAAI", "WACV"):
                return acro + "W", src or (acro + " Workshop")
            return acro, src or acro
    if not src or re.search(_ARXIV_RE, low):
        return "arXiv", src or "arXiv (preprint)"
    if re.search(_REPO_RE, low):
        return "Repository", src
    return (src if len(src) <= 22 else src[:21].rstrip() + "…"), src


def _pin_rank(title):
    t = (title or "").lower()
    for i, kw in enumerate(PINNED):
        if re.search(r"\b" + re.escape(kw) + r"\b", t):
            return i
    return None


def _trim(text, n):
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "…"


def _score(p):
    b = _blob(p)
    rec = _recency(p.get("publication_date"))
    frontier = min(100, 40 + sum(1 for x in FRONTIER_PHRASES if x in b) * 18)
    sota = min(100, 35 + sum(1 for x in SOTA_PHRASES if x in b) * 22)
    benches = _benchmarks(b)
    bench = min(100, 40 + len(benches) * 20)
    return round(rec * 0.25 + frontier * 0.30 + sota * 0.25 + bench * 0.20), rec, sota, frontier, benches


def _why(rec, sota, frontier, benches):
    bits = []
    if frontier >= 70:
        bits.append("strong frontier signal")
    if sota >= 70:
        bits.append("possible SOTA impact")
    if rec >= 92:
        bits.append("very recent")
    if benches:
        bits.append("evaluated on " + ", ".join(benches[:2]))
    if not bits:
        bits.append("relevant to the object-counting frontier")
    return "High relevance: " + ", ".join(bits) + "."


def _load_existing_enrichment():
    """Map normalized title -> {summary fields, image_url} from current dashboard."""
    enr = {}
    if not os.path.exists(PRIMARY):
        return enr
    try:
        with open(PRIMARY, encoding="utf-8") as f:
            old = json.load(f)
        for p in old.get("rankings", {}).get("top_score", []):
            key = " ".join((p.get("title") or "").lower().split())
            keep = {}
            for k in ("has_summary", "summary_preview", "paper_id", "image_url", "image_size"):
                if p.get(k) is not None:
                    keep[k] = p[k]
            if keep:
                enr[key] = keep
    except Exception as exc:  # noqa: BLE001
        print("[merge] could not read existing dashboard: %s" % exc)
    return enr


def build_feed(papers, enrichment):
    feed = []
    for p in papers:
        score, rec, sota, frontier, benches = _score(p)
        b = _blob(p)
        topics = _topics(b)
        cat = _classify(p)
        tags = list(topics[:3])
        for x in benches[:2]:
            if x not in tags:
                tags.append(x)
        if not tags and p.get("concepts"):
            tags = p["concepts"][:3]
        year = p.get("year")
        if not year and p.get("publication_date"):
            ys = p["publication_date"][:4]
            year = int(ys) if ys.isdigit() else None
        item = {
            "title": p.get("title", "Untitled"), "authors": p.get("authors", []),
            "venue": _venue(p)[0], "venue_full": _venue(p)[1], "year": year,
            "category": cat, "score": score, "recency_score": rec, "sota_signal": sota,
            "url": p.get("url", ""), "paper_url": p.get("url", ""), "code_url": "",
            "why_live": _why(rec, sota, frontier, benches),
            "abstract_summary": _trim(p.get("abstract", ""), 240),
            "tags": tags, "datasets": benches, "benchmarks": benches,
            "_topics": topics, "_pub": p.get("publication_date", ""),
        }
        # Preserve AI summary/image produced earlier by the local backend.
        key = " ".join((item["title"]).lower().split())
        if key in enrichment:
            item.update(enrichment[key])
        rank = _pin_rank(item["title"])
        if rank is not None:
            item["pinned"] = True
            item["pin_order"] = rank
        item["_pin"] = rank if rank is not None else 999
        feed.append(item)
    feed.sort(key=lambda x: (x["_pin"], -x["score"]))
    return feed


def _ensure_pinned(papers):
    hay = " || ".join((p.get("title") or "").lower() for p in papers)
    extra = [CURATED_PINNED[kw] for kw in PINNED
             if kw in CURATED_PINNED and not re.search(r"\b" + re.escape(kw) + r"\b", hay)]
    return papers + extra


def _hot_topics(feed):
    counts = {}
    for p in feed:
        for t in p.get("_topics", []):
            counts[t] = counts.get(t, 0) + 1
    items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:12]
    return [{"topic": t, "count": c, "trend": "up" if c >= 2 else "flat"} for t, c in items]


def _category_distribution(feed):
    counts = {}
    for p in feed:
        counts[p["category"]] = counts.get(p["category"], 0) + 1
    return [{"category": k, "count": v} for k, v in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)]


def _venues(feed):
    counts = {}
    for p in feed:
        counts[p.get("venue") or "arXiv"] = counts.get(p.get("venue") or "arXiv", 0) + 1
    return [{"venue": k, "count": c} for k, c in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:12]]


def _daily_digest(feed, hot):
    out = []
    if hot:
        top = hot[0]
        out.append({"title": top["topic"] + " is trending in object counting",
                    "reason": "%d tracked papers reference %s." % (top["count"], top["topic"]),
                    "topic": top["topic"], "importance": "high",
                    "related_papers": [p["title"] for p in feed if top["topic"] in p.get("_topics", [])][:3]})
    sota = [p for p in feed if p["sota_signal"] >= 70]
    if sota:
        out.append({"title": "New papers claim benchmark improvements",
                    "reason": "%d tracked papers carry SOTA-style language." % len(sota),
                    "topic": "SOTA", "importance": "medium",
                    "related_papers": [p["title"] for p in sota][:3]})
    if feed:
        out.append({"title": "Most notable new read", "reason": feed[0]["why_live"],
                    "topic": feed[0]["category"], "importance": "high", "related_papers": [feed[0]["title"]]})
    return out


def _graph(feed):
    paths = []
    for p in feed[:8]:
        chain = [{"type": "paper", "label": _trim(p["title"], 42)}]
        if p.get("category"):
            chain.append({"type": "method", "label": p["category"]})
        if p.get("datasets"):
            chain.append({"type": "dataset", "label": p["datasets"][0]})
        if p.get("_topics"):
            chain.append({"type": "topic", "label": p["_topics"][0]})
        if len(chain) > 1:
            paths.append(chain)
    return {"paths": paths, "nodes": [], "links": []}


def _research_trends():
    return {
        "summary": ("Object counting is shifting from per-class density regression toward "
                    "general, promptable systems: class-agnostic, few-/zero-shot and "
                    "open-vocabulary counting, vision-language and foundation models, and "
                    "increasingly efficiency / real-time (state-space / Mamba) designs."),
        "items": [
            {"title": "Class-agnostic & exemplar-based counting", "detail": "Counting arbitrary objects from a few exemplars (FSC-147) is now a core setting.", "tags": ["CVPR", "ICCV", "FSC-147"]},
            {"title": "Vision-language & open-vocabulary counting", "detail": "Text prompts and CLIP-style features count novel categories (CLIP-Count, CounTX, OVID).", "tags": ["Open-Vocabulary", "Text-Guided", "CLIP"]},
            {"title": "From few-shot to zero-shot & training-free", "detail": "Reducing reliance on exemplars and annotations is a fast-growing direction.", "tags": ["Few-Shot", "Zero-Shot", "Training-Free"]},
            {"title": "Foundation models as backbones", "detail": "SAM/DINO and large encoders drive detect-and-verify counting (DAVE, CountGD).", "tags": ["SAM", "DINO", "Foundation Model"]},
            {"title": "Efficiency & real-time inference", "detail": "State-space (Mamba) and lightweight designs target high-FPS counting (RT-Counter, MambaCount).", "tags": ["Mamba", "Real-Time", "Efficiency"]},
            {"title": "New domains & robustness", "detail": "Drone/aerial, remote sensing and dense scenes drive multimodal, robust counting.", "tags": ["DroneCrowd", "Remote Sensing", "Robustness"]},
        ],
    }


def _curated_sota():
    return {"benchmarks": {
        "FSC-147": {"metric": "MAE (test)", "leaderboard": [
            {"method": "DAVE", "score": 8.91, "year": 2024, "paper_url": "#", "code_url": "#"},
            {"method": "CACViT", "score": 9.13, "year": 2024, "paper_url": "#", "code_url": "#"},
            {"method": "LOCA", "score": 10.79, "year": 2023, "paper_url": "#", "code_url": "#"},
            {"method": "CounTR", "score": 11.95, "year": 2022, "paper_url": "#", "code_url": "#"}]},
        "CARPK": {"metric": "MAE", "leaderboard": [
            {"method": "BMNet+", "score": 5.76, "year": 2022, "paper_url": "#", "code_url": "#"},
            {"method": "FamNet", "score": 18.19, "year": 2021, "paper_url": "#", "code_url": "#"}]}}}


def _curated_timeline():
    return {"timeline": [
        {"year": 2018, "type": "Class-Agnostic Counting (GMN)", "methods": ["GMN"], "summary": "Generic matching network frames counting as matching to exemplars."},
        {"year": 2021, "type": "Few-Shot Counting (FSC-147)", "methods": ["FamNet"], "summary": "Learning To Count Everything introduces the FSC-147 benchmark."},
        {"year": 2022, "type": "Transformer-based Counting", "methods": ["CounTR", "BMNet+"], "summary": "Transformers improve class-agnostic counting."},
        {"year": 2023, "type": "Vision-Language Counting", "methods": ["CLIP-Count", "CounTX", "LOCA"], "summary": "Text prompts enable language-driven counting."},
        {"year": 2024, "type": "Open-Vocabulary Counting", "methods": ["DAVE", "CACViT", "CountGD"], "summary": "Detect-and-verify and open-vocabulary counting push generality."},
        {"year": 2025, "type": "State Space / Real-Time", "methods": ["MambaCount", "RT-Counter"], "summary": "State-space models and efficient designs target real-time counting."}]}


def _curated_datasets(feed):
    base = [("FSC-147", "few-shot object counting"), ("FSCD-LVIS", "few-shot counting + detection"),
            ("CountBench", "open-vocabulary counting"), ("REC-8K", "referring expression counting"),
            ("CARPK", "vehicle counting"), ("PUCPR+", "vehicle counting")]
    usage = {}
    for p in feed:
        for b in p.get("benchmarks", []):
            usage[b] = usage.get(b, 0) + 1
    out = [{"name": n, "task": t, "metric": "MAE/RMSE", "paper_count": usage.get(n, 0)} for n, t in base]
    out.sort(key=lambda d: d["paper_count"], reverse=True)
    return out


def build_payload(papers, enrichment):
    feed = build_feed(_ensure_pinned(papers), enrichment)
    hot = _hot_topics(feed)
    cat = _category_distribution(feed)
    venues = _venues(feed)
    digest = _daily_digest(feed, hot)
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_week = 0
    for p in feed:
        try:
            if p["_pub"] and datetime.fromisoformat(p["_pub"][:10]).replace(tzinfo=timezone.utc) >= week_ago:
                new_week += 1
        except Exception:
            pass
    sota_signals = sum(1 for p in feed if p["sota_signal"] >= 70)
    generated = datetime.now(timezone.utc).isoformat()
    clean = [{k: v for k, v in p.items() if not k.startswith("_")} for p in feed]
    return {
        "generated_at": generated,
        "live_status": {"mode": "live", "refresh_cadence": "daily via GitHub Actions",
                        "paper_count": len(feed), "generated_at": generated},
        "stats": {"total": len(feed), "new_this_week": new_week, "categories": len(cat),
                  "hot_topics": len(hot), "sota_signals": sota_signals, "last_updated": generated},
        "rankings": {"top_score": clean},
        "research_trends": _research_trends(),
        "daily_digest": digest, "hot_topics": hot, "venues": venues,
        "timeline": _curated_timeline(), "sota": _curated_sota(),
        "datasets": _curated_datasets(feed), "category_distribution": cat, "graph": _graph(feed),
    }


def write_outputs(payload):
    blob = json.dumps(payload, ensure_ascii=False, indent=2)
    for path in OUTPUTS:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(blob)
        js = path[:-5] + ".js" if path.endswith(".json") else path + ".js"
        with open(js, "w", encoding="utf-8") as f:
            f.write("window.__RADAR_DATA__ = " + blob + ";\n")
        print("[dashboard] wrote %d papers -> %s" % (payload["stats"]["total"], path))


def main():
    enrichment = _load_existing_enrichment()
    papers = fetch_recent()
    if not papers and os.path.exists(PRIMARY):
        print("[pipeline] no papers fetched; keeping existing dashboard")
        return
    payload = build_payload(papers, enrichment)
    write_outputs(payload)
    print("Done. papers=%d  preserved_enrichment=%d" % (payload["stats"]["total"], len(enrichment)))


if __name__ == "__main__":
    main()
