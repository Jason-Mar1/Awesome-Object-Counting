const RADAR_ASSET_BASE = new URL('.', document.currentScript ? document.currentScript.src : window.location.href);

async function loadRadar(){
  const status = document.getElementById('status');
  const feed = document.getElementById('feed');
  const digest = document.getElementById('digest');
  const hotTopics = document.getElementById('hotTopics');
  const sotaBody = document.getElementById('sotaPanelBody');
  const timelineBody = document.getElementById('timelinePanelBody');
  const lastUpdated = document.getElementById('lastUpdated');
  if(!status || !feed || !digest) return;

  try {
    const dataUrl = new URL('data/dashboard.json', RADAR_ASSET_BASE);
    dataUrl.searchParams.set('ts', Date.now());
    const res = await fetch(dataUrl.toString());
    if (!res.ok) throw new Error('dashboard.json not found');
    const d = await res.json();

    const liveFeed = d.live_feed || (d.rankings && d.rankings.top_score) || [];
    const dailyDigest = d.daily_digest || [];
    const topics = d.hot_topics || [];
    const total = (d.stats && d.stats.total) || liveFeed.length || 0;
    const updated = shortTime(d.generated_at || 'pending');

    if(lastUpdated) lastUpdated.textContent = 'Last updated: ' + updated + ' · ' + (d.live_status && d.live_status.mode || 'live dashboard');

    status.innerHTML = [
      statCard('Papers tracked', total),
      statCard('Categories', (d.stats && d.stats.categories) || 0),
      statCard('Hot topics', topics.length || 0),
      statCard('Refresh', (d.live_status && d.live_status.refresh_cadence) || 'scheduled')
    ].join('');

    feed.innerHTML = liveFeed.length ? liveFeed.map(renderPaper).join('') : emptyState('No live papers yet. Trigger the GitHub Action to build the first live feed.');
    digest.innerHTML = dailyDigest.length ? dailyDigest.map(renderDigest).join('') : emptyState('Daily digest will appear after the next radar build.');

    if(hotTopics) hotTopics.innerHTML = topics.length ? topics.map(renderTopic).join('') : emptyState('No hot topics yet.');
    if(sotaBody) sotaBody.innerHTML = renderSota(d.sota || {}) || emptyState('No SOTA seeds yet.');
    if(timelineBody) timelineBody.innerHTML = renderTimeline(d.timeline || {}) || emptyState('No timeline data yet.');
  } catch (err) {
    status.innerHTML = statCard('Status', 'Loading failed');
    feed.innerHTML = emptyState('Could not load radar data: ' + err.message);
    digest.innerHTML = emptyState('Check radar/data/dashboard.json in the repository.');
    if(lastUpdated) lastUpdated.textContent = 'Radar data failed to load.';
  }
}

function statCard(label, value){
  return '<article class="stat"><span>' + escapeHtml(label) + '</span><b>' + escapeHtml(String(value)) + '</b></article>';
}

function renderPaper(p){
  const url = p.url || p.paper_url || p.openalex_url || '#';
  const why = p.why_live || p.reason || 'tracked paper';
  const topics = (p.frontier_topics || []).map(t => '<span class="mini-tag">' + escapeHtml(t) + '</span>').join('');
  return '<article class="paper"><div class="paper-meta"><span>' + escapeHtml(p.category || 'object counting') + '</span><span>' + escapeHtml(String(p.year || '')) + '</span><span>score ' + escapeHtml(String(p.score || 0)) + '</span></div><h3><a href="' + escapeAttr(url) + '" target="_blank" rel="noreferrer">' + escapeHtml(p.title || 'Untitled paper') + '</a></h3><p>' + escapeHtml(why) + '</p><div class="mini-tags">' + topics + '</div></article>';
}

function renderDigest(x){
  return '<article class="paper compact"><h3>' + escapeHtml(x.title || 'Radar insight') + '</h3><p>' + escapeHtml(x.reason || 'important update') + '</p></article>';
}

function renderTopic(t){
  return '<span class="tag">' + escapeHtml(t.topic || t.x || t.name || 'topic') + '<b>' + escapeHtml(String(t.count || t.y || t.value || 0)) + '</b></span>';
}

function renderSota(sota){
  const benches = sota.benchmarks || {};
  return Object.entries(benches).map(([name, b]) => {
    const rows = (b.leaderboard || []).map(item => '<li><b>' + escapeHtml(item.method || '-') + '</b><span>' + escapeHtml(String(item.mae || item.score || item.value || '-')) + '</span></li>').join('');
    return '<article class="sota-card"><h3>' + escapeHtml(name) + '</h3><p>Metric: ' + escapeHtml(b.metric || '-') + '</p><ul>' + rows + '</ul></article>';
  }).join('');
}

function renderTimeline(timeline){
  return (timeline.timeline || []).map(t => '<article class="timeline-item"><b>' + escapeHtml(String(t.year || '')) + '</b><div><h3>' + escapeHtml(t.type || '') + '</h3><p>' + escapeHtml((t.methods || []).join(' → ')) + '</p></div></article>').join('');
}

function emptyState(text){return '<div class="empty">' + escapeHtml(text) + '</div>';}
function shortTime(value){if(value === 'pending') return 'pending'; return String(value).replace('T', ' ').slice(0, 19);}
function escapeHtml(value){return String(value).replace(/[&<>"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));}
function escapeAttr(value){return escapeHtml(value).replace(/'/g, '&#39;');}

loadRadar();
