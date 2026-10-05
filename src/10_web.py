"""Genera el sitio web estático del estudio (web/) con el sistema visual editorial de OpenArg.

Entradas: docs/resumen_ejecutivo.md, docs/modulos/*.md, docs/fuentes*.md, docs/claims_ledger.csv, docs/auditoria.csv,
          outputs/charts/*, outputs/informe.pdf, data/raw/E2_gt_Q1|Q3_*.csv, data/processed/G_escenarios.csv
Salida:   web/ (index, módulos, verificá, fuentes, metodología, assets, charts, descargas) — listo para Vercel.
"""
from __future__ import annotations

import csv
import html
import json
import re
import shutil
from pathlib import Path

import markdown
import pandas as pd

from common import CHARTS, DOCS, PROCESSED, RAW, ROOT, TODAY

WEB = ROOT / "web"
SRC = ROOT / "web_src"
SITE = "Ciudadanía por Inversión"
FONTS = ("https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700"
         "&family=JetBrains+Mono:wght@400;500;700&display=swap")
CHARTJS = "/assets/chart.umd.min.js"  # Chart.js 4.4.1 (MIT), copia local
BASE_URL = "https://ciudadania.openarg.org"  # dominio público (Vercel; DNS en Route 53, zona openarg.org)
DEFAULT_DESC = ("Investigación de Colossus Lab sobre el Programa de Ciudadanía por Inversión de Argentina: base legal, "
                "mercado, comparación internacional, pasaporte y escenarios fiscales, con cada dato verificado contra su fuente.")
OG_DIR, OG_W, OG_H = SRC / "og", 1200, 630  # tarjetas Open Graph (se versionan en web_src/og y se copian a web/og)

