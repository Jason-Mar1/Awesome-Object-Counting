import json
from pathlib import Path
from collections import Counter
import statistics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'papers.json'
BENCH = ROOT / 'data' / 'benchmarks.json'
OUT = ROOT / 'docs' / 'radar' / 'data'
OUT.mkdir(parents=True, exist_ok=True)


def load_json(p):
    return json.loads(p.read_text()) if p.exists() else {}


def safe(papers):
    return papers if isinstance(papers, list) else []


data = load_json(DATA)
bench = load_json(BENCH)

papers = safe(data.get('papers', []))

# normalize
for i, p in enumerate(papers):
    p['score'] = p.get('score', 0) or 0
    p['cited_by_count'] = p.get('cited_by_count', 0) or 0
    p['year'] = p.get('year', 0) or 0
    p['id'] = i


def build_rankings():
    return {
        'top_score': sorted(papers, key=lambda x: x['score'], reverse=True)[:10],
        'top_cited': sorted(papers, key=lambda x: x['cited_by_count'], reverse=True)[:10],
        'top_recent': sorted(papers, key=lambda x: x['year'], reverse=True)[:10],
    }


def build_trends():
    years = Counter(p.get('year', 0) for p in papers)
    cats = Counter(p.get('category', 'unknown') for p in papers)
    return {
        'years': [{'x': k, 'y': v} for k, v in sorted(years.items())],
        'categories': [{'name': k, 'value': v} for k, v in cats.most_common(10)]
    }


def build_graph():
    top = sorted(papers, key=lambda x: x['score'], reverse=True)[:20]
    nodes = []
    links = []
    for p in top:
        pid = f"p{p['id']}"
        nodes.append({'id': pid, 'label': p.get('title','')[:40], 'type': 'paper'})
        for t in (p.get('tags') or []):
            tid = f"t_{t}"
            nodes.append({'id': tid, 'label': t, 'type': 'tag'})
            links.append({'source': pid, 'target': tid})
    return {'nodes': nodes, 'links': links}


dashboard = {
    'generated_at': data.get('generated_at_utc', ''),
    'stats': {
        'total': len(papers),
        'categories': len(set(p.get('category') for p in papers))
    },
    'rankings': build_rankings(),
    'trends': build_trends(),
    'graph': build_graph(),
    'benchmarks': bench
}

(OUT / 'dashboard.json').write_text(json.dumps(dashboard, indent=2, ensure_ascii=False))
print('v2 dashboard built')