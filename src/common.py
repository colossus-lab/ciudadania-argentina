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
    existing = sorted(RAW.glob(f"{name}_*.{ext.lstrip('.')}"))
    if existing and not force:
        return existing[-1]
    r = get(url, **kw)
    r.raise_for_status()
    p = raw_path(name, ext)
    p.write_bytes(r.content)
    return p


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]