MODULES = [
    # (código, archivo, slug, título, bajada, etiquetas)
    ("A", "A_normativa.md", "marco-normativo", "Marco normativo", "Qué dice el DNU 366/2025, qué no dice y qué resolvieron los jueces", ["DNU 366/2025", "Boletín Oficial", "justicia"]),
    ("B", "B_mercado.md", "mercado-potencial", "Mercado potencial", "Quién puede pagarlo y a quién le sirve el pasaporte argentino", ["Fed SCF", "UBS", "movilidad"]),
    ("C", "C_benchmark.md", "benchmark-cbi", "Otros programas", "Argentina frente al Caribe, Turquía, Malta y las golden visas europeas", ["FMI", "Unión Europea", "Caribe"]),
    ("D", "D_pasaporte_vwp.md", "pasaporte-y-visa-waiver", "Pasaporte y Visa Waiver", "Qué vale el pasaporte y qué falta para entrar sin visa a EE.UU.", ["VWP", "DHS", "Chile"]),
    ("E", "E_popularidad.md", "popularidad-post-qatar", "¿Más popular desde Qatar?", "Atención, turismo y tipo de cambio, 2015–2026", ["Wikipedia", "turismo", "series de tiempo"]),
    ("E2", "E2_busquedas_pasaporte.md", "busquedas-del-pasaporte", "Búsquedas del pasaporte", "Qué se busca en Google sobre la ciudadanía argentina, dónde y desde cuándo", ["Google Trends", "EE.UU.", "mundo"]),
    ("F", "F_refugio.md", "refugio-austral", "¿Refugio austral?", "Argentina frente a Nueva Zelanda, Uruguay, Chile, Portugal y Canadá", ["WGI", "FAOSTAT", "litio"]),
    ("G", "G_escenarios.md", "escenarios-fiscales", "Escenarios fiscales", "Cuánto podría recaudar y qué parte de la deuda cubre", ["BCRA", "deuda", "escenarios"]),
]
ROMAN = ["I.", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII.", "IX."]
LABELS = r"(DATO|ESTIMACIÓN|HIPÓTESIS|ESCENARIO)"
CLAIM_RE = re.compile(r"\b((?:A|B|C|D|E|F|G)\d{2,3})\b")


# ------------------------------------------------------------------ utilidades de HTML
def esc(t: str) -> str:
    return html.escape(str(t), quote=True)


def tag_html(label: str) -> str:
    cls = {"DATO": "dato", "ESTIMACIÓN": "estimacion", "HIPÓTESIS": "hipotesis", "ESCENARIO": "escenario"}[label]
    return f'<span class="tag tag--{cls}">{label}</span>'


def md_to_html(md: str, claim_ids: set) -> str:
    h = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
    h = re.sub(r'(src|href)="[^"]*?outputs/charts/', r'\1="/charts/', h)
    h = re.sub(r"<table>", '<div class="ed-table-wrap"><table>', h)
    h = h.replace("</table>", "</table></div>")
    # Etiquetas dentro de negritas -> chips
    h = re.sub(r"<strong>(.*?)</strong>", lambda m: "<strong>" + re.sub(LABELS, lambda x: tag_html(x.group(1)), m.group(1)) + "</strong>", h)
    return link_claims(h, claim_ids)


def link_claims(h: str, claim_ids: set) -> str:
    """Enlaza códigos de afirmación (A01, F058…) al explorador, solo en texto (no dentro de etiquetas ni de <a>/<code>)."""
    out, depth_a = [], 0
    for part in re.split(r"(<[^>]+>)", h):
        if part.startswith("<"):
            if re.match(r"<(a|code)\b", part):
                depth_a += 1
            elif re.match(r"</(a|code)>", part):
                depth_a = max(0, depth_a - 1)
            out.append(part)
        elif depth_a:
            out.append(part)
        else:
            out.append(CLAIM_RE.sub(lambda m: f'<a class="claim" href="/verificar?q={m.group(1)}#{m.group(1)}">{m.group(1)}</a>'
                                    if m.group(1) in claim_ids else m.group(1), part))
    return "".join(out)


def inline_md(t: str, claim_ids: set) -> str:
    h = md_to_html(t, claim_ids)
    return re.sub(r"^<p>(.*)</p>$", r"\1", h.strip(), flags=re.S)


def page(title: str, body: str, active: str = "", description: str = "", extra_head: str = "", scripts: str = "",
         path: str = "/", og_image: str = "/og/inicio.png", og_type: str = "article") -> str:
    nav = [("/", "Inicio"), ("/#respuestas", "Respuestas"), ("/#modulos", "Módulos"), ("/verificar", "Verificá"),
           ("/fuentes", "Fuentes"), ("/metodologia", "Metodología")]
    cur = ' aria-current="page"'
    nav_html = "".join(f'<a href="{u}"{cur if active == u else ""}>{t}</a>' for u, t in nav)
    desc = esc(description or DEFAULT_DESC)
    url, img = esc(BASE_URL + path), esc(BASE_URL + og_image)
    return f"""<!doctype html>
<html lang="es-AR" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="{esc(SITE)} — Colossus Lab">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="es_AR">
<meta property="og:type" content="{og_type}">
<meta property="og:image" content="{img}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="{OG_W}">
<meta property="og:image:height" content="{OG_H}">
<meta property="og:image:alt" content="{esc(title)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%2306090f'/%3E%3Crect y='10' width='32' height='12' fill='%2374acdf'/%3E%3Ccircle cx='16' cy='16' r='4' fill='%23f6b40e'/%3E%3C/svg%3E">
<script>try{{var t=localStorage.getItem("cxi-theme");if(t)document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
<link rel="stylesheet" href="/assets/fonts/fonts.css">
<link rel="stylesheet" href="/assets/style.css">
{extra_head}
</head>
<body>
<header>
<span class="ed-flagstripe" aria-hidden="true"></span>
<div class="ed-topbar">
  <a class="ed-topbar-mark" href="/"><span class="ed-topbar-mark-name">{SITE}</span><span class="ed-topbar-mark-sub">por Colossus Lab</span></a>
  <nav class="ed-topbar-nav" aria-label="Principal">{nav_html}</nav>
  <div class="ed-topbar-right">
    <button class="ed-theme-toggle" type="button" aria-label="Cambiar tema">☀</button>
    <a class="ed-topbar-cta" href="/descargas/informe.pdf">Informe PDF</a>
  </div>
</div>
</header>
<main>
{body}
</main>
{colophon()}
{scripts}
<script src="/assets/app.js"></script>
</body>
</html>
"""


def colophon() -> str:
    mods = "".join(f'<a href="/modulos/{m[2]}">{m[0]} · {esc(m[3])}</a>' for m in MODULES)
    return f"""<footer class="ed-colophon">
<div class="ed-container">
  <div class="ed-colophon-grid">
    <div><span class="ed-colophon-brand-name">{SITE}</span><span class="ed-meta">por Colossus Lab · en la línea editorial de OpenArg</span>
      <p class="ed-lead" style="margin-top:.8rem;font-size:.85rem">Investigación con fuentes oficiales. Cada dato tiene su cita literal y se verifica de forma automática contra la copia descargada.</p></div>
    <div><span class="ed-colophon-col-title">Módulos</span>{mods}</div>
    <div><span class="ed-colophon-col-title">Verificación</span><a href="/verificar">Explorador de afirmaciones</a><a href="/fuentes">Fuentes</a><a href="/fuentes#fallidas">Fuentes fallidas</a><a href="/metodologia">Metodología</a></div>
    <div><span class="ed-colophon-col-title">Descargas</span><a href="/descargas/informe.pdf">Informe completo (PDF)</a><a href="/descargas/claims_ledger.csv">Registro de afirmaciones (CSV)</a><a href="/descargas/auditoria.csv">Auditoría (CSV)</a><a href="https://openarg.org" rel="noopener">OpenArg</a></div>
  </div>
  <div class="ed-colophon-bottom"><span>Colossus Lab · Buenos Aires · MMXXVI</span><span>Corte de datos: {TODAY}</span></div>
</div>
</footer>"""


# ------------------------------------------------------------------ datos
def load_claims() -> list:
    with (DOCS / "claims_ledger.csv").open(encoding="utf-8") as f:
        led = list(csv.DictReader(f))
    aud = {}
    if (DOCS / "auditoria.csv").exists():
        with (DOCS / "auditoria.csv").open(encoding="utf-8") as f:
            aud = {r["claim_id"]: r for r in csv.DictReader(f)}
    out = []
    for r in led:
        a = aud.get(r["claim_id"], {})
        out.append(dict(id=r["claim_id"], m=r["modulo"], e=r["etiqueta"], a=r["afirmacion"], v=r["valor"], f=r["fuente"],
                        t=r["tipo_fuente"], u=r["url"] if r["url"].startswith("http") else "", c=r["cita_textual"][:600],
                        s=a.get("estado", "—"), n=a.get("nota", "")))
    return out


def chart_data() -> dict:
    d = {}
    q1 = sorted(RAW.glob("E2_gt_Q1_*.csv"))
    if q1:
        df = pd.read_csv(q1[-1], index_col=0, parse_dates=True)
        labels = [x.strftime("%Y-%m-%d") for x in df.index]

        def nearest(date):
            t = pd.Timestamp(date)
            return labels[int(abs(df.index - t).argmin())]
        d["gt5y"] = dict(labels=labels, passport=df["argentina passport"].tolist(), citizenship=df["argentina citizenship"].tolist(),
                         events=[dict(at=nearest("2025-07-28"), label="Declaración VWP (28/07/25)"),
                                 dict(at=nearest("2026-06-14"), label="Mundial 2026 en EE.UU."),
                                 dict(at=nearest("2026-10-02"), label="Anuncio CBI")])
    q3 = sorted(RAW.glob("E2_gt_Q3_*.csv"))
    if q3:
        df = pd.read_csv(q3[-1], index_col=0, parse_dates=True)
        labels = [x.strftime("%d/%m %H:00") for x in df.index]
        ann = next((l for x, l in zip(df.index, labels) if x >= pd.Timestamp("2026-10-02")), None)
        d["gt7d"] = dict(labels=labels, citizenship=df["argentina citizenship"].tolist(), passport=df["argentina passport"].tolist(),
                         events=[dict(at=ann, label="02/10, día del anuncio")] if ann else [])
    g = PROCESSED / "G_escenarios.csv"
    if g.exists():
        df = pd.read_csv(g)
        df = df[df["canal"] == "70% aporte / 30% bono"]
        d["esc"] = dict(caribe=492, rows=[dict(n=int(r.solicitantes_principales), ingreso=float(r.ingreso_tesoro_musd),
                                              pctExt=float(r.pct_venc_capital_externo_2027), pctRes=float(r.pct_reservas))
                                         for r in df.itertuples()])
    return d


# ------------------------------------------------------------------ páginas
def build_index(claims: list, ids: set) -> str:
    rs = (DOCS / "resumen_ejecutivo.md").read_text(encoding="utf-8")
    rows = [l for l in rs.splitlines() if l.startswith("| ") and not l.startswith("| Pregunta") and not l.startswith("|---")]
    answers = []
    for l in rows:
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        q, a, et = cells[:3]
        tags = "".join(tag_html(x.strip()) for x in et.split("/") if x.strip() in ("DATO", "ESTIMACIÓN", "HIPÓTESIS", "ESCENARIO"))
        answers.append(f'<div class="ed-answer"><div class="ed-answer-q">{esc(q)}</div><div class="ed-answer-a">{inline_md(a, ids)}</div><div class="ed-answer-tags">{tags}</div></div>')
    risks_md = rs[rs.index("## Los tres riesgos"):rs.index("## Qué no se pudo verificar")]
    risks = []
    for i, m in enumerate(re.finditer(r"^\d\. \*\*(.+?)\*\*\s*(.+)$", risks_md, flags=re.M)):
        title = re.sub(r"\s*\((DATO|ESCENARIO|HIPÓTESIS|ESTIMACIÓN)\)\.?$", "", m.group(1)).rstrip(".")
        lab = re.search(LABELS, m.group(1))
        risks.append(f'<div class="ed-pipeline-step"><span class="ed-pipeline-num">0{i + 1}</span><h3 class="ed-pipeline-label">{esc(title)} {tag_html(lab.group(1)) if lab else ""}</h3>'
                     f'<p class="ed-pipeline-desc">{inline_md(m.group(2), ids)}</p></div>')
    n_ok = sum(c["s"] == "OK" for c in claims)
    cards = "".join(f'<a class="ed-ecosystem-card" href="/modulos/{m[2]}"><div class="ed-ecosystem-card-glyph" aria-hidden="true">{m[0]}</div>'
                    f'<div class="ed-ecosystem-card-body"><span class="ed-ecosystem-card-num">MÓDULO {m[0]} · {sum(c["m"] == m[0] for c in claims)} AFIRMACIONES</span>'
                    f'<h3 class="ed-ecosystem-card-title">{esc(m[3])}</h3><p class="ed-ecosystem-card-tagline">{esc(m[4])}</p>'
                    f'<span class="ed-ecosystem-card-cta">Abrir →</span></div></a>' for m in MODULES)
    toc = "".join(f'<li><a href="/modulos/{m[2]}"><span class="n">{m[0]}</span>{esc(m[3])}</a></li>' for m in MODULES)
    L = lambda cid: f'<a class="claim" href="/verificar?q={cid}#{cid}">{cid}</a>'
    body = f"""
<section class="ed-hero"><div class="ed-container">
  <div class="ed-hero-center">
    <p class="ed-eyebrow"><span class="ed-eyebrow-num">N.º 01 / MMXXVI</span> Informe · corte {TODAY[8:10]}/{TODAY[5:7]}/{TODAY[:4]}</p>
    <h1 class="ed-display ed-hero-title"><span class="ed-hero-title-line">Ciudadanía por inversión,</span><span class="ed-hero-title-line ed-hero-title-line--alt">¿momento Argentina?</span></h1>
    <p class="ed-hero-subtitle">El 2 de octubre de 2026 el Gobierno anunció que va a vender la ciudadanía argentina a cambio de USD 350.000. Revisamos la base legal, quién podría comprarla, cuánto podría recaudar y si el “momento Argentina” que la justifica se sostiene con datos.</p>
    <div class="ed-hero-actions">
      <a class="ed-textlink" href="#respuestas">Las respuestas <span class="ed-textlink-arrow">→</span></a>
      <a class="ed-textlink" href="#modulos">Los ocho módulos <span class="ed-textlink-arrow">→</span></a>
      <a class="ed-textlink" href="/verificar">Verificá cada dato <span class="ed-textlink-arrow">→</span></a>
    </div>
  </div>
  <div class="ed-hero-foot">
    <div><div class="ed-num-display">{n_ok}</div><p class="ed-meta">afirmaciones verificadas contra su fuente · de {len(claims)} registradas</p>
      <p class="ed-lead" style="margin-top:.8rem">Cada número de este sitio enlaza a su fuente oficial, a la copia descargada y a la cita literal que lo respalda.</p></div>
    <nav aria-label="Módulos"><ul class="ed-hero-toc">{toc}</ul></nav>
  </div>
</div></section>

<section class="ed-section"><div class="ed-container">
  <div class="ed-section-head"><p class="ed-eyebrow"><span class="ed-eyebrow-num">I.</span> Cuatro cifras</p>
    <h2 class="ed-section-title">Lo que hay que saber en un minuto</h2></div>
  <div class="ed-scale-row"><div class="ed-scale-row-num">USD 350.000</div><div class="ed-scale-row-label">El precio</div>
    <div class="ed-scale-row-detail">Aporte no reembolsable al Tesoro, o USD 800.000 en un bono. Una familia tipo paga USD 500.000 {L("A01")} {L("A05")}. Es el programa verificado más caro del benchmark {L("C80")}.</div></div>
  <div class="ed-scale-row"><div class="ed-scale-row-num">30/06/26</div><div class="ed-scale-row-label">La base legal, anulada</div>
    <div class="ed-scale-row-detail">La Cámara Nacional Electoral declaró nulo el DNU 366/2025, que crea la vía por inversión {L("A18")}. Ninguna norma publicada fija los montos anunciados {L("A17")}.</div></div>
  <div class="ed-scale-row"><div class="ed-scale-row-num">USD 492 M</div><div class="ed-scale-row-label">Lo que recauda todo el Caribe</div>
    <div class="ed-scale-row-detail">Promedio anual de los cinco programas caribeños juntos (2020–24) {L("C90")}. Igualarlo exigiría ≈ 1.430 solicitantes argentinos por año {L("G06")}.</div></div>
  <div class="ed-scale-row"><div class="ed-scale-row-num">+1.300%</div><div class="ed-scale-row-label">La búsqueda que más creció</div>
    <div class="ed-scale-row-detail">“argentina citizenship by investment program” en Google, la semana del anuncio {L("E62")}. El interés por el pasaporte argentino en EE.UU. ya venía creciendo desde mediados de 2025 {L("E51")}.</div></div>
</div></section>

<section class="ed-section" id="respuestas"><div class="ed-container">
  <div class="ed-section-head"><p class="ed-eyebrow"><span class="ed-eyebrow-num">II.</span> Respuestas</p>
    <h2 class="ed-section-title">Nueve preguntas, nueve respuestas con su etiqueta</h2>
    <p class="ed-lead">{tag_html("DATO")} sale directo de una fuente · {tag_html("ESTIMACIÓN")} es un cálculo propio con método explícito · {tag_html("HIPÓTESIS")} es una interpretación · {tag_html("ESCENARIO")} es una proyección condicional.</p></div>
  <div class="ed-answers">{''.join(answers)}</div>
</div></section>

<section class="ed-section"><div class="ed-container">
  <div class="ed-section-head"><p class="ed-eyebrow"><span class="ed-eyebrow-num">III.</span> Riesgos</p>
    <h2 class="ed-section-title">Los tres riesgos que más pesan</h2></div>
  <div class="ed-pipeline">{''.join(risks)}</div>
</div></section>

<section class="ed-section"><div class="ed-container">
  <div class="ed-section-head"><p class="ed-eyebrow"><span class="ed-eyebrow-num">IV.</span> Google</p>
    <h2 class="ed-section-title">El pasaporte argentino ya se buscaba antes del anuncio</h2>
    <p class="ed-lead">Índice relativo de Google Trends (0–100; no es cantidad de búsquedas). En EE.UU. el interés despegó con la declaración para volver al Visa Waiver Program y tocó su máximo durante el Mundial. El anuncio del 2 de octubre generó un pico mundial inmediato.</p></div>
  <figure class="ed-chart"><p class="ed-chart-title">Estados Unidos, semanal, últimos 5 años</p>
    <div class="ed-chart-legend"><span><i style="background:var(--chart-1)"></i>argentina passport</span><span><i style="background:var(--chart-2)"></i>argentina citizenship</span></div>
    <div class="ed-chart-canvas"><canvas id="chart-gt5y" role="img" aria-label="Serie semanal de Google Trends en EE.UU. para argentina passport y argentina citizenship, 2021–2026"></canvas></div>
    <figcaption class="ed-chart-note">Fuente: Google Trends, geo=US, descargado el {TODAY} {L("E50")} {L("E51")} {L("E52")}. Que coincidan en fecha no prueba la causa.</figcaption></figure>
  <figure class="ed-chart"><p class="ed-chart-title">Mundo, por hora, últimos 7 días</p>
    <div class="ed-chart-legend"><span><i style="background:var(--chart-2)"></i>argentina citizenship</span><span><i style="background:var(--chart-1)"></i>argentina passport</span></div>
    <div class="ed-chart-canvas"><canvas id="chart-gt7d" role="img" aria-label="Serie horaria mundial de Google Trends de los últimos 7 días"></canvas></div>
    <figcaption class="ed-chart-note">Fuente: Google Trends, mundo, horas UTC {L("E54")} {L("E64")}. Más en <a class="ed-textlink" href="/modulos/busquedas-del-pasaporte">Búsquedas del pasaporte <span class="ed-textlink-arrow">→</span></a></figcaption></figure>
</div></section>

<section class="ed-section"><div class="ed-container">
  <div class="ed-section-head"><p class="ed-eyebrow"><span class="ed-eyebrow-num">V.</span> Escenarios</p>
    <h2 class="ed-section-title">Cuánto podría recaudar, y qué cubre</h2>
    <p class="ed-lead">{tag_html("ESCENARIO")} Aportes al Tesoro según cuántos solicitantes principales se aprueben por año (70% aporte, 30% bono; el bono es financiamiento, no ingreso). La línea marca lo que recaudan juntos los cinco programas del Caribe.</p></div>
  <figure class="ed-chart"><div class="ed-chart-canvas"><canvas id="chart-esc" role="img" aria-label="Ingreso al Tesoro por escenario de solicitantes, comparado con el Caribe"></canvas></div>
    <figcaption class="ed-chart-note">Fuente: MECON (anuncio 02/10/2026), Secretaría de Finanzas (deuda al 30/06/2026), BCRA, FMI. {L("G04")} {L("G05")} {L("G06")} {L("C90")}</figcaption></figure>
</div></section>

<section class="ed-section" id="modulos"><div class="ed-container">
  <div class="ed-section-head"><p class="ed-eyebrow"><span class="ed-eyebrow-num">VI.</span> El estudio</p>
    <h2 class="ed-section-title">Ocho módulos, cada uno con su método y sus fuentes</h2>
    <p class="ed-lead">Cada módulo abre con un resumen de cinco líneas y documenta qué fuentes se usaron, cuáles fallaron y por qué.</p></div>
  <div class="ed-ecosystem">{cards}</div>
</div></section>

<section class="ed-section"><div class="ed-container">
  <div class="ed-section-head"><p class="ed-eyebrow"><span class="ed-eyebrow-num">VII.</span> Método</p>
    <h2 class="ed-section-title">Cómo se verifica cada dato</h2></div>
  <div class="ed-pipeline ed-pipeline--4">
    <div class="ed-pipeline-step"><span class="ed-pipeline-num">01</span><h3 class="ed-pipeline-label">Fuente oficial</h3><p class="ed-pipeline-desc">Boletín Oficial, BCRA, INDEC, Fed, FMI, EUR-Lex, DHS. La prensa solo sirve para fechar eventos.</p></div>
    <div class="ed-pipeline-step"><span class="ed-pipeline-num">02</span><h3 class="ed-pipeline-label">Copia fechada</h3><p class="ed-pipeline-desc">Cada documento se descarga con fecha en el nombre y se registra su hash SHA-256.</p></div>
    <div class="ed-pipeline-step"><span class="ed-pipeline-num">03</span><h3 class="ed-pipeline-label">Cita literal</h3><p class="ed-pipeline-desc">Cada afirmación guarda la frase exacta o el localizador de la celda de la que sale.</p></div>
    <div class="ed-pipeline-step"><span class="ed-pipeline-num">04</span><h3 class="ed-pipeline-label">Auditoría</h3><p class="ed-pipeline-desc">Un script busca cada cita dentro de la copia local. Resultado: {n_ok} de {len(claims)} OK.</p></div>
  </div>
  <p style="margin-top:2rem"><a class="ed-textlink" href="/metodologia">Metodología y limitaciones <span class="ed-textlink-arrow">→</span></a></p>
</div></section>
"""
    return body


def build_module(i: int, mod: tuple, ids: set) -> str:
    code, fname, slug, title, tagline, tags = mod
    md = (DOCS / "modulos" / fname).read_text(encoding="utf-8")
    md = re.sub(r"^# .*\n", "", md, count=1)
    # Resumen de 5 líneas en caja destacada
    m = re.search(r"(?:^## Resumen \(5 líneas\)\s*$|^\*\*Resumen \(5 líneas\)\*\*\s*$)(.*?)(?=^## |^---|\Z)", md, flags=re.M | re.S)
    summary_html, rest = "", md
    if m:
        summary_html = f'<div class="ed-summary"><h2>Resumen en cinco líneas</h2>{md_to_html(m.group(1).strip(), ids)}</div>'
        rest = md[:m.start()] + md[m.end():]
    rest = re.sub(r"^---\s*$", "", rest, flags=re.M)
    pref = f"{code}_"
    plates = []
    for j, p in enumerate(sorted(CHARTS.glob(f"{pref}*.svg")), 1):
        if code == "E" and p.name.startswith("E2_"):
            continue
        plates.append(f'<figure class="ed-plate"><div class="ed-plate-paper"><img src="/charts/{p.name}" alt="Gráfico {code}.{j}: {esc(p.stem.replace("_", " "))}" loading="lazy"></div>'
                      f'<figcaption><span>Lámina {code}.{j}</span><span><a href="/charts/{p.name}">SVG</a> · <a href="/charts/{p.stem}.png">PNG</a></span></figcaption></figure>')
    prev_m = MODULES[i - 1] if i > 0 else None
    next_m = MODULES[i + 1] if i + 1 < len(MODULES) else None
    pager = '<nav class="ed-pager">' + (f'<a class="ed-textlink" href="/modulos/{prev_m[2]}">← {prev_m[0]} · {esc(prev_m[3])}</a>' if prev_m else "<span></span>") + \
            (f'<a class="ed-textlink" href="/modulos/{next_m[2]}">{next_m[0]} · {esc(next_m[3])} <span class="ed-textlink-arrow">→</span></a>' if next_m else '<a class="ed-textlink" href="/verificar">Verificá cada dato <span class="ed-textlink-arrow">→</span></a>') + "</nav>"
    tag_chips = " ".join(f'<span class="tag">{esc(t)}</span>' for t in tags)
    return f"""
<section class="ed-hero" style="padding-bottom:1rem"><div class="ed-container ed-article">
  <p class="ed-eyebrow"><span class="ed-eyebrow-num">Módulo {code}</span> {esc(ROMAN[i] if i < len(ROMAN) else "")} de VIII</p>
  <h1 class="ed-display" style="margin:1rem 0">{esc(title)}</h1>
  <p class="ed-lead">{esc(tagline)}</p>
  <p style="margin-top:1rem">{tag_chips}</p>
</div></section>
<section class="ed-section" style="padding-top:2rem"><div class="ed-container ed-article">
  {summary_html}
  {''.join(plates)}
  <div class="ed-prose">{dedupe_imgs(md_to_html(rest, ids), plates)}</div>
  {pager}
</div></section>"""


def dedupe_imgs(h: str, plates: list) -> str:
    """Quita del texto las imágenes que ya se muestran como lámina."""
    stems = {m for p in plates for m in re.findall(r'/charts/([^".]+)\.svg', p)}
    return re.sub(r'<p>\s*<img[^>]*src="/charts/([^".]+)\.(?:png|svg)"[^>]*>\s*</p>',
                  lambda m: "" if m.group(1) in stems else m.group(0), h)


def build_verificar(claims: list) -> str:
    mods = sorted({c["m"] for c in claims}, key=lambda x: (x[0], len(x)))
    mod_opts = "".join(f'<option value="{m}">Módulo {m}</option>' for m in mods)
    return f"""
<section class="ed-hero" style="padding-bottom:1rem"><div class="ed-container">
  <p class="ed-eyebrow"><span class="ed-eyebrow-num">Verificá</span> Registro de afirmaciones</p>
  <h1 class="ed-display" style="margin:1rem 0">Cada dato, con su fuente y su cita</h1>
  <p class="ed-lead">Las {len(claims)} afirmaciones del estudio, con la fuente, la cita literal (o el localizador de la celda) y el resultado de la auditoría automática contra la copia descargada. Buscá por código (A18), por tema o por fuente.</p>
</div></section>
<section class="ed-section" style="padding-top:2rem"><div class="ed-container">
  <div class="ed-filters" role="search">
    <input id="f-q" type="search" placeholder="Buscar: código, tema, fuente…" aria-label="Buscar afirmaciones">
    <select id="f-mod" aria-label="Módulo"><option value="">Todos los módulos</option>{mod_opts}</select>
    <select id="f-et" aria-label="Etiqueta"><option value="">Todas las etiquetas</option><option>DATO</option><option>ESTIMACIÓN</option><option>HIPÓTESIS</option><option>ESCENARIO</option></select>
    <select id="f-st" aria-label="Estado de auditoría"><option value="">Todos los estados</option><option>OK</option><option>REVISAR</option><option>FALLA</option></select>
  </div>
  <p class="ed-count" id="claims-count"></p>
  <div class="ed-table-wrap"><table class="ed-table"><thead><tr><th>Código</th><th>Etiqueta</th><th>Afirmación y valor</th><th>Fuente y cita</th><th>Auditoría</th></tr></thead>
    <tbody id="claims-body"></tbody></table></div>
  <p class="ed-meta" style="margin-top:1rem">Descargas: <a href="/descargas/claims_ledger.csv">claims_ledger.csv</a> · <a href="/descargas/auditoria.csv">auditoria.csv</a></p>
</div></section>"""


def build_simple(title: str, eyebrow: str, lead: str, md: str, ids: set) -> str:
    return f"""
<section class="ed-hero" style="padding-bottom:1rem"><div class="ed-container ed-article">
  <p class="ed-eyebrow"><span class="ed-eyebrow-num">{esc(eyebrow)}</span></p>
  <h1 class="ed-display" style="margin:1rem 0">{esc(title)}</h1>
  <p class="ed-lead">{lead}</p>
</div></section>
<section class="ed-section" style="padding-top:2rem"><div class="ed-container ed-article"><div class="ed-prose">{md_to_html(md, ids)}</div></div></section>"""


def metodologia_md() -> str:
    rs = (DOCS / "resumen_ejecutivo.md").read_text(encoding="utf-8")
    nv = rs[rs.index("## Qué no se pudo verificar"):rs.index("## Cómo leer este informe")]
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    pend = readme[readme.index("## Pendientes conocidos"):readme.index("Contacto:")] if "## Pendientes conocidos" in readme else ""
    return f"""## Reglas del estudio
- **Toda cifra sale de una fuente primaria (P) o de una referencia privada con metodología pública (R).** La prensa y los buscadores (S) solo sirven para fechar eventos.
- **Nada se completa "a ojo".** Si una fuente falla, se registra en [Fuentes fallidas](/fuentes#fallidas) y el trabajo sigue con lo que hay.
- **No se scrapea nada que esté detrás de un formulario de registro**, y no se usan fuentes cuyos términos prohíben el acceso automatizado (por ejemplo, Henley Passport Index).
- **No se asumen hechos no confirmados.** Por ejemplo, el resultado de Argentina en el Mundial 2026 se dio por cierto recién cuando se verificó en notas oficiales de CONMEBOL, AFA y RFEF (E34–E36).
- **Cuatro etiquetas:** DATO, ESTIMACIÓN, HIPÓTESIS y ESCENARIO. Los contrapesos se presentan con el mismo cuidado que la evidencia a favor.

## Cómo se verifica
1. Cada documento se descarga a `data/raw/` con la fecha en el nombre, y se registra su hash SHA-256.
2. Cada afirmación va a `docs/claims_ledger.csv` con su fuente, el archivo local y la cita literal. Si el dato sale de una tabla, en lugar de cita lleva un localizador (hoja, fila, columna, valor).
3. `src/09_auditoria.py` busca cada cita dentro del texto extraído de la copia local, o el valor dentro del archivo. Las ESTIMACIONES deben citar los códigos de sus insumos.
4. Las sumas que no se pueden verificar automáticamente se verifican a mano, y el procedimiento queda en `docs/auditoria_manual.csv`.

{nv}
{pend}
## Reproducir
El código y los datos están en el repositorio `colossus-lab/ciudadania-argentina`. Con `make all` se corren los módulos, la auditoría y se genera el informe; `python src/10_web.py` regenera este sitio.
"""


# ------------------------------------------------------------------ tarjetas Open Graph (1200×630)
OG_CSS = """
html, body { margin: 0; width: 1200px; height: 630px; overflow: hidden; background: #06090f; }
.c { position: relative; box-sizing: border-box; width: 1200px; height: 630px; padding: 70px 76px 54px; display: flex;
     flex-direction: column; color: #e8ecf4; font-family: "Inter", sans-serif;
     background: radial-gradient(900px 520px at 88% 0%, #74acdf26, transparent 62%),
                 radial-gradient(700px 420px at 0% 100%, #f6b40e14, transparent 60%),
                 linear-gradient(#74acdf0d 1px, transparent 1px) 0 0 / 48px 48px,
                 linear-gradient(90deg, #74acdf0d 1px, transparent 1px) 0 0 / 48px 48px, #06090f; }
.stripe { position: absolute; top: 0; left: 0; right: 0; height: 10px;
          background: linear-gradient(90deg, #74acdf 0 33.3%, #ffffff 33.3% 66.6%, #74acdf 66.6% 100%); }
.eyebrow { font-family: "JetBrains Mono", monospace; font-size: 22px; letter-spacing: .14em; text-transform: uppercase; color: #8892a8; }
.eyebrow b { color: #f6b40e; font-weight: 500; }
h1 { font-family: "Familjen Grotesk", sans-serif; font-weight: 700; letter-spacing: -.035em; line-height: 1.0;
     margin: 30px 0 0; max-width: 1040px; }
h1 em { font-style: normal; color: #74acdf; }
p { font-size: 29px; line-height: 1.38; color: #a3acc0; margin: 28px 0 0; max-width: 980px; }
.foot { margin-top: auto; display: flex; justify-content: space-between; align-items: flex-end; padding-top: 22px;
        border-top: 1px solid #e8ecf429; font-family: "JetBrains Mono", monospace; font-size: 22px; color: #8892a8; }
.foot .url { color: #e8ecf4; }
.foot .n { font-family: "Familjen Grotesk", sans-serif; font-weight: 700; font-size: 46px; letter-spacing: -.03em;
           color: #74acdf; margin-right: 12px; vertical-align: -4px; }
"""


def og_card(eyebrow: str, title_html: str, subtitle: str, n_claims: int, size: int) -> str:
    fonts = (SRC / "fonts" / "fonts.css").read_text(encoding="utf-8").replace(
        "/assets/fonts/", (SRC / "fonts").resolve().as_uri() + "/")
    return f"""<!doctype html><html lang="es-AR"><head><meta charset="utf-8"><style>{fonts}{OG_CSS}</style></head>
<body><div class="c"><span class="stripe"></span>
<div class="eyebrow">{eyebrow}</div>
<h1 style="font-size:{size}px">{title_html}</h1>
<p>{esc(subtitle)}</p>
<div class="foot"><span class="url">ciudadania.openarg.org</span>
<span><span class="n">{n_claims}</span>afirmaciones verificadas contra su fuente</span></div>
</div></body></html>"""


def build_og_images(n_claims: int) -> None:
    """Renderiza las tarjetas con Edge/Chrome headless a web_src/og/*.png. Sin navegador, conserva las existentes."""
    import subprocess
    import tempfile

    from common import find_browser
    exe = find_browser()
    if not exe:
        print("Sin navegador headless: se reutilizan las tarjetas Open Graph de web_src/og/")
        return
    cards = {"inicio": og_card("<b>Informe</b> · Colossus Lab · Octubre 2026",
                               "Ciudadanía por inversión,<br><em>¿momento Argentina?</em>",
                               "Base legal, mercado, otros programas, pasaporte, popularidad y escenarios fiscales "
                               "del programa anunciado el 02/10/2026.", n_claims, 96)}
    for code, _f, slug, title, sub, _tags in MODULES:
        cards[slug] = og_card(f"<b>Módulo {code}</b> · Ciudadanía por inversión", esc(title), sub, n_claims, 104)
    OG_DIR.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        for name, card in cards.items():
            src = Path(tmp) / f"{name}.html"
            src.write_text(card, encoding="utf-8")
            out = OG_DIR / f"{name}.png"
            subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                            f"--window-size={OG_W},{OG_H}", "--virtual-time-budget=4000", f"--user-data-dir={Path(tmp) / 'perfil'}",
                            f"--screenshot={out}", src.resolve().as_uri()], capture_output=True, timeout=120, check=False)
    print(f"Tarjetas Open Graph: {len(cards)} en web_src/og/")


