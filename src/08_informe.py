"""Arma el informe final a partir del resumen ejecutivo y los documentos por módulo.

Entradas: docs/resumen_ejecutivo.md, docs/modulos/{A..G}_*.md, outputs/charts/*.png
Salidas:  outputs/informe.md, outputs/informe.html, outputs/informe.pdf (fondo blanco)
"""
from __future__ import annotations

import re

import markdown

from common import CHARTS, DOCS, ROOT, TODAY

OUT = ROOT / "outputs"
ORDER = ["A", "B", "C", "D", "E", "E2", "F", "G"]

CSS = """
@page { size: A4; margin: 18mm 16mm; @bottom-right { content: counter(page); font-size: 8pt; color: #52514e; } }
html, body { background: #ffffff; color: #0b0b0b; }
body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 10pt; line-height: 1.45; max-width: 900px; margin: 0 auto; padding: 16px; }
h1 { font-size: 20pt; margin-bottom: 4px; } h2 { font-size: 14pt; border-bottom: 1px solid #c3c2b7; padding-bottom: 3px; margin-top: 28px; page-break-after: avoid; }
h3 { font-size: 11.5pt; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; font-size: 8.5pt; margin: 8px 0; display: block; overflow-x: auto; }
th, td { border: 1px solid #d9d8d3; padding: 3px 5px; vertical-align: top; text-align: left; word-break: break-word; }
th { background: #f0efec; }
img { max-width: 100%; height: auto; display: block; margin: 10px 0; page-break-inside: avoid; }
code { font-size: 8.5pt; background: #f4f4f2; padding: 0 2px; word-break: break-all; }
.meta { color: #52514e; font-size: 9pt; }
.modulo { page-break-before: always; }
@media print { table { display: table; } th, td { word-break: normal; overflow-wrap: break-word; } }
"""


def section(md: str, title_re: str) -> str:
    """Devuelve el cuerpo de la sección '## <título>' (hasta el próximo '## ')."""
    m = re.search(rf"^## {title_re}\s*$(.*?)(?=^## |\Z)", md, flags=re.M | re.S)
    return m.group(1).strip() if m else ""


def consolidate_sources() -> None:
    fu = ["# Fuentes", "", "Tipos: **P** primaria · **R** referencia privada con metodología pública · **S** secundaria (solo para fechar).",
          "Copias locales en `data/raw/` con fecha; hash SHA-256 en `docs/claims_ledger.csv`. Generado por `src/08_informe.py`.", ""]
    ff = ["# Fuentes fallidas", "", "Fuentes que no pudieron descargarse o verificarse, con causa y acción. Generado por `src/08_informe.py`.", "",
          "## General (probe de fuentes)", "",
          "| Fecha | Fuente | Error | Causa | Acción |", "|---|---|---|---|---|",
          "| 2026-10-03 | 52 URLs de 39 dominios (primer probe) | ProxyError 403 al CONNECT | Política de red del primer entorno | Resuelto: red habilitada; probe 48/55 OK |",
          "| 2026-10-03 | web.archive.org | Conexión reseteada por el proxy de egreso (ws_closed_mid_exchange) durante toda la primera sesión | Red del primer entorno | **Resuelto:** el mismo día se re-corrieron los módulos desde otra red; la Wayback respondió y se completaron la serie de rechazo de visas (D) y los respaldos de los demás módulos |",
          "| 2026-10-03 | api.census.gov | El probe lo marcó OK pero redirige a missing_key.html | La API exige key con registro | E usó el ACS Summary File oficial |", ""]
    for m, path in module_docs():
        md = path.read_text(encoding="utf-8")
        title = md.splitlines()[0].lstrip("# ").strip()
        a, b = section(md, r"Fuentes"), section(md, r"Fuentes fallidas")
        if a:
            fu += [f"## {title}", "", a, ""]
        if b:
            ff += [f"## {title}", "", b, ""]
    (DOCS / "fuentes.md").write_text("\n".join(fu), encoding="utf-8")
    (DOCS / "fuentes_fallidas.md").write_text("\n".join(ff), encoding="utf-8")


