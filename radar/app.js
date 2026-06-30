/* Object Counting Research Radar — front-end controller
 * Pure vanilla JS. Loads dashboard.json (with relative-path fallbacks) and
 * renders every module. Never white-screens: each module has an empty state
 * and the whole load path has an error fallback.
 */
(function () {
  "use strict";

  // Candidate locations for dashboard.json so the same app.js works whether it
  // is served from /, /radar/, /docs/ or /docs/radar/ on GitHub Pages.
  var DATA_CANDIDATES = [
    "data/dashboard.json",
    "radar/data/dashboard.json",
    "./data/dashboard.json",
    "../radar/data/dashboard.json",
  ];

  var state = { feed: [], filtered: [] };

  /* ---------------- utilities ---------------- */
  function $(sel) { return document.querySelector(sel); }

  function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function num(v, fallback) { return (typeof v === "number" && !isNaN(v)) ? v : (fallback || 0); }

  function trendArrow(t) {
    if (t === "up") return '<i class="bi bi-arrow-up-short trend up"></i>';
    if (t === "down") return '<i class="bi bi-arrow-down-short trend down"></i>';
    return '<i class="bi bi-arrow-right-short trend flat"></i>';
  }

  function fmtDate(iso) {
    if (!iso) return "—";
    var d = new Date(iso);
    if (isNaN(d)) return iso;
    return d.toISOString().slice(0, 10);
  }

  function emptyState(msg) { return '<div class="empty">' + escapeHtml(msg) + "</div>"; }

  /* ---------------- data loading ---------------- */
  function tryFetch(idx) {
    if (idx >= DATA_CANDIDATES.length) {
      return Promise.reject(new Error("not-found"));
    }
    return fetch(DATA_CANDIDATES[idx], { cache: "no-store" })
      .then(function (r) {
        if (!r.ok) throw new Error("bad-status");
        return r.json();
      })
      .catch(function () { return tryFetch(idx + 1); });
  }

  function loadRadar() {
    // Prefer data embedded via <script> (works under file:// too).
    if (window.__RADAR_DATA__) {
      try { renderAll(window.__RADAR_DATA__ || {}); return; }
      catch (e) { /* fall through to fetch */ }
    }
    tryFetch(0)
      .then(function (data) { renderAll(data || {}); })
      .catch(function () {
        renderFatal(
          "Radar data is not available yet. Please run the GitHub Action to generate dashboard.json."
        );
      });
  }

  function renderFatal(msg) {
    var feed = $("#feed-list");
    if (feed) feed.innerHTML = '<div class="error">' + escapeHtml(msg) + "</div>";
    // Still render seeded static modules so the page is never blank.
    safe(renderStats, {});
    safe(renderResearchTrends, {});
    safe(renderDigest, []);
    safe(renderHotTopics, []);
    safe(renderVenues, []);
    safe(renderSota, {});
    safe(renderTimeline, {});
    safe(renderDatasets, []);
    safe(renderCategoryDistribution, []);
    safe(renderGraph, {});
    setStatus({});
  }

  function safe(fn, arg) {
    try { fn(arg); } catch (e) { /* never let one module break the page */ }
  }

  /* ---------------- master render ---------------- */
  function renderAll(data) {
    setStatus(data.live_status || {});
    safe(renderStats, data.stats || {});
    state.feed = (data.rankings && data.rankings.top_score) || [];
    state.filtered = state.feed.slice();
    safe(renderFeed, state.filtered);
    safe(renderResearchTrends, data.research_trends || {});
    safe(renderDigest, data.daily_digest || []);
    safe(renderHotTopics, data.hot_topics || []);
    safe(renderVenues, data.venues || []);
    safe(renderSota, data.sota || {});
    safe(renderTimeline, data.timeline || {});
    safe(renderDatasets, data.datasets || []);
    safe(renderCategoryDistribution, data.category_distribution || []);
    safe(renderGraph, data.graph || {});
  }

  /* ---------------- radar status (hero card) ---------------- */
  function setStatus(s) {
    var mode = s.mode || "static";
    var modeHtml = mode === "live"
      ? '<span class="badge-live"><span class="dot"></span>Live</span>'
      : '<span class="badge-seed"><i class="bi bi-database-gear"></i> ' + escapeHtml(mode.charAt(0).toUpperCase() + mode.slice(1)) + "</span>";
    setText("#st-mode", null, modeHtml);
    setText("#st-refresh", s.refresh_cadence || "every 6 hours");
    setText("#st-updated", fmtDate(s.generated_at || s.last_updated));
    setText("#st-count", String(num(s.paper_count, state.feed.length)));
  }

  function setText(sel, text, html) {
    var el = $(sel);
    if (!el) return;
    if (html !== undefined) el.innerHTML = html;
    else el.textContent = text;
  }

  /* ---------------- stats cards ---------------- */
  function renderStats(stats) {
    var cards = [
      { label: "Papers Tracked", icon: "bi-file-earmark-text", num: num(stats.total), note: "arXiv + curated sources" },
      { label: "New This Week", icon: "bi-clock-history", num: num(stats.new_this_week), note: "Recently added" },
      { label: "Categories", icon: "bi-collection", num: num(stats.categories), note: "Method routes covered" },
      { label: "Hot Topics", icon: "bi-fire", num: num(stats.hot_topics), note: "Trending keywords" },
      { label: "SOTA Signals", icon: "bi-trophy", num: num(stats.sota_signals), note: "Possible SOTA claims" },
      { label: "Last Updated", icon: "bi-arrow-clockwise", num: fmtDate(stats.last_updated || stats.generated_at), note: "Most recent build", small: true },
    ];
    var el = $("#stats-grid");
    if (!el) return;
    el.innerHTML = cards.map(function (c) {
      return (
        '<div class="stat">' +
        '<div class="stat-top"><span class="label">' + escapeHtml(c.label) + "</span>" +
        '<i class="bi ' + c.icon + ' stat-icon"></i></div>' +
        '<div class="num' + (c.small ? " small" : "") + '">' + escapeHtml(String(c.num)) + "</div>" +
        '<div class="note">' + escapeHtml(c.note) + "</div>" +
        "</div>"
      );
    }).join("");
  }

  /* ---------------- live feed ---------------- */
  function paperCard(p) {
    var cat = p.category ? '<span class="chip cat">' + escapeHtml(p.category) + "</span>" : "";
    var year = p.year ? '<span class="chip year">' + escapeHtml(String(p.year)) + "</span>" : "";
    var score = (p.score !== undefined && p.score !== null) ? '<span class="chip score">Score ' + escapeHtml(String(p.score)) + "</span>" : "";
    var sota = p.sota_signal && num(p.sota_signal) >= 70 ? '<span class="chip sota"><i class="bi bi-trophy"></i> SOTA signal</span>' : "";
    var aibadge = p.has_summary ? '<span class="chip ai"><i class="bi bi-stars"></i> AI 讲解</span>' : "";
    var pin = p.pinned ? '<span class="chip pin"><i class="bi bi-pin-angle-fill"></i> Featured</span>' : "";
    var venue = p.venue ? '<span class="chip venue" title="' + escapeHtml(p.venue_full || p.venue) + '"><i class="bi bi-mortarboard-fill"></i> ' + escapeHtml(p.venue) + "</span>" : "";
    var authors = (p.authors && p.authors.length)
      ? '<p class="authors">' + escapeHtml(p.authors.slice(0, 4).join(", ")) + (p.authors.length > 4 ? " et al." : "") + "</p>"
      : "";
    var why = p.why_live ? '<p class="why"><b>Why live:</b> ' + escapeHtml(p.why_live) + "</p>" : "";
    var summary = p.abstract_summary ? '<p class="summary">' + escapeHtml(p.abstract_summary) + "</p>" : "";
    var preview = p.summary_preview
      ? '<div class="ai-summary"><div class="ai-label"><i class="bi bi-stars"></i> AI 论文讲解</div>' + escapeHtml(p.summary_preview) + "</div>"
      : "";
    var img = p.image_url
      ? '<img class="paper-img" src="' + escapeHtml(p.image_url) + '" alt="overview" loading="lazy" onerror="this.style.display=\'none\'" />'
      : "";
    var tags = (p.tags || []).map(function (t) { return '<span class="tag">' + escapeHtml(t) + "</span>"; }).join("");
    var tagsHtml = tags ? '<div class="tags">' + tags + "</div>" : "";

    var links = [];
    var paperUrl = p.paper_url || p.url;
    if (paperUrl) links.push('<a href="' + escapeHtml(paperUrl) + '" target="_blank" rel="noopener"><i class="bi bi-file-earmark-text"></i> Paper</a>');
    if (p.code_url) links.push('<a href="' + escapeHtml(p.code_url) + '" target="_blank" rel="noopener"><i class="bi bi-github"></i> Code</a>');
    if (paperUrl) links.push('<a href="' + escapeHtml(paperUrl) + '" target="_blank" rel="noopener"><i class="bi bi-arrow-right-circle"></i> Details</a>');

    return (
      '<article class="paper' + (p.pinned ? " pinned" : "") + '">' +
      img +
      '<div class="meta-row">' + pin + venue + cat + year + score + sota + aibadge + "</div>" +
      "<h3>" + escapeHtml(p.title || "Untitled") + "</h3>" +
      authors + why + summary + preview + tagsHtml +
      '<div class="actions">' + links.join("") + "</div>" +
      "</article>"
    );
  }

  function renderFeed(list) {
    var el = $("#feed-list");
    if (!el) return;
    if (!list || !list.length) {
      el.innerHTML = emptyState(
        "No live papers yet. Trigger the GitHub Action to build the first live feed."
      );
      return;
    }
    el.innerHTML = list.map(paperCard).join("");
  }

  function applyFeedControls() {
    var q = ($("#feed-search") && $("#feed-search").value || "").trim().toLowerCase();
    var sort = ($("#feed-sort") && $("#feed-sort").value) || "score";

    var list = state.feed.filter(function (p) {
      if (!q) return true;
      var hay = [p.title, p.category, (p.tags || []).join(" "), (p.authors || []).join(" "), (p.datasets || []).join(" ")]
        .join(" ").toLowerCase();
      return hay.indexOf(q) !== -1;
    });

    list.sort(function (a, b) {
      // Pinned/featured papers always stay on top, in their pinned order.
      var pa = a.pinned ? (typeof a.pin_order === "number" ? a.pin_order : 0) : 9999;
      var pb = b.pinned ? (typeof b.pin_order === "number" ? b.pin_order : 0) : 9999;
      if (pa !== pb) return pa - pb;
      if (sort === "newest") return num(b.year) - num(a.year);
      if (sort === "sota") return num(b.sota_signal) - num(a.sota_signal);
      if (sort === "recency") return num(b.recency_score) - num(a.recency_score);
      return num(b.score) - num(a.score); // default: score
    });

    state.filtered = list;
    renderFeed(list);
    var meta = $("#feed-meta");
    if (meta) meta.textContent = list.length + " / " + state.feed.length + " papers";
  }

  /* ---------------- research trends ---------------- */
  function renderResearchTrends(rt) {
    rt = rt || {};
    var sEl = $("#trends-summary");
    var lEl = $("#trends-list");
    if (sEl) sEl.textContent = rt.summary || "";
    if (!lEl) return;
    var items = rt.items || [];
    if (!items.length) { lEl.innerHTML = emptyState("No research trends yet."); return; }
    lEl.innerHTML = items.map(function (t) {
      var tags = (t.tags || []).map(function (x) { return '<span class="tag">' + escapeHtml(x) + "</span>"; }).join("");
      return (
        '<div class="trend-card">' +
        '<div class="tc-title">' + escapeHtml(t.title || "") + "</div>" +
        '<div class="tc-detail">' + escapeHtml(t.detail || "") + "</div>" +
        (tags ? '<div class="tags">' + tags + "</div>" : "") +
        "</div>"
      );
    }).join("");
  }

  /* ---------------- daily digest ---------------- */
  function renderDigest(items) {
    var el = $("#digest-list");
    if (!el) return;
    if (!items || !items.length) { el.innerHTML = emptyState("No digest entries yet."); return; }
    el.innerHTML = items.map(function (d) {
      var imp = (d.importance || "low").toLowerCase();
      return (
        '<div class="digest">' +
        '<div class="t">' + escapeHtml(d.title || "") + "</div>" +
        '<div class="r">' + escapeHtml(d.reason || "") + "</div>" +
        '<div class="imp ' + imp + '">' + escapeHtml(imp) + " priority" +
        (d.topic ? " · " + escapeHtml(d.topic) : "") + "</div>" +
        "</div>"
      );
    }).join("");
  }

  /* ---------------- venues ---------------- */
  function renderVenues(items) {
    var el = $("#venues-list");
    if (!el) return;
    if (!items || !items.length) { el.innerHTML = emptyState("No venue data yet."); return; }
    el.innerHTML = items.map(function (v) {
      return (
        '<span class="topic venue-pill"><i class="bi bi-mortarboard-fill"></i> ' + escapeHtml(v.venue || "") +
        '<span class="count">' + escapeHtml(String(num(v.count))) + "</span></span>"
      );
    }).join("");
  }

  /* ---------------- hot topics ---------------- */
  function renderHotTopics(items) {
    var el = $("#topics-list");
    if (!el) return;
    if (!items || !items.length) { el.innerHTML = emptyState("No hot topics detected yet."); return; }
    el.innerHTML = items.map(function (t) {
      return (
        '<span class="topic">' + escapeHtml(t.topic || "") +
        '<span class="count">' + escapeHtml(String(num(t.count))) + "</span>" +
        '<span class="tr">' + trendArrow(t.trend) + "</span>" +
        "</span>"
      );
    }).join("");
  }

  /* ---------------- SOTA tracking ---------------- */
  function renderSota(sota) {
    var el = $("#sota-grid");
    if (!el) return;
    var benches = (sota && sota.benchmarks) || {};
    var names = Object.keys(benches);
    if (!names.length) { el.innerHTML = emptyState("No SOTA records yet."); return; }
    el.innerHTML = names.map(function (name) {
      var b = benches[name] || {};
      var lb = (b.leaderboard || []).map(function (e) {
        var link = e.paper_url && e.paper_url !== "#"
          ? '<a href="' + escapeHtml(e.paper_url) + '" target="_blank" rel="noopener">' + escapeHtml(e.method || "") + "</a>"
          : escapeHtml(e.method || "");
        return '<li><span class="rk"></span>' + link +
          '<span class="m">' + escapeHtml(String(e.score)) + "</span></li>";
      }).join("");
      return (
        '<div class="bench">' +
        '<div class="bh"><h3>' + escapeHtml(name) + "</h3>" +
        '<span class="metric">' + escapeHtml(b.metric || "") + "</span></div>" +
        (lb ? '<ol class="lb">' + lb + "</ol>" : emptyState("No leaderboard entries.")) +
        "</div>"
      );
    }).join("");
  }

  /* ---------------- method timeline ---------------- */
  function renderTimeline(tl) {
    var el = $("#timeline-list");
    if (!el) return;
    var nodes = (tl && (tl.timeline || tl)) || [];
    if (!Array.isArray(nodes)) nodes = [];
    if (!nodes.length) { el.innerHTML = emptyState("No timeline data yet."); return; }
    var maxYear = nodes.reduce(function (m, n) { return Math.max(m, num(n.year)); }, 0);
    el.innerHTML = nodes.map(function (n) {
      var active = num(n.year) === maxYear ? " active" : "";
      var methods = (n.methods || []).join(" → ");
      return (
        '<div class="tl-node' + active + '">' +
        '<div><span class="yr">' + escapeHtml(String(n.year || "")) + '</span> — <span class="ty">' + escapeHtml(n.type || "") + "</span></div>" +
        (methods ? '<div class="ms">' + escapeHtml(methods) + "</div>" : "") +
        (n.summary ? '<div class="sm">' + escapeHtml(n.summary) + "</div>" : "") +
        "</div>"
      );
    }).join("");
  }

  /* ---------------- datasets ---------------- */
  function renderDatasets(items) {
    var el = $("#datasets-grid");
    if (!el) return;
    if (!items || !items.length) { el.innerHTML = emptyState("No dataset records yet."); return; }
    el.innerHTML = items.map(function (d) {
      return (
        '<div class="ds">' +
        '<div class="n">' + escapeHtml(d.name || "") + "</div>" +
        '<div class="meta">' + escapeHtml(d.task || "") + (d.metric ? " · " + escapeHtml(d.metric) : "") + "</div>" +
        '<div class="cnt">' + escapeHtml(String(num(d.paper_count))) + " papers</div>" +
        "</div>"
      );
    }).join("");
  }

  /* ---------------- category distribution ---------------- */
  function renderCategoryDistribution(items) {
    var el = $("#dist-list");
    if (!el) return;
    if (!items || !items.length) { el.innerHTML = emptyState("No category data yet."); return; }
    var max = items.reduce(function (m, c) { return Math.max(m, num(c.count)); }, 1);
    el.innerHTML = items.map(function (c) {
      var pct = Math.round((num(c.count) / max) * 100);
      return (
        '<div class="row">' +
        '<div class="top"><span>' + escapeHtml(c.category || "") + "</span><span>" + escapeHtml(String(num(c.count))) + "</span></div>" +
        '<div class="bar"><span style="width:' + pct + '%"></span></div>' +
        "</div>"
      );
    }).join("");
  }

  /* ---------------- research graph (static paths) ---------------- */
  function renderGraph(graph) {
    var el = $("#graph-list");
    if (!el) return;
    var paths = (graph && graph.paths) || [];
    if (!paths.length) { el.innerHTML = emptyState("No research-graph relations yet."); return; }
    el.innerHTML = paths.map(function (chain) {
      if (!Array.isArray(chain)) return "";
      var parts = chain.map(function (node, i) {
        var type = node.type || "topic";
        var sep = i < chain.length - 1 ? '<span class="garrow">→</span>' : "";
        return '<span class="gnode ' + escapeHtml(type) + '">' + escapeHtml(node.label || "") + "</span>" + sep;
      });
      return '<div class="gpath">' + parts.join("") + "</div>";
    }).join("");
  }

  /* ---------------- theme (light/dark, auto by IP time) ---------------- */
  function setThemeDom(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var icon = document.querySelector("#theme-toggle i");
    if (icon) icon.className = theme === "light" ? "bi bi-sun" : "bi bi-moon-stars";
  }

  function themeForHour(h) {
    return (h >= 6 && h < 18) ? "light" : "dark"; // day = light, night = dark
  }

  function getMode() {
    try { return localStorage.getItem("oc-theme-mode") || "auto"; } catch (e) { return "auto"; }
  }

  // Resolve the current hour at the user's location via their IP, falling back
  // to the browser's local clock if the lookup fails.
  function fetchIpHour() {
    if (!window.fetch) return Promise.resolve(null);
    var controller = ("AbortController" in window) ? new AbortController() : null;
    var opts = controller ? { signal: controller.signal } : {};
    if (controller) setTimeout(function () { controller.abort(); }, 3500);
    return fetch("https://worldtimeapi.org/api/ip", opts)
      .then(function (r) { if (!r.ok) throw new Error("bad"); return r.json(); })
      .then(function (d) {
        // d.datetime is local time at the IP, e.g. "2026-06-30T14:05:01+02:00"
        if (d && typeof d.datetime === "string" && d.datetime.length >= 13) {
          var h = parseInt(d.datetime.slice(11, 13), 10);
          if (!isNaN(h)) return h;
        }
        return null;
      })
      .catch(function () { return null; });
  }

  function applyManual(theme) {
    try {
      localStorage.setItem("oc-theme-mode", "manual");
      localStorage.setItem("oc-theme", theme);
    } catch (e) {}
    setThemeDom(theme);
  }

  function initTheme() {
    var btn = $("#theme-toggle");
    if (btn) {
      btn.addEventListener("click", function () {
        var cur = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
        applyManual(cur === "light" ? "dark" : "light");
      });
    }

    if (getMode() === "manual") {
      var saved = "dark";
      try { saved = localStorage.getItem("oc-theme") || "dark"; } catch (e) {}
      setThemeDom(saved);
      return;
    }

    // Auto mode: apply local-time guess immediately, then refine using IP time.
    setThemeDom(themeForHour(new Date().getHours()));
    fetchIpHour().then(function (h) {
      if (getMode() === "manual") return;        // user toggled meanwhile
      if (h === null) return;                     // keep local-time result
      setThemeDom(themeForHour(h));
    });
  }

  /* ---------------- nav + boot ---------------- */
  function initNav() {
    var toggle = $("#nav-toggle");
    var links = $("#navlinks");
    if (toggle && links) {
      toggle.addEventListener("click", function () { links.classList.toggle("open"); });
      links.addEventListener("click", function (e) {
        if (e.target.tagName === "A") links.classList.remove("open");
      });
    }
    var search = $("#feed-search");
    var sort = $("#feed-sort");
    if (search) search.addEventListener("input", applyFeedControls);
    if (sort) sort.addEventListener("change", applyFeedControls);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    initNav();
    loadRadar();
  });
})();
