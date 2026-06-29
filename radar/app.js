async function loadRadar(){
  const status = document.getElementById('status');
  const feed = document.getElementById('feed');
  const digest = document.getElementById('digest');

  try {
    const res = await fetch('./data/dashboard.json?ts=' + Date.now());
    if (!res.ok) throw new Error('dashboard.json not found');
    const d = await res.json();

    const liveFeed = d.live_feed || d.rankings?.top_score || [];
    const dailyDigest = d.daily_digest || [];
    const hotTopics = d.hot_topics || [];

    status.innerHTML = [
      statCard('Papers', d.stats?.total || liveFeed.length || 0),
      statCard('Categories', d.stats?.categories || 0),
      statCard('Hot Topics', hotTopics.length || 0),
      statCard('Updated', shortTime(d.generated_at || 'pending'))
    ].join('');

    feed.innerHTML = liveFeed.length ? liveFeed.map(renderPaper).join('') : emptyState('No live papers yet. Trigger the GitHub Action to build the first live feed.');
    digest.innerHTML = dailyDigest.length ? dailyDigest.map(renderDigest).join('') : emptyState('Daily digest will appear after the next radar build.');

    renderExtraPanel('Hot Topics', hotTopics.map(t => '<span class="tag">' + escapeHtml(t.topic || t.x || t.name) + ' · ' + (t.count || t.y || t.value || 0) + '</span>').join(''));
    renderExtraPanel('SOTA Tracking', renderSota(d.sota || {}));
    renderExtraPanel('Method Timeline', renderTimeline(d.timeline || {}));
  } catch (err) {
    status.innerHTML = statCard('Status', 'Loading failed');
    feed.innerHTML = emptyState('Could not load radar data: ' + escapeHtml(err.message));
    digest.innerHTML = emptyState('Check radar/data/dashboard.json in the repository.');
  }
}

function statCard(label, value){
  return '<article class="stat"><span>' + escapeHtml(label) + '</span><b>' + escapeHtml(String(value)) + '</b></article>';
}

function renderPaper(p){
  const url = p.url || p.paper_url || p.openalex_url || '#';
  const why = p.why_live || p.reason || 'tracked paper';
  return '<article class="paper"><h3><a href="' + escapeAttr(url) + '" target="_blank" rel="noreferrer">' + escapeHtml(p.title || 'Untitled paper') + '</a></h3><p>' + escapeHtml(p.category || 'object counting') + ' · ' + escapeHtml(String(p.year || '')) + ' · score ' + escapeHtml(String(p.score || 0)) + '</p><small>' + escapeHtml(why) + '</small></article>';
}

function renderDigest(x){
  return '<article class="paper compact"><h3>' + escapeHtml(x.title || 'Radar insight') + '</h3><p>' + escapeHtml(x.reason || 'important update') + '</p></article>';
}

function renderExtraPanel(title, html){
  if(!html) return;
  const main = document.querySelector('main');
  let panel = document.getElementById('panel-' + title.toLowerCase().replaceAll(' ', '-'));
  if(!panel){
    panel = document.createElement('section');
    panel.className = 'panel';
    panel.id = 'panel-' + title.toLowerCase().replaceAll(' ', '-');
    panel.innerHTML = '<h2>' + escapeHtml(title) + '</h2><div class="panel-body"></div>';
    main.appendChild(panel);
  }
  panel.querySelector('.panel-body').innerHTML = html;
}

function renderSota(sota){
  const benches = sota.benchmarks || {};
  return Object.entries(benches).map(([name, b]) => '<article class="paper compact"><h3>' + escapeHtml(name) + '</h3><p>Metric: ' + escapeHtml(b.metric || '-') + ' · Entries: ' + ((b.leaderboard || []).length) + '</p></article>').join('');
}

function renderTimeline(timeline){
  return (timeline.timeline || []).map(t => '<article class="paper compact"><h3>' + escapeHtml(String(t.year || '')) + ' · ' + escapeHtml(t.type || '') + '</h3><p>' + escapeHtml((t.methods || []).join(' → ')) + '</p></article>').join('');
}

function emptyState(text){
  return '<div class="empty">' + escapeHtml(text) + '</div>';
}

function shortTime(value){
  if(value === 'pending') return 'pending';
  return String(value).replace('T', ' ').slice(0, 19);
}

function escapeHtml(value){
  return String(value).replace(/[&<>"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));
}

function escapeAttr(value){
  return escapeHtml(value).replace(/'/g, '&#39;');
}

loadRadar();