def module_docs() -> list:
    docs = []
    for m in ORDER:
        hits = sorted((DOCS / "modulos").glob(f"{m}_*.md"))
        if hits:
            docs.append((m, hits[0]))
    return docs


def charts_for(m: str) -> list:
    return sorted(CHARTS.glob(f"{m}_*.png"))


def demote(md: str) -> str:
    """Baja un nivel los encabezados de un documento de módulo (# -> ##)."""
    return re.sub(r"^(#{1,5}) ", lambda x: "#" + x.group(1) + " ", md, flags=re.M)


def build_md() -> str:
    parts = [f"# Ciudadanía por Inversión y el \"momento Argentina\"\n\n"
             f"<p class=\"meta\">Colossus Lab · Informe generado el {TODAY} · "
             f"Etiquetas: <b>DATO</b> (fuente directa) · <b>ESTIMACIÓN</b> (cálculo propio) · "
             f"<b>HIPÓTESIS</b> (interpretación) · <b>ESCENARIO</b> (proyección condicional). "
             f"Cada DATO tiene su cita literal en <code>docs/claims_ledger.csv</code>, auditada contra la copia local "
             f"(<code>docs/auditoria.csv</code>).</p>\n"]
    resumen = DOCS / "resumen_ejecutivo.md"
    if resumen.exists():
        parts.append(demote(resumen.read_text(encoding="utf-8")))
    for m, path in module_docs():
        body = demote(path.read_text(encoding="utf-8"))
        imgs = "\n".join(f"![{p.stem}](charts/{p.name})" for p in charts_for(m))
        # Inserta los gráficos después del resumen de 5 líneas (antes de la primera sección ### que no sea el resumen).
        split = re.search(r"^### (?!.*Resumen)", body, flags=re.M)
        if imgs and split:
            body = body[:split.start()] + imgs + "\n\n" + body[split.start():]
        elif imgs:
            body += "\n\n" + imgs
        parts.append(f"<div class=\"modulo\"></div>\n\n{body}")
    return "\n\n".join(parts)


def main() -> None:
    consolidate_sources()
    md = build_md()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "informe.md").write_text(md, encoding="utf-8")
    body = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
    html = (f"<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\">"
            f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>Ciudadanía por Inversión — Colossus Lab</title><style>{CSS}</style></head>"
            f"<body>{body}</body></html>")
    (OUT / "informe.html").write_text(html, encoding="utf-8")
    try:
        from weasyprint import HTML
        HTML(string=html, base_url=str(OUT)).write_pdf(OUT / "informe.pdf")
        print("-> outputs/informe.{md,html,pdf}")
    except Exception as e:  # noqa: BLE001
        # WeasyPrint necesita Pango/GTK (en Windows no viene instalado): respaldo con Chromium/Edge headless.
        if headless_pdf(OUT / "informe.html", OUT / "informe.pdf"):
            print(f"-> outputs/informe.{{md,html,pdf}} (PDF con navegador headless; WeasyPrint: {type(e).__name__})")
        else:
            print(f"PDF no generado ({type(e).__name__}: {e}); quedan outputs/informe.md y .html")


def headless_pdf(src, dst) -> bool:
    """Imprime `src` a PDF con Edge/Chrome headless, con un perfil temporal (no toca el navegador del usuario)."""
    import shutil
    import subprocess
    import tempfile
    from pathlib import Path
    cands = [shutil.which(n) for n in ("msedge", "chrome", "google-chrome", "chromium", "chromium-browser")]
    cands += [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe"]
    exe = next((c for c in cands if c and Path(c).exists()), None)
    if not exe:
        return False
    Path(dst).unlink(missing_ok=True)  # que un PDF viejo no pase por recién generado
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as prof:
        try:
            subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={prof}",
                            f"--print-to-pdf={dst}", Path(src).resolve().as_uri()],
                           capture_output=True, timeout=180, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return False
    return Path(dst).exists() and Path(dst).stat().st_size > 0


if __name__ == "__main__":
    main()
