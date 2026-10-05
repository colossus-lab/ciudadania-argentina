/* Ciudadanía por Inversión — Colossus Lab. Tema, gráficos interactivos y explorador de afirmaciones. */
(function () {
  "use strict";
  var root = document.documentElement;

  // ---------- Tema (oscuro por defecto, como openarg.org) ----------
  function storedTheme() { try { return localStorage.getItem("cxi-theme"); } catch (e) { return null; } }
  function setTheme(t) {
    root.setAttribute("data-theme", t);
    try { localStorage.setItem("cxi-theme", t); } catch (e) { /* sin almacenamiento: no pasa nada */ }
    document.querySelectorAll(".ed-theme-toggle").forEach(function (b) {
      b.setAttribute("aria-label", t === "dark" ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
      b.textContent = t === "dark" ? "☀" : "☾";
    });
    renderCharts();
  }
  function currentTheme() {
    var t = root.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }
  document.addEventListener("DOMContentLoaded", function () {
    var t = storedTheme() || "dark";
    root.setAttribute("data-theme", t);
    document.querySelectorAll(".ed-theme-toggle").forEach(function (b) {
      b.addEventListener("click", function () { setTheme(currentTheme() === "dark" ? "light" : "dark"); });
    });
    setTheme(t);
    initClaims();
    highlightHash();
  });

  // ---------- Gráficos ----------
  var charts = [];
  function css(v) { return getComputedStyle(root).getPropertyValue(v).trim(); }
  var nf = new Intl.NumberFormat("es-AR");
  function baseOptions(yTitle) {
    return {
      responsive: true, maintainAspectRatio: false, animation: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: css("--tooltip-bg"), borderColor: css("--tooltip-border"), borderWidth: 1,
          titleColor: css("--tooltip-text"), bodyColor: css("--tooltip-text"), padding: 10,
          titleFont: { family: "JetBrains Mono", size: 11 }, bodyFont: { family: "Inter", size: 12 },
          callbacks: { label: function (c) { return " " + c.dataset.label + ": " + nf.format(c.parsed.y); } }
        }
      },
      scales: {
        x: { grid: { display: false }, border: { color: css("--ed-rule-strong") },
             ticks: { color: css("--chart-axis"), font: { family: "Inter", size: 11 }, maxRotation: 0, autoSkipPadding: 18 } },
        y: { beginAtZero: true, grid: { color: css("--chart-grid") }, border: { display: false },
             title: { display: !!yTitle, text: yTitle || "", color: css("--chart-axis"), font: { family: "Inter", size: 11 } },
             ticks: { color: css("--chart-axis"), font: { family: "Inter", size: 11 }, callback: function (v) { return nf.format(v); } } }
      }
    };
  }
  var eventLines = {
    id: "eventLines",
    afterDatasetsDraw: function (chart, args, opts) {
      if (!opts || !opts.events) return;
      var ctx = chart.ctx, x = chart.scales.x, area = chart.chartArea;
      ctx.save();
      opts.events.forEach(function (ev, i) {
        var idx = chart.data.labels.indexOf(ev.at);
        if (idx < 0) return;
        var px = x.getPixelForValue(idx);
        ctx.strokeStyle = css("--ed-rule-strong"); ctx.setLineDash([3, 3]); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(px, area.top); ctx.lineTo(px, area.bottom); ctx.stroke();
        ctx.setLineDash([]); ctx.fillStyle = css("--ed-ink-2"); ctx.font = "11px Inter";
        ctx.textAlign = px > area.right - 170 ? "right" : "left";
        ctx.fillText(ev.label, px + (ctx.textAlign === "right" ? -5 : 5), area.top + 12 + i * 15);
      });
      ctx.restore();
    }
  };
  var hLine = {
    id: "hLine",
    afterDatasetsDraw: function (chart, args, opts) {
      if (!opts || opts.value == null) return;
      var y = chart.scales.y.getPixelForValue(opts.value), area = chart.chartArea, ctx = chart.ctx;
      ctx.save(); ctx.strokeStyle = css("--chart-2"); ctx.lineWidth = 2; ctx.setLineDash([6, 4]);
      ctx.beginPath(); ctx.moveTo(area.left, y); ctx.lineTo(area.right, y); ctx.stroke();
      ctx.setLineDash([]); ctx.fillStyle = css("--ed-ink"); ctx.font = "600 11px Inter"; ctx.textAlign = "left";
      ctx.fillText(opts.label, area.left + 6, y - 7); ctx.restore();
    }
  };

  function renderCharts() {
    if (!window.Chart || !window.CXI_DATA) return;
    charts.forEach(function (c) { c.destroy(); }); charts = [];
    var D = window.CXI_DATA;
    var el;
    if ((el = document.getElementById("chart-gt5y")) && D.gt5y) {
      var o = baseOptions("Índice relativo (máx. = 100)");
      o.plugins.eventLines = { events: D.gt5y.events };
      charts.push(new Chart(el, { type: "line", plugins: [eventLines], options: o, data: {
        labels: D.gt5y.labels,
        datasets: [
          { label: "argentina passport", data: D.gt5y.passport, borderColor: css("--chart-1"), backgroundColor: css("--chart-1"), borderWidth: 2, pointRadius: 0, pointHoverRadius: 5, tension: .2 },
          { label: "argentina citizenship", data: D.gt5y.citizenship, borderColor: css("--chart-2"), backgroundColor: css("--chart-2"), borderWidth: 2, pointRadius: 0, pointHoverRadius: 5, tension: .2 }
        ] } }));
    }
    if ((el = document.getElementById("chart-gt7d")) && D.gt7d) {
      var o2 = baseOptions("Índice relativo (máx. = 100)");
      o2.plugins.eventLines = { events: D.gt7d.events };
      charts.push(new Chart(el, { type: "line", plugins: [eventLines], options: o2, data: {
        labels: D.gt7d.labels,
        datasets: [
          { label: "argentina citizenship", data: D.gt7d.citizenship, borderColor: css("--chart-2"), backgroundColor: css("--chart-2"), borderWidth: 2, pointRadius: 0, pointHoverRadius: 5, tension: .15 },
          { label: "argentina passport", data: D.gt7d.passport, borderColor: css("--chart-1"), backgroundColor: css("--chart-1"), borderWidth: 2, pointRadius: 0, pointHoverRadius: 5, tension: .15 }
        ] } }));
    }
    if ((el = document.getElementById("chart-esc")) && D.esc) {
      var o3 = baseOptions("Ingreso al Tesoro (USD millones)");
      o3.interaction = { mode: "nearest", intersect: true };
      o3.plugins.hLine = { value: D.esc.caribe, label: "5 programas del Caribe juntos ≈ USD " + D.esc.caribe + " M/año" };
      o3.plugins.tooltip.callbacks.label = function (c) {
        var r = D.esc.rows[c.dataIndex];
        return [" Aportes: USD " + nf.format(r.ingreso) + " M", " " + nf.format(r.pctExt) + "% de venc. de capital externo 2027", " " + nf.format(r.pctRes) + "% de reservas brutas"];
      };
      charts.push(new Chart(el, { type: "bar", plugins: [hLine], options: o3, data: {
        labels: D.esc.rows.map(function (r) { return nf.format(r.n) + " solicitantes"; }),
        datasets: [{ label: "Aportes", data: D.esc.rows.map(function (r) { return r.ingreso; }), backgroundColor: css("--chart-1"), borderRadius: { topLeft: 4, topRight: 4 }, maxBarThickness: 90 }]
      } }));
    }
  }
  window.addEventListener("load", renderCharts);

  // ---------- Explorador de afirmaciones ----------
  function initClaims() {
    var tbody = document.getElementById("claims-body");
    if (!tbody || !window.CXI_CLAIMS) return;
    var q = document.getElementById("f-q"), m = document.getElementById("f-mod"), e = document.getElementById("f-et"), s = document.getElementById("f-st");
    var count = document.getElementById("claims-count");
    var params = new URLSearchParams(location.search);
    if (params.get("q")) q.value = params.get("q");
    function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
    function tagClass(et) { return "tag tag--" + et.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
    function render() {
      var qq = q.value.trim().toLowerCase(), mm = m.value, ee = e.value, ss = s.value, out = [], n = 0;
      window.CXI_CLAIMS.forEach(function (c) {
        if (mm && c.m !== mm) return;
        if (ee && c.e !== ee) return;
        if (ss && c.s !== ss) return;
        if (qq && (c.id + " " + c.a + " " + c.v + " " + c.f + " " + c.c).toLowerCase().indexOf(qq) < 0) return;
        n++;
        if (n > 400) return;
        out.push('<tr id="' + esc(c.id) + '"><td><span class="ed-meta-mono">' + esc(c.id) + '</span></td><td><span class="' + tagClass(c.e) + '">' + esc(c.e) +
          '</span></td><td>' + esc(c.a) + (c.v ? '<br><strong>' + esc(c.v) + '</strong>' : '') + '</td><td>' +
          (c.u ? '<a href="' + esc(c.u) + '" target="_blank" rel="noopener">' + esc(c.f) + '</a>' : esc(c.f)) +
          (c.t ? ' <span class="ed-meta-mono">(' + esc(c.t) + ')</span>' : '') +
          '<div class="ed-claim-cita">' + esc(c.c) + '</div></td><td><span class="' + (c.s === "OK" ? "status-ok" : "status-rev") + '">' + esc(c.s) + '</span><div class="ed-claim-cita">' + esc(c.n) + '</div></td></tr>');
      });
      tbody.innerHTML = out.join("");
      count.textContent = n + (n === 1 ? " afirmación" : " afirmaciones") + (n > 400 ? " (se muestran 400; refiná la búsqueda)" : "");
    }
    [q, m, e, s].forEach(function (x) { x.addEventListener("input", render); });
    render();
  }
  function highlightHash() {
    if (!location.hash) return;
    var el = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (el) { el.classList.add("hl"); el.scrollIntoView({ block: "center" }); }
  }
})();