def main() -> None:
    claims = load_claims()
    ids = {c["id"] for c in claims}
    if WEB.exists():
        shutil.rmtree(WEB)
    (WEB / "assets").mkdir(parents=True)
    (WEB / "modulos").mkdir()
    (WEB / "charts").mkdir()
    (WEB / "descargas").mkdir()
    shutil.copy(SRC / "style.css", WEB / "assets" / "style.css")
    shutil.copy(SRC / "app.js", WEB / "assets" / "app.js")
    shutil.copy(SRC / "chart.umd.min.js", WEB / "assets" / "chart.umd.min.js")
    shutil.copytree(SRC / "fonts", WEB / "assets" / "fonts")
    build_og_images(len(claims))
    if OG_DIR.exists():
        shutil.copytree(OG_DIR, WEB / "og")
    for p in CHARTS.glob("*"):
        if p.suffix in (".svg", ".png"):
            shutil.copy(p, WEB / "charts" / p.name)
    for src, dst in [(ROOT / "outputs" / "informe.pdf", "informe.pdf"), (DOCS / "claims_ledger.csv", "claims_ledger.csv"),
                     (DOCS / "auditoria.csv", "auditoria.csv")]:
        if src.exists():
            shutil.copy(src, WEB / "descargas" / dst)
    (WEB / "assets" / "data.js").write_text("window.CXI_DATA=" + json.dumps(chart_data(), ensure_ascii=False) + ";", encoding="utf-8")
    (WEB / "assets" / "claims.js").write_text("window.CXI_CLAIMS=" + json.dumps(claims, ensure_ascii=False) + ";", encoding="utf-8")

    chart_scripts = f'<script src="{CHARTJS}"></script><script src="/assets/data.js"></script>'
    (WEB / "index.html").write_text(page(f"{SITE}, ¿momento Argentina? — Colossus Lab", build_index(claims, ids), "/", scripts=chart_scripts,
                                          path="/", og_type="website"), encoding="utf-8")
    for i, mod in enumerate(MODULES):
        (WEB / "modulos" / f"{mod[2]}.html").write_text(
            page(f"{mod[3]} — {SITE} — Colossus Lab", build_module(i, mod, ids), "/#modulos", description=mod[4],
                 path=f"/modulos/{mod[2]}", og_image=f"/og/{mod[2]}.png"), encoding="utf-8")
    (WEB / "verificar.html").write_text(page(f"Verificá cada dato — {SITE}", build_verificar(claims), "/verificar", path="/verificar",
                                             scripts='<script src="/assets/claims.js"></script>'), encoding="utf-8")
    fu = (DOCS / "fuentes.md").read_text(encoding="utf-8").split("\n", 1)[1]
    ff = (DOCS / "fuentes_fallidas.md").read_text(encoding="utf-8").split("\n", 1)[1]
    fuentes_md = fu + '\n\n<h2 id="fallidas">Fuentes fallidas</h2>\n\n' + ff
    (WEB / "fuentes.html").write_text(page(f"Fuentes — {SITE}", build_simple(
        "Fuentes", "Fuentes", "Todas las fuentes usadas, por módulo, con su tipo (P primaria · R referencia con metodología pública · S secundaria, solo para fechar), y las que fallaron con su causa.",
        fuentes_md, ids), "/fuentes", path="/fuentes"), encoding="utf-8")
    (WEB / "metodologia.html").write_text(page(f"Metodología — {SITE}", build_simple(
        "Metodología", "Metodología", "Cómo se armó el estudio, cómo se verifica cada dato y qué quedó sin verificar.", metodologia_md(), ids), "/metodologia", path="/metodologia"), encoding="utf-8")
    (WEB / "404.html").write_text(page(f"No encontrado — {SITE}", build_simple("Página no encontrada", "404", 'Volvé al <a class="ed-textlink" href="/">inicio</a>.', "", ids)), encoding="utf-8")
    (WEB / "vercel.json").write_text(json.dumps({
        "cleanUrls": True, "trailingSlash": False,
        "headers": [{"source": "/(assets|charts)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=3600"}]}],
    }, indent=2), encoding="utf-8")
    n = sum(1 for _ in WEB.rglob("*") if _.is_file())
    print(f"web/ generado: {n} archivos")


if __name__ == "__main__":
    main()
