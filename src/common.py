"""Utilidades compartidas: sesión HTTP con User-Agent identificable, rate limit y guardado en data/raw."""
from __future__ import annotations

import datetime as dt
import hashlib
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
CHARTS = ROOT / "outputs" / "charts"
DOCS = ROOT / "docs"

UA = "ColossusLab-Research/1.0 (contacto: dantedeagostino@gmail.com)"
TODAY = dt.date.today().isoformat()

_session = requests.Session()
_session.headers.update({"User-Agent": UA, "Accept-Language": "es-AR,es;q=0.9,en;q=0.8"})
_last_call: dict[str, float] = {}
MIN_INTERVAL = 1.0  # segundos entre pedidos al mismo host


def _throttle(url: str) -> None:
    host = requests.utils.urlparse(url).netloc
    wait = MIN_INTERVAL - (time.time() - _last_call.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    _last_call[host] = time.time()


def get(url: str, retries: int = 3, timeout: int = 60, **kw) -> requests.Response:
    """GET con throttle por host y reintentos con backoff exponencial ante errores de red / 5xx / 429."""
    last_exc = None
    for i in range(retries):
        _throttle(url)
        try:
            r = _session.get(url, timeout=timeout, **kw)
            if r.status_code in (429, 500, 502, 503, 504) and i < retries - 1:
                time.sleep(2 ** (i + 1))
                continue
            return r
        except requests.RequestException as e:  # noqa: PERF203
            last_exc = e
            time.sleep(2 ** (i + 1))
    raise last_exc  # type: ignore[misc]


def raw_path(name: str, ext: str, date: str | None = None) -> Path:
    """data/raw/{name}_{YYYY-MM-DD}.{ext}"""
    return RAW / f"{name}_{date or TODAY}.{ext.lstrip('.')}"


def download(url: str, name: str, ext: str, force: bool = False, **kw) -> Path:
    """Descarga `url` a data/raw con fecha en el nombre. Reutiliza la copia del día si existe."""
    RAW.mkdir(parents=True, exist_ok=True)
    existing = [p for p in sorted(RAW.glob(f"{name}_*.{ext.lstrip('.')}")) if p.stat().st_size > 0]
    if existing and not force:
        return existing[-1]
    r = get(url, **kw)
    r.raise_for_status()
    if not r.content:
        raise ValueError(f"Respuesta vacía (HTTP {r.status_code}) para {url}: no se guarda un archivo de 0 bytes")
    p = raw_path(name, ext)
    p.write_bytes(r.content)
    return p


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def find_browser() -> str | None:
    """Edge/Chrome/Chromium para tareas headless (PDF del informe, imágenes Open Graph del sitio)."""
    import shutil
    cands = [shutil.which(n) for n in ("msedge", "chrome", "google-chrome", "chromium", "chromium-browser")]
    cands += [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe"]
    return next((c for c in cands if c and Path(c).exists()), None)


# --- Extracción de texto y registro de afirmaciones (claims ledger) ---------------------------------

import csv
import html as _html
import re as _re

LEDGER = DOCS / "claims_ledger.csv"
CLAIMS_DIR = DOCS / "claims"
LEDGER_FIELDS = ["claim_id", "modulo", "etiqueta", "afirmacion", "valor", "fuente", "tipo_fuente", "url",
                 "archivo_local", "sha256", "cita_textual", "fecha_acceso"]


def html_to_text(path: Path) -> str:
    s = path.read_text(encoding="utf-8", errors="ignore")
    s = _re.sub(r"(?is)<(script|style).*?</\1>", "", s)
    s = _re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</tr>", "\n", s)
    t = _html.unescape(_re.sub(r"<[^>]+>", " ", s))
    return norm_ws(t)


def pdf_to_text(path: Path) -> str:
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return norm_ws("\n".join((p.extract_text() or "") for p in pdf.pages))


def norm_ws(t: str) -> str:
    return _re.sub(r"\s+", " ", t.replace(" ", " ")).strip()


def local_text(path: Path) -> str:
    return pdf_to_text(path) if path.suffix.lower() == ".pdf" else html_to_text(path)


def quote(text: str, needle: str) -> str:
    """Devuelve `needle` si aparece literalmente (normalizando espacios) en `text`; si no, error."""
    n = norm_ws(needle)
    if n not in text:
        raise ValueError(f"Cita no encontrada en la fuente: {n[:80]}…")
    return n


def write_ledger(module: str, rows: list[dict]) -> None:
    """Escribe docs/claims/claims_{module}.csv (un archivo por módulo, para poder correr módulos en paralelo)
    y reconstruye docs/claims_ledger.csv uniendo todos los módulos."""
    for r in rows:
        r.setdefault("fecha_acceso", TODAY)
        r["modulo"] = module
    CLAIMS_DIR.mkdir(parents=True, exist_ok=True)
    with (CLAIMS_DIR / f"claims_{module}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        w.writerows(rows)
    merge_ledger()


def merge_ledger() -> None:
    allrows = []
    for p in sorted(CLAIMS_DIR.glob("claims_*.csv")):
        with p.open(encoding="utf-8") as f:
            allrows += list(csv.DictReader(f))
    with LEDGER.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        w.writerows(sorted(allrows, key=lambda r: r["claim_id"]))
