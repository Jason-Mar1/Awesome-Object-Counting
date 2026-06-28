async function load(){
  const res = await fetch('./data/dashboard.json');
  const d = await res.json();

  document.getElementById('generatedAt').innerText = d.generated_at || '--';

  const papers = d.rankings.top_score.concat([]);
  const all = d.rankings.top_score.concat(d.rankings.top_cited).concat(d.rankings.top_recent);

  document.getElementById('stats').innerHTML = `
    <div class='badge'>Total: ${d.stats.total}</div>
    <div class='badge'>Categories: ${d.stats.categories}</div>
  `;

  // render papers
  const container = document.getElementById('papers');
  const raw = d.rankings.top_score;

  container.innerHTML = raw.map(p=>`
    <div class='card'>
      <b>${p.title}</b>
      <div>${p.category || ''} | score ${p.score || 0} | ${p.year || ''}</div>
    </div>
  `).join('');

  // chart
  const yc = d.trends.years;
  new Chart(document.getElementById('yearChart'),{
    type:'line',
    data:{
      labels: yc.map(x=>x.x),
      datasets:[{label:'papers', data: yc.map(x=>x.y)}]
    }
  });

  // graph
  const g = d.graph;
  const root = document.getElementById('graph');
  root.innerHTML = JSON.stringify(g).slice(0,500);
}

load();