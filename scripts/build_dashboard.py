import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'papers.json'
SOTA = ROOT / 'data' / 'sota_seed.json'
RULES = ROOT / 'data' / 'intelligence_rules.json'
OUT = ROOT / 'docs' / 'radar' / 'data'
OUT.mkdir(parents=True, exist_ok=True)


def load(p):
    return json.loads(p.read_text()) if p.exists() else {}


def score(p, rules):
    text = (p.get('title','') + ' ' + p.get('abstract','')).lower()
    s = 0

    if p.get('year',0) >= 2025:
        s += rules['weights']['recency']

    if p.get('cited_by_count',0) > 0:
        s += rules['weights']['citation']

    if any(k in text for k in rules['benchmark_keywords']):
        s += rules['weights']['benchmark_presence']

    for _, kws in rules['frontier_topics'].items():
        if any(k in text for k in kws):
            s += rules['weights']['frontier_topic']
            break

    return s


def main():
    data = load(DATA)
    rules = load(RULES)
    sota = load(SOTA)

    papers = data.get('papers', [])

    for i,p in enumerate(papers):
        p['id'] = i
        p['score'] = score(p, rules)

    papers_sorted = sorted(papers, key=lambda x: x['score'], reverse=True)

    years = Counter(p.get('year',0) for p in papers)
    cats = Counter(p.get('category','unknown') for p in papers)

    dashboard = {
        'generated_at': data.get('generated_at_utc',''),
        'stats': {
            'total': len(papers),
            'categories': len(cats)
        },
        'rankings': {
            'top_score': papers_sorted[:10],
            'top_recent': sorted(papers, key=lambda x: x.get('year',0), reverse=True)[:10],
            'top_cited': sorted(papers, key=lambda x: x.get('cited_by_count',0), reverse=True)[:10]
        },
        'trends': {
            'years': [{'x':k,'y':v} for k,v in years.items()],
            'categories': [{'x':k,'y':v} for k,v in cats.items()]
        },
        'graph': {'nodes': [], 'links': []},
        'sota': sota
    }

    (OUT / 'dashboard.json').write_text(json.dumps(dashboard, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()