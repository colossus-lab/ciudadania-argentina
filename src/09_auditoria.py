"""Auditoría del claims ledger contra las copias locales.

Para cada afirmación de docs/claims_ledger.csv verifica:
  1. que el archivo local exista y su SHA-256 coincida con el registrado;
  2. DATO desde PDF/HTML/TXT: que la cita literal esté en el texto extraído;
  3. DATO desde CSV/JSON/XLSX/ZIP: que el valor del localizador (`valor=...`) se encuentre en el archivo;
  4. ESTIMACIÓN/ESCENARIO/HIPÓTESIS: que los claim_id citados como insumo existan en el ledger.
Escribe docs/auditoria.csv y termina con código 1 si hay fallas.
"""
from __future__ import annotations

import csv
import io
import re
import sys
import zipfile
from pathlib import Path

from common import DOCS, LEDGER, ROOT, local_text, norm_ws, sha256

TEXT_EXT = {".pdf", ".html", ".htm", ".txt", ".xml"}


def _num_variants(v: str) -> set[str]:
    v = v.strip().rstrip(".")
    out = {v}
    try:
        f = float(v.replace(",", ""))
        out |= {repr(f), str(f), f"{f:.0f}", f"{f:.1f}", f"{f:.2f}", f"{f:g}"}
        if f.is_integer():
            out.add(str(int(f)))
    except ValueError:
        pass
    return out


def _value_in_file(path: Path, value: str) -> bool:
    variants = _num_variants(value)
    suf = path.suffix.lower()
    if suf in (".xlsx", ".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                for c in row:
                    if c is None:
                        continue
                    if isinstance(c, (int, float)):
                        if any(_close(c, x) for x in variants):
                            return True
                    elif str(c).strip() in variants:
                        return True
        return False
    if suf == ".xls":
        import pandas as pd
        for df in pd.read_excel(path, sheet_name=None, header=None).values():
            for c in df.to_numpy().ravel():
                if isinstance(c, (int, float)) and any(_close(c, x) for x in variants):
                    return True
                if str(c).strip() in variants:
                    return True
        return False
    if suf == ".zip":
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if n.lower().endswith((".csv", ".txt", ".json")):
                    data = z.read(n).decode("utf-8", errors="ignore")
                    if any(x in data for x in variants):
                        return True
        return False
    data = path.read_text(encoding="utf-8", errors="ignore")
    return any(x in data for x in variants)


def _close(c: float, x: str) -> bool:
    try:
        return abs(float(c) - float(x.replace(",", ""))) <= 1e-6 * max(1.0, abs(float(c)))
    except ValueError:
        return False


def _pairs(cita: str) -> dict:
    """Extrae pares `clave=valor` de un localizador separado por ';'."""
    out = {}
    for part in cita.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip().split(" (")[0].strip()
    return out


def _csv_tables(path: Path, cita: str) -> list:
    """Devuelve [(header, rows)] de un CSV suelto o del CSV nombrado al inicio de la cita dentro de un ZIP."""
    import csv as _csv
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8", errors="ignore") as f:
            rows = list(_csv.reader(f))
        return [(rows[0], rows[1:])] if rows else []
    if path.suffix.lower() == ".zip":
        first = cita.split(";")[0].strip().split(":")[0]
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if n.endswith(first) or Path(n).name == first]
            out = []
            for n in names:
                rows = list(_csv.reader(io.StringIO(z.read(n).decode("utf-8", errors="ignore"))))
                if rows:
                    out.append((rows[0], rows[1:]))
            return out
    return []


def _csv_locator_ok(path: Path, cita: str) -> bool | None:
    pairs = _pairs(cita)
    for header, rows in _csv_tables(path, cita):
        h = [c.strip() for c in header]
        keys = {k: v for k, v in pairs.items() if k in h}
        if len(keys) < 2:
            continue
        multi = {k: v.split("/") for k, v in keys.items()}
        n = max(len(v) for v in multi.values())
        ok_all = True
        for i in range(n):
            want = {k: (v[i] if len(v) == n else v[0]).strip() for k, v in multi.items()}
            idx = {k: h.index(k) for k in want}
            def match(row):
                for k, v in want.items():
                    cell = row[idx[k]].strip() if idx[k] < len(row) else ""
                    if cell != v and not _close_str(cell, v):
                        return False
                return True
            if not any(match(r) for r in rows):
                ok_all = False
        return ok_all
    return None


def _close_str(a: str, b: str) -> bool:
    try:
        return abs(float(a) - float(b.replace(",", ""))) <= 1e-6 * max(1.0, abs(float(a)))
    except ValueError:
        return False


def audit_row(r: dict, ids: set[str], cache: dict) -> tuple[str, str]:
    et = r["etiqueta"].strip().upper()
    cita = r["cita_textual"]
    path = ROOT / r["archivo_local"] if r["archivo_local"] else None
    if et != "DATO":
        refs = set(re.findall(r"\b[A-G]\d{2}\b", cita)) - {r["claim_id"]}
        missing = sorted(refs - ids)
        if missing:
            return "FALLA", f"insumos inexistentes: {', '.join(missing)}"
        if refs:
            return "OK", f"insumos: {', '.join(sorted(refs))}"
        if path and path.exists() and (not r["sha256"] or sha256(path) == r["sha256"]):
            return "OK", "método explícito sobre archivo local verificado (hash)"
        return "REVISAR", "sin insumos citados ni archivo local"
    if not path:
        return "FALLA", "DATO sin archivo local"
    if not path.exists():
        return "FALLA", "archivo local inexistente"
    if r["sha256"] and sha256(path) != r["sha256"]:
        return "FALLA", "SHA-256 no coincide"
    suf = path.suffix.lower()
    if suf in TEXT_EXT:
        if path not in cache:
            cache[path] = local_text(path)
        clean = re.sub(r"\[[^\]]*\]", "", cita)
        parts = [norm_ws(x) for x in clean.split(" | ") if norm_ws(x)]
        missing = [x for x in parts if x not in cache[path]]
        if not missing:
            return "OK", f"{len(parts)} cita(s) literal(es) encontrada(s)"
        return "FALLA", f"cita no encontrada: {missing[0][:60]}"
    loc = _csv_locator_ok(path, cita)
    if loc is True:
        return "OK", "fila del localizador encontrada"
    if loc is False:
        return "FALLA", "fila del localizador no encontrada"
    m = re.search(r"valor(?:_miles)?\s*=\s*([-\d.,eE+]+)", cita)
    if not m:
        return "REVISAR", "localizador no verificable automáticamente"
    return ("OK", f"valor {m.group(1)} encontrado") if _value_in_file(path, m.group(1)) else ("FALLA", f"valor {m.group(1)} no encontrado")


def main() -> int:
    with LEDGER.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    ids = {r["claim_id"] for r in rows}
    cache: dict = {}
    out = []
    for r in rows:
        try:
            status, note = audit_row(r, ids, cache)
        except Exception as e:  # noqa: BLE001
            status, note = "FALLA", f"{type(e).__name__}: {e}"[:200]
        out.append(dict(claim_id=r["claim_id"], modulo=r["modulo"], etiqueta=r["etiqueta"], estado=status, nota=note))
    with (DOCS / "auditoria.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader(); w.writerows(out)
    counts = {s: sum(o["estado"] == s for o in out) for s in ("OK", "REVISAR", "FALLA")}
    print(f"Auditoría: {len(out)} afirmaciones -> {counts}")
    for o in out:
        if o["estado"] != "OK":
            print(f"  {o['claim_id']:5s} {o['estado']:8s} {o['nota']}")
    return 1 if counts["FALLA"] else 0


if __name__ == "__main__":
    sys.exit(main())
