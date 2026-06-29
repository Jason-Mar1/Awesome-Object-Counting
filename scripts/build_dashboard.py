import json
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'papers.json'
SOTA = ROOT / 'data' / 'sota_seed.json'
RULES = ROOT / 'data' / 'intelligence_rules.json'
TIMELINE = ROOT / 'data' / 'method_timeline.json'
OUT = ROOT / 'docs' / 'radar' / 'data'
OUT.mkdir(parents=True, exist_ok=True)


def load(path):
    return json.loads(path.read_text()) if path.exists() else {}


def safe_rules(rules):
    return {
        'weights': rules.get('weights', {}),
        'frontier_topics': rules.get('frontier_topics', {}),
        'benchmark_keywords': rules.get('benchmark_keywords', []),
        'code_keywords': rules.get('code_keywords', []),
        'sota_keywords': rules.get('sota_keywords', [])
    }


def text_of(paper):
    return (paper.get('title','') + ' ' + paper.get('abstract','') + ' ' + paper.get('url','')).lower()


def score(paper, rules):
    rules = safe_rules(rules)
    weights = rules['weights']
    text = text_of(paper)
    value = 0

    if paper.get('year', 0) >= 2025:
        value += weights.get('recency', 0)
    if paper.get('cited_by_count', 0) > 0:
        value += weights.get('citation', 0)
    if any(k in text for k in rules['benchmark_keywords']):
        value += weights.get('benchmark_presence', 0)
    if any(k in text for k in rules['code_keywords']):
        value += weights.get('code_signal', 0)
    if any(k in text for k in rules['sota_keywords']):
        value += weights.get('sota_signal', 0)

    topic_hits = []
    for topic, keywords in rules['frontier_topics'].items():
        if any(k in text for k in keywords):
            topic_hits.append(topic)
    if topic_hits:
        value += weights.get('frontier_topic', 0)

    paper['frontier_topics'] = topic_hits
    return value


def build_live_feed(papers):
    live = sorted(papers, key=lambda p: (p.get('year', 0), p.get('score', 0)), reverse=True)[:25]
    return [
        {
            'title': p.get('title',''),
            'year': p.get('year'),
            'score': p.get('score', 0),
            'category': p.get('category',''),
            'url': p.get('url') or p.get('paper_url') or p.get('openalex_url') or '',
            'why_live': explain(p)
        }
        for p in live
    ]


def explain(paper):
    reasons = []
    if paper.get('year', 0) >= 2025:
        reasons.append('recent')
    if paper.get('frontier_topics'):
        reasons.append('frontier topic')
    if paper.get('score', 0) >= 40:
        reasons.append('high intelligence score')
    if not reasons:
        reasons.append('tracked paper')
    return ', '.join(reasons)


def build_digest(papers):
    return [
        {
            'title': p.get('title',''),
            'reason': explain(p),
            'score': p.get('score', 0)
        }
        for p in sorted(papers, key=lambda x: x.get('score', 0), reverse=True)[:8]
    ]


def build_hot_topics(papers):
    topics = Counter()
    for p in papers:
        for t in p.get('frontier_topics', []):
            topics[t] += 1
    return [{'topic': k, 'count': v} for k, v in topics.most_common(10)]


def build_graph(papers):
    nodes = []
    links = []
    seen = set()
    for p in sorted(papers, key=lambda x: x.get('score', 0), reverse=True)[:30]:
        pid = 'paper_' + str(p.get('id'))
        if pid not in seen:
            nodes.append({'id': pid, 'label': p.get('title','')[:48], 'type': 'paper'})
            seen.add(pid)
        for topic in p.get('frontier_topics', []):
            tid = 'topic_' + topic
            if tid not in seen:
                nodes.append({'id': tid, 'label': topic, 'type': 'topic'})
                seen.add(tid)
            links.append({'source': pid, 'target': tid})
    return {'nodes': nodes, 'links': links}


def main():
    data = load(DATA)
    rules = load(RULES)
    sota = load(SOTA)
    timeline = load(TIMELINE)

    papers = data.get('papers', [])
    for idx, paper in enumerate(papers):
        paper['id'] = idx
        paper['score'] = score(paper, rules)

    papers_by_score = sorted(papers, key=lambda x: x.get('score', 0), reverse=True)
    papers_by_year = sorted(papers, key=lambda x: x.get('year', 0), reverse=True)
    papers_by_citation = sorted(papers, key=lambda x: x.get('cited_by_count', 0), reverse=True)

    years = Counter(p.get('year', 0) for p in papers)
    categories = Counter(p.get('category', 'unknown') for p in papers)

    dashboard = {
        'generated_at': data.get('generated_at_utc') or datetime.now(timezone.utc).isoformat(),
        'live_status': {
            'mode': 'scheduled-live',
            'refresh_cadence': 'every 6 hours via GitHub Actions',
            'paper_count': len(papers)
        },
        'stats': {
            'total': len(papers),
            'categories': len(categories),
            'hot_topics': len(build_hot_topics(papers))
        },
        'rankings': {
            'top_score': papers_by_score[:10],
            'top_recent': papers_by_year[:10],
            'top_cited': papers_by_citation[:10]
        },
        'live_feed': build_live_feed(papers),
        'daily_digest': build_digest(papers),
        'hot_topics': build_hot_topics(papers),
        'trends': {
            'years': [{'x': k, 'y': v} for k, v in sorted(years.items())],
            'categories': [{'x': k, 'y': v} for k, v in categories.most_common(12)]
        },
        'graph': build_graph(papers),
        'sota': sota,
        'timeline': timeline
    }

    (OUT / 'dashboard.json').write_text(json.dumps(dashboard, ensure_ascii=False, indent=2))
    (OUT / 'live_feed.json').write_text(json.dumps(dashboard['live_feed'], ensure_ascii=False, indent=2))
    (OUT / 'daily_digest.json').write_text(json.dumps(dashboard['daily_digest'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
