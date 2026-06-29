async function load(){
  const res = await fetch('./data/dashboard.json');
  const d = await res.json();

  document.getElementById('generatedAt').innerText = d.generated_at || '--';

  document.getElementById('stats').innerHTML = `
    <div class='badge'>Total: ${d.stats.total}</div>
    <div class='badge'>Categories: ${d.stats.categories}</div>
    <div class='badge'>SOTA entries: ${countSota(d.sota || {})}</div>
    <div class='badge'>Timeline: ${(d.timeline && d.timeline.timeline || []).length}</div>
  `;

  renderRanking('topScore', d.rankings.top_score || []);
  renderRanking('topCited', d.rankings.top_cited || []);
  renderRanking('topRecent', d.rankings.top_recent || []);
  renderPapers(d.rankings.top_score || []);
  renderSota(d.sota || {});
  renderTimeline(d.timeline || {});
  renderDigest(d.daily_digest || []);

  const yc = d.trends.years || [];
  new Chart(document.getElementById('yearChart'),{
    type:'line',
    data:{labels: yc.map(x=>x.x), datasets:[{label:'papers', data: yc.map(x=>x.y)}]}
  });

  const cc = d.trends.categories || [];
  if(document.getElementById('categoryChart')){
    new Chart(document.getElementById('categoryChart'),{
      type:'bar',
      data:{labels: cc.map(x=>x.x || x.name), datasets:[{label:'category', data: cc.map(x=>x.y || x.value)}]}
    });
  }

  const root = document.getElementById('graph');
  root.innerHTML = '<pre>' + JSON.stringify(d.graph || {}, null, 2).slice(0,1200) + '</pre>';
}

function renderRanking(id, items){
  const el = document.getElementById(id);
  if(!el) return;
  el.innerHTML = items.map(p=>'<li><b>'+p.title+'</b><br/><small>score '+(p.score||0)+' | '+(p.year||'')+'</small></li>').join('');
}

function renderPapers(items){
  const container = document.getElementById('papers');
  container.innerHTML = items.map(p=>'<div class="card"><b>'+p.title+'</b><div>'+(p.category||'')+' | score '+(p.score||0)+' | '+(p.year||'')+'</div><small>'+((p.abstract||'').slice(0,180))+'</small></div>').join('');
  document.getElementById('count').innerText = items.length;
}

function renderSota(sota){
  const root = ensurePanel('sotaPanel','SOTA Tracking');
  const benches = sota.benchmarks || {};
  root.innerHTML += Object.entries(benches).map(([name,b])=>'<div class="card"><b>'+name+'</b><br/>Metric: '+(b.metric||'')+'<br/>Entries: '+((b.leaderboard||[]).length)+'</div>').join('');
}

function renderTimeline(timeline){
  const root = ensurePanel('timelinePanel','Method Evolution Timeline');
  root.innerHTML += (timeline.timeline || []).map(t=>'<div class="card"><b>'+t.year+'</b> '+t.type+'<br/><small>'+(t.methods||[]).join(' → ')+'</small></div>').join('');
}

function renderDigest(items){
  const root = ensurePanel('digestPanel','Daily Radar Digest');
  root.innerHTML += (items || []).map(x=>'<div class="card"><b>'+x.title+'</b><br/><small>'+x.reason+'</small></div>').join('');
}

function ensurePanel(id,title){
  let el = document.getElementById(id);
  if(!el){
    el = document.createElement('section');
    el.id = id;
    el.className = 'card';
    el.innerHTML = '<h2>'+title+'</h2>';
    document.querySelector('main').appendChild(el);
  }
  return el;
}

function countSota(sota){
  return Object.values(sota.benchmarks || {}).reduce((a,b)=>a+(b.leaderboard||[]).length,0);
}

load();