"""Módulo E — ¿Argentina es más "popular" desde Qatar 2022?

Corre de punta a punta desde data/raw (descarga solo lo que falta):
  1. Atención: Wikimedia Pageviews API (agent=user, diaria desde 2015-07-01), 7 artículos + controles.
  2. Google Trends EE.UU. (pytrends): como mucho 2 intentos espaciados; si falla, se registra y no se insiste.
  3. Turismo receptivo: datos.yvera.gob.ar (DNM total país y ETI Ezeiza+Aeroparque) + informes ETI de INDEC.
  4. Tipo de cambio real: BCRA ITCRM (multilateral y bilateral EE.UU.).
  5. Diáspora: Census ACS 1 año, B05006 (nacidos en Argentina), 2010–2024 vía Summary File (la API exige key).
  6. DHS OHSS Yearbook (LPR y naturalizaciones): se intenta; si bloquea, se registra.
  7. NTTO (trade.gov): salidas de ciudadanos de EE.UU. a Sudamérica (el detalle por país es de pago).
Método: ITS (regresión segmentada, HAC Newey-West), quiebres con ruptures (PELT, penalidad tipo BIC),
modelo de turismo log(llegadas) ~ log(ITCRM) + eventos + estacionalidad, y veredicto.
"""
from __future__ import annotations

import csv
import io
import json
import re
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from common import (CHARTS, PROCESSED, RAW, ROOT, TODAY, download, get, local_text, pdf_to_text, quote, raw_path,
                    sha256, write_ledger)

MODULO = "E"
FALLAS: list[dict] = []      # fuentes fallidas (se vuelcan a data/processed/E_fuentes_estado.csv)
ESTADO: list[dict] = []      # estado de todas las fuentes


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def ok(fuente: str, url: str, archivo: Path | str, nota: str = "") -> None:
    ESTADO.append(dict(fecha=TODAY, fuente=fuente, url=url, estado="OK", archivo=str(archivo), nota=nota))


def falla(fuente: str, url: str, error: str, causa: str, accion: str) -> None:
    d = dict(fecha=TODAY, fuente=fuente, url=url, error=error, causa=causa, accion=accion)
    FALLAS.append(d)
    ESTADO.append(dict(fecha=TODAY, fuente=fuente, url=url, estado="FALLA", archivo="", nota=f"{error} | {causa} | {accion}"))


# ----------------------------------------------------------------------------------------------------
# Eventos (fecha de inicio, etiqueta, tipo de fuente, estado de verificación)
# ----------------------------------------------------------------------------------------------------
EVENTOS = [
    # id, fecha, etiqueta corta, descripción, fuente/estado
    ("qatar", "2022-12-18", "Final Qatar", "Final del Mundial Qatar 2022 (Argentina campeón)",
     "S (fecha del evento; FIFA/prensa)"),
    ("messi", "2023-07-15", "Messi-Miami", "Messi se incorpora al Inter Miami (07/2023; se usa el 15/07/2023 como fecha de corte)",
     "S (fecha aproximada al mes, según el plan)"),
    ("balotaje", "2023-11-19", "Balotaje", "Segunda vuelta presidencial (gana Javier Milei)", "S (fecha del evento)"),
    ("asuncion", "2023-12-10", "Asunción Milei", "Asunción de Javier Milei", "S (fecha del evento)"),
    ("copa24", "2024-06-20", "Copa Am. 2024", "Copa América 2024 (20/06–14/07/2024)", "S (fecha del evento)"),
    ("cepo", "2025-04-14", "Fin cepo (PH)", "Com. BCRA \"A\" 8226 (11/04/2025), vigente desde 14/04/2025: acceso al MLC "
     "para personas humanas sin conformidad previa", "P (BCRA, verificado con cita literal)"),
    ("mundial26", "2026-06-11", "Mundial 2026", "Mundial 2026 (EE.UU./México/Canadá), 11/06–19/07/2026. Resultado de "
     "Argentina NO verificado en fuente primaria descargable (fifa.com se renderiza con JavaScript)",
     "S (fechas); resultado: no verificado"),
    ("cbi", "2026-10-02", "Anuncio CBI", "Anuncio del Programa de Ciudadanía por Inversión (Módulo A)", "P (Módulo A)"),
]
EV = {e[0]: pd.Timestamp(e[1]) for e in EVENTOS}

# Ventanas de torneos (pulsos) para no confundir picos de torneo con cambios de nivel
TORNEOS = {
    "wc2018": ("2018-06-14", "2018-07-15"),
    "ca2019": ("2019-06-14", "2019-07-07"),
    "ca2021": ("2021-06-13", "2021-07-10"),
    "wc2022": ("2022-11-20", "2022-12-18"),
    "ca2024": ("2024-06-20", "2024-07-14"),
    "wc2026": ("2026-06-11", "2026-07-19"),
}

# ----------------------------------------------------------------------------------------------------
# 1. Wikimedia Pageviews
# ----------------------------------------------------------------------------------------------------
PV_START, PV_END = "20150701", "20261002"
ARTICULOS = [  # (clave, proyecto, título, rol)
    ("ar_en", "en", "Argentina", "foco"),
    ("ar_es", "es", "Argentina", "foco"),
    ("ar_de", "de", "Argentinien", "foco"),
    ("bsas_en", "en", "Buenos_Aires", "foco"),
    ("messi_en", "en", "Lionel_Messi", "foco"),
    ("milei_en", "en", "Javier_Milei", "foco"),
    ("patagonia_en", "en", "Patagonia", "foco"),
    ("cl_en", "en", "Chile", "control"),
    ("uy_en", "en", "Uruguay", "control"),
    ("br_en", "en", "Brazil", "control"),
    ("co_en", "en", "Colombia", "control"),
    # controles en el mismo idioma para los artículos es/de (robustez)
    ("cl_es", "es", "Chile", "control_es"),
    ("uy_es", "es", "Uruguay", "control_es"),
    ("br_es", "es", "Brasil", "control_es"),
    ("co_es", "es", "Colombia", "control_es"),
    ("cl_de", "de", "Chile", "control_de"),
    ("uy_de", "de", "Uruguay", "control_de"),
    ("br_de", "de", "Brasilien", "control_de"),
    ("co_de", "de", "Kolumbien", "control_de"),
]
PV_URL = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{p}.wikipedia/all-access/user/"
          "{a}/daily/" + PV_START + "/" + PV_END)


def download_retry(url: str, name: str, ext: str, tries: int = 6, wait: int = 15) -> Path:
    """download() de common con reintentos espaciados ante 429 (el rate limit de Wikimedia es por IP compartida)."""
    last = None
    for k in range(tries):
        try:
            return download(url, name, ext)
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(wait * (k + 1))
    raise last  # type: ignore[misc]


def load_pageviews() -> pd.DataFrame:
    series = {}
    for key, proj, title, _rol in ARTICULOS:
        url = PV_URL.format(p=proj, a=title)
        try:
            p = download_retry(url, f"E_wikimedia_pv_{proj}_{title}", "json")
        except Exception as e:  # noqa: BLE001
            falla(f"Wikimedia Pageviews {proj}:{title}", url, str(e)[:120], "rate limit / red", "Se omite el artículo")
            continue
        items = json.loads(p.read_text())["items"]
        s = pd.Series({pd.Timestamp(i["timestamp"][:8]): i["views"] for i in items}, name=key, dtype=float)
        series[key] = s
        ok(f"Wikimedia Pageviews {proj}:{title}", url, rel(p))
    df = pd.DataFrame(series).sort_index()
    df.index.name = "fecha"
    return df


# ----------------------------------------------------------------------------------------------------
# 2. Google Trends (pytrends) — máximo 2 intentos espaciados, sin insistir
# ----------------------------------------------------------------------------------------------------
GT_KW = ["Argentina", "Buenos Aires", "Chile", "Uruguay", "Colombia"]
GT_URL = "https://trends.google.com/trends/explore?date=all&geo=US&q=Argentina,Buenos%20Aires,Chile,Uruguay,Colombia"


def load_gtrends() -> pd.DataFrame | None:
    existing = sorted(RAW.glob("E_gtrends_us_*.csv"))
    if existing:
        ok("Google Trends EE.UU. (CSV)", GT_URL, rel(existing[-1]))
        return pd.read_csv(existing[-1], parse_dates=["date"]).set_index("date")
    log = sorted(RAW.glob("E_gtrends_intentos_*.json"))
    if log:  # ya se intentó y falló: no se insiste (regla del módulo)
        info = json.loads(log[-1].read_text())
        falla("Google Trends vía pytrends", GT_URL, info.get("error", "")[:160], info.get("causa", ""),
              "No se insiste. Exportar CSV a mano (ver docs/modulos/E_popularidad.md)")
        return None
    intentos = []
    for k in range(2):
        try:
            from pytrends.request import TrendReq
            tr = TrendReq(hl="en-US", tz=0, timeout=(10, 30),
                          requests_args={"headers": {"User-Agent": "ColossusLab-Research/1.0 (contacto: dantedeagostino@gmail.com)"}})
            tr.build_payload(GT_KW, timeframe="all", geo="US")
            df = tr.interest_over_time()
            if df is None or df.empty:
                raise RuntimeError("respuesta vacía")
            out = raw_path("E_gtrends_us", "csv")
            df.reset_index().to_csv(out, index=False)
            ok("Google Trends EE.UU. (pytrends)", GT_URL, rel(out))
            return df
        except Exception as e:  # noqa: BLE001
            intentos.append(dict(intento=k + 1, hora=time.strftime("%H:%M:%S"), error=f"{type(e).__name__}: {e}"[:300]))
            if k == 0:
                time.sleep(90)
    err = intentos[-1]["error"]
    causa = "429 / bloqueo de Google a clientes automáticos" if "429" in err or "TooManyRequests" in err else "error de pytrends"
    raw_path("E_gtrends_intentos", "json").write_text(json.dumps(dict(intentos=intentos, error=err, causa=causa), indent=1))
    falla("Google Trends vía pytrends", GT_URL, err[:160], causa,
          "2 intentos espaciados (90 s); no se insiste. Exportar CSV a mano (ver docs/modulos/E_popularidad.md)")
    return None


# ----------------------------------------------------------------------------------------------------
# 3. Turismo receptivo (datos.yvera.gob.ar + INDEC)
# ----------------------------------------------------------------------------------------------------
YV = "https://datos.yvera.gob.ar/dataset/"
URL_DNM = YV + "4cbf7d4a-702a-4911-8c1e-717a45214902/resource/fdfe0ae4-4acc-4421-aa48-6149a02bc615/download/turistas-no-residentes-serie.csv"
URL_ETI_M = YV + ("78b880c1-50d5-4a0c-9c87-7350e70548c2/resource/32cd65c4-7558-48cf-a8ac-bbb07147b5a1/download/"
                  "turistas_pernoctes_estadia_media_turistas_no_residentes_por_residencia_ezeiza_aeroparque_mensual.csv")
URL_ETI_GASTO = YV + ("78b880c1-50d5-4a0c-9c87-7350e70548c2/resource/9a2c43e4-8037-4cf3-8559-bdab2a37ca94/download/"
                      "gasto_total_promedio_diario_por_turista_en_usd_turistas_no_residentes_trimestral_segun_paso.csv")
# Informes técnicos ETI de INDEC (trimestrales: traen gasto por residencia, que yvera no publica)
INDEC_ETI = {
    "2025T1": "https://www.indec.gob.ar/uploads/informesdeprensa/eti_04_257F79FE4B90.pdf",
    "2025T3": "https://www.indec.gob.ar/uploads/informesdeprensa/eti_10_250B9725FF40.pdf",
    "2026T1": "https://www.indec.gob.ar/uploads/informesdeprensa/eti_04_261D31E891A2.pdf",
    "2026T2": "https://www.indec.gob.ar/uploads/informesdeprensa/eti_07_2611F2D28020.pdf",
}
URL_CABA_EEUU = "https://turismo.buenosaires.gob.ar/sites/turismo/files/eeuu_perfiles_internacionales_2025.pdf"
URL_NTTO = "https://www.trade.gov/sites/default/files/2024-02/US-Outbound-to-World-Regions.xlsx"
URL_NTTO_I92 = "https://www.trade.gov/us-international-air-travel-statistics-i-92-data"


def load_turismo() -> dict:
    out = {}
    p = download(URL_DNM, "E_yvera_dnm_turistas_no_residentes", "csv")
    ok("Yvera/DNM — turistas no residentes total país", URL_DNM, rel(p))
    d = pd.read_csv(p, encoding="utf-8-sig", parse_dates=["indice_tiempo"])
    out["dnm_raw"] = d
    out["dnm_path"] = p
    p = download(URL_ETI_M, "E_yvera_eti_no_residentes_mensual", "csv")
    ok("Yvera/INDEC ETI — no residentes Ezeiza+Aeroparque mensual", URL_ETI_M, rel(p))
    out["eti_raw"] = pd.read_csv(p, encoding="utf-8-sig", parse_dates=["indice_tiempo"])
    out["eti_path"] = p
    p = download(URL_ETI_GASTO, "E_yvera_eti_gasto_trimestral", "csv")
    ok("Yvera/INDEC ETI — gasto no residentes por paso, trimestral", URL_ETI_GASTO, rel(p))
    out["gasto_raw"] = pd.read_csv(p, encoding="utf-8-sig", parse_dates=["indice_tiempo"])
    out["gasto_path"] = p
    out["indec"] = {}
    for q, url in INDEC_ETI.items():
        try:
            p = download(url, f"E_indec_eti_{q}", "pdf")
            out["indec"][q] = (p, url)
            ok(f"INDEC ETI informe {q}", url, rel(p))
        except Exception as e:  # noqa: BLE001
            falla(f"INDEC ETI informe {q}", url, str(e)[:120], "descarga", "Se omite")
    try:
        p = download(URL_CABA_EEUU, "E_caba_perfil_eeuu_2025", "pdf")
        out["caba"] = (p, URL_CABA_EEUU)
        ok("Ente de Turismo CABA — Perfil mercado EE.UU. 2025", URL_CABA_EEUU, rel(p))
    except Exception as e:  # noqa: BLE001
        falla("Ente de Turismo CABA — Perfil EE.UU. 2025", URL_CABA_EEUU, str(e)[:120], "descarga", "Se omite")
    p = download(URL_NTTO, "E_ntto_us_outbound_regiones", "xlsx")
    ok("NTTO — U.S. citizen travel to international regions", URL_NTTO, rel(p))
    out["ntto_path"] = p
    p = download(URL_NTTO_I92, "E_ntto_i92_pagina", "html")
    out["i92_path"] = p
    return out


def ntto_south_america(p: Path) -> pd.Series:
    """Primera fila 'South America' (tabla del año) de cada hoja anual 2011+ (metodología APIS comparable desde 2011)."""
    import openpyxl
    wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
    vals = {}
    for name in wb.sheetnames:
        m = re.fullmatch(r"(\d{4})(rev)?", name)
        if not m or int(m.group(1)) < 2011:
            continue
        y = int(m.group(1))
        for row in wb[name].iter_rows(values_only=True):
            if isinstance(row[0], str) and row[0].strip() == "South America":
                for k in range(12):
                    v = row[1 + k]
                    if isinstance(v, (int, float)):
                        vals[pd.Timestamp(year=y, month=k + 1, day=1)] = float(v)
                break
    return pd.Series(vals, name="ntto_us_a_sudamerica").sort_index()


# ----------------------------------------------------------------------------------------------------
# 4. BCRA ITCRM
# ----------------------------------------------------------------------------------------------------
URL_ITCRM = "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/ITCRMSerie.xlsx"
URL_A8226 = "https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A8226.pdf"


def load_itcrm() -> tuple[pd.DataFrame, Path]:
    p = download(URL_ITCRM, "E_bcra_itcrm_serie", "xlsx")
    ok("BCRA ITCRM y bilaterales", URL_ITCRM, rel(p))
    df = pd.read_excel(p, sheet_name="ITCRM y bilaterales prom. mens.", header=1)
    df = df.rename(columns=lambda c: str(c).strip())
    df = df[pd.to_datetime(df["Período"], errors="coerce").notna()].copy()
    df["mes"] = pd.to_datetime(df["Período"]).dt.to_period("M").dt.to_timestamp()
    df = df.set_index("mes")[["ITCRM", "ITCRB Estados Unidos"]].astype(float)
    df.columns = ["itcrm", "itcrb_eeuu"]
    return df, p


# ----------------------------------------------------------------------------------------------------
# 5. Census ACS B05006 (Summary File; la API exige key desde hace poco y la key requiere registro)
# ----------------------------------------------------------------------------------------------------
CB = "https://www2.census.gov/programs-surveys/acs/summary_file"
ACS_YEARS = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024]
URL_CENSUS_API = "https://api.census.gov/data/2023/acs/acs1?get=NAME,B05006_001E&for=us:1"


def acs_seq_year(y: int) -> dict:
    import openpyxl
    import xlrd
    base = f"{CB}/{y}/sequence-based-SF/data/" if y == 2021 else f"{CB}/{y}/data/"
    tpl = sorted(RAW.glob(f"E_acs_{y}_1yr_templates_*.zip"))
    if tpl:
        tpl_url = base + "(templates)"
        ptpl = tpl[-1]
    else:
        html = get(base).text
        n = re.search(r'href="(%d_1yr_Summary_?FileTemplates\.zip)"' % y, html).group(1)
        tpl_url = base + n
        ptpl = download(tpl_url, f"E_acs_{y}_1yr_templates", "zip")
    z = zipfile.ZipFile(ptpl)
    found = {}
    for n in z.namelist():
        if not re.search(r"seq\d+\.xlsx?$", n, re.I):
            continue
        data = z.read(n)
        if n.lower().endswith(".xlsx"):
            ws = openpyxl.load_workbook(io.BytesIO(data), read_only=True).worksheets[0]
            rows = list(ws.iter_rows(values_only=True, max_row=2))
        else:
            sh = xlrd.open_workbook(file_contents=data).sheet_by_index(0)
            rows = [sh.row_values(0), sh.row_values(1)]
        for i, (h, t) in enumerate(zip(rows[0], rows[1])):
            if not (h and re.fullmatch(r"B05006_?0*\d+", str(h))):
                continue
            t = str(t).strip()
            key = None
            if t.endswith("Argentina"):
                key = "argentina"
            elif int(re.sub(r"\D", "", str(h)[6:])) == 1:
                key = "total_extranjeros"
            elif re.search(r"South America:?$", t):
                key = "sudamerica"
            if key and key not in found:
                found[key] = (int(re.search(r"seq(\d+)", n, re.I).group(1)), i, str(h))
    res = dict(anio=y, tipo="sequence-based")
    for key, (seq, col, h) in found.items():
        url = f"{base}1_year_seq_by_state/UnitedStates/{y}1us{seq:04d}000.zip"
        p = download(url, f"E_acs_{y}_1yr_us_seq{seq:04d}", "zip")
        zz = zipfile.ZipFile(p)
        for fn in zz.namelist():
            kind = fn[0]  # e = estimación, m = margen de error (90%)
            for row in csv.reader(io.TextIOWrapper(zz.open(fn), encoding="latin-1")):
                if row[5] == "0000001" and row[2] == "us":
                    res[f"{key}_{'est' if kind == 'e' else 'moe'}"] = float(row[col])
                    break
        res[f"{key}_loc"] = f"{rel(p)} :: {h} (col {col}, LOGRECNO 0000001)"
        res["url"] = url
    return res


def acs_table_year(y: int) -> dict:
    url = f"{CB}/{y}/table-based-SF/data/1YRData/acsdt1y{y}-b05006.dat"
    p = download(url, f"E_acs_{y}_1yr_b05006", "dat")
    surl = f"{CB}/{y}/table-based-SF/documentation/ACS{y}1YR_Table_Shells.txt"
    ps = download(surl, f"E_acs_{y}_1yr_table_shells", "txt")
    shells = pd.read_csv(ps, sep="|", encoding="utf-8-sig", dtype=str)
    sh = shells[shells["Table ID"] == "B05006"]
    line = {"argentina": sh[sh["Label"].str.strip() == "Argentina"]["Unique ID"].iloc[0],
            "sudamerica": sh[sh["Label"].str.strip().str.rstrip(":") == "South America"]["Unique ID"].iloc[0],
            "total_extranjeros": "B05006_001"}
    d = pd.read_csv(p, sep="|", dtype=str)
    us = d[d["GEO_ID"] == "0100000US"].iloc[0]
    res = dict(anio=y, tipo="table-based", url=url)
    for key, uid in line.items():
        num = uid.split("_")[1]
        res[f"{key}_est"] = float(us[f"B05006_E{num}"])
        res[f"{key}_moe"] = float(us[f"B05006_M{num}"])
        res[f"{key}_loc"] = f"{rel(p)} :: GEO_ID=0100000US; columna B05006_E{num}"
    return res


def load_acs() -> pd.DataFrame:
    # Intento con la API (registrado si exige key)
    try:
        r = get(URL_CENSUS_API, allow_redirects=False)
        if r.status_code in (301, 302) and "missing_key" in r.headers.get("Location", ""):
            falla("Census API (api.census.gov) ACS B05006", URL_CENSUS_API, f"HTTP {r.status_code} -> missing_key.html",
                  "La API exige una key (requiere formulario de registro)",
                  "Se usa el ACS Summary File oficial (www2.census.gov), mismas estimaciones")
    except Exception as e:  # noqa: BLE001
        falla("Census API", URL_CENSUS_API, str(e)[:120], "red", "Se usa el Summary File")
    rows = []
    for y in ACS_YEARS:
        try:
            rows.append(acs_table_year(y) if y >= 2022 else acs_seq_year(y))
            ok(f"Census ACS {y} 1 año B05006 (Summary File)", rows[-1]["url"], rows[-1]["argentina_loc"].split(" ::")[0])
        except Exception as e:  # noqa: BLE001
            falla(f"Census ACS {y} Summary File", CB, str(e)[:120], "descarga/parseo", "Se omite el año")
    return pd.DataFrame(rows).set_index("anio")


# ----------------------------------------------------------------------------------------------------
# 6. DHS OHSS Yearbook (LPR y naturalizaciones por país de nacimiento)
# ----------------------------------------------------------------------------------------------------
URL_OHSS = "https://ohss.dhs.gov/topics/immigration/yearbook/2024"
URL_OHSS_LPR = "https://ohss.dhs.gov/system/files/2026-06/2026_0604_ohss_yearbook_lawful_permanent_residents_fy2024.xlsx"
URL_OHSS_NATZ = "https://ohss.dhs.gov/system/files/2026-06/2026_0604_ohss_yearbook_naturalizations_fy2024.xlsx"


def ohss_row(p: Path, sheet: str, header_start: str, country: str = "Argentina") -> dict:
    import openpyxl
    ws = openpyxl.load_workbook(p, read_only=True, data_only=True)[sheet]
    hdr = None
    for row in ws.iter_rows(values_only=True):
        if isinstance(row[0], str) and row[0].strip().startswith(header_start):
            hdr = row
        elif hdr and isinstance(row[0], str) and row[0].strip() == country:
            return {int(h): float(v) for h, v in zip(hdr[1:], row[1:]) if isinstance(h, (int, float)) and v is not None}
    raise ValueError(f"{country} no encontrado en {sheet}")


def load_ohss() -> pd.DataFrame | None:
    """DHS OHSS Yearbook FY2024: Tabla 3 (LPR por país de nacimiento) y Tabla 22 (naturalizaciones por país de nacimiento)."""
    try:
        pl = download(URL_OHSS_LPR, "E_ohss_lpr_fy2024", "xlsx")
        pn = download(URL_OHSS_NATZ, "E_ohss_natz_fy2024", "xlsx")
    except Exception as e:  # noqa: BLE001
        falla("DHS OHSS Yearbook FY2024 (LPR / naturalizaciones)", URL_OHSS, str(e)[:120],
              "Akamai anti-bots intermitente en ohss.dhs.gov", "Reintentar; probar Wayback")
        return None
    ok("DHS OHSS Yearbook FY2024 — LPR (Tabla 3, país de nacimiento)", URL_OHSS_LPR, rel(pl))
    ok("DHS OHSS Yearbook FY2024 — Naturalizaciones (Tabla 22)", URL_OHSS_NATZ, rel(pn))
    lpr = ohss_row(pl, "Table 3", "Region and country of birth")
    nat = ohss_row(pn, "Table 22", "Region and country of birth")
    df = pd.DataFrame({"lpr_nacidos_argentina": lpr, "naturalizaciones_nacidos_argentina": nat})
    df.index.name = "anio_fiscal"
    df.attrs["paths"] = (pl, pn)
    return df


# ====================================================================================================
# ANÁLISIS
# ====================================================================================================
import statsmodels.api as sm  # noqa: E402

HAC_LAGS_D = 30   # rezagos Newey-West, datos diarios
HAC_LAGS_M = 12   # rezagos Newey-West, datos mensuales
CTRL = {"en": ["cl_en", "uy_en", "br_en", "co_en"], "es": ["cl_es", "uy_es", "br_es", "co_es"],
        "de": ["cl_de", "uy_de", "br_de", "co_de"]}
VENTANAS = [  # ventanas descriptivas (sin torneos)
    ("2019 (pre-pandemia)", "2019-01-01", "2019-12-31"),
    ("Base pre-Qatar (ene–oct 2022)", "2022-01-01", "2022-10-31"),
    ("2023 (sin dic-22)", "2023-01-01", "2023-12-31"),
    ("2024 (sin Copa América)", "2024-01-01", "2024-12-31"),
    ("2025", "2025-01-01", "2025-12-31"),
    ("2026 ene–may (pre-Mundial)", "2026-01-01", "2026-05-31"),
    ("2026 ago–sep (post-Mundial)", "2026-08-01", "2026-09-30"),
]


def torneo_mask(idx: pd.DatetimeIndex) -> pd.Series:
    m = pd.Series(False, index=idx)
    for a, b in TORNEOS.values():
        m |= (idx >= pd.Timestamp(a)) & (idx <= pd.Timestamp(b))
    return m


def build_daily(pv: pd.DataFrame) -> pd.DataFrame:
    lg = np.log(pv.where(pv > 0))
    out = pd.DataFrame(index=pv.index)
    out["log_ar_en"] = lg["ar_en"]
    for lang, art in (("en", "ar_en"), ("es", "ar_es"), ("de", "ar_de")):
        out[f"ctrl_{lang}"] = lg[CTRL[lang]].mean(axis=1)
        out[f"D_{lang}"] = lg[art] - out[f"ctrl_{lang}"]
    return out


def ventanas_table(pv: pd.DataFrame, dd: pd.DataFrame) -> pd.DataFrame:
    rows = []
    tm = torneo_mask(pv.index)
    for lab, a, b in VENTANAS:
        sel = (pv.index >= a) & (pv.index <= b) & ~tm.values
        r = dict(ventana=lab, desde=a, hasta=b, dias=int(sel.sum()))
        for k in ["ar_en", "ar_es", "ar_de", "bsas_en", "messi_en", "milei_en", "patagonia_en"] + CTRL["en"]:
            r[f"gm_{k}"] = float(np.exp(np.log(pv.loc[sel, k].where(pv.loc[sel, k] > 0)).mean()))
        for lang in ("en", "es", "de"):
            r[f"relativo_{lang}"] = float(np.exp(dd.loc[sel, f"D_{lang}"].mean()))
        rows.append(r)
    t = pd.DataFrame(rows).set_index("ventana")
    base = t.loc["Base pre-Qatar (ene–oct 2022)"]
    for c in [c for c in t.columns if c.startswith(("gm_", "relativo_"))]:
        t[f"{c}_vs_base_pct"] = 100 * (t[c] / base[c] - 1)
    return t


def design_daily(idx: pd.DatetimeIndex, steps: list[str], slope_at: str | None = None) -> pd.DataFrame:
    X = pd.DataFrame(index=idx)
    t = (idx - idx[0]).days.values / 365.25
    X["const"] = 1.0
    X["tendencia_anual"] = t
    for s in steps:
        X[f"nivel_{s}"] = (idx >= EV[s]).astype(float)
    if slope_at:
        X[f"pendiente_{slope_at}"] = np.where(idx >= EV[slope_at], (idx - EV[slope_at]).days / 365.25, 0.0)
    for k, (a, b) in TORNEOS.items():
        X[f"pulso_{k}"] = ((idx >= pd.Timestamp(a)) & (idx <= pd.Timestamp(b))).astype(float)
    X["pulso_anuncio_cbi"] = (idx >= EV["cbi"]).astype(float)
    for mth in range(2, 13):
        X[f"mes_{mth}"] = (idx.month == mth).astype(float)
    for d in range(1, 7):
        X[f"dow_{d}"] = (idx.dayofweek == d).astype(float)
    return X


def fit_its(y: pd.Series, steps: list[str], slope_at: str | None, lags: int) -> sm.regression.linear_model.RegressionResultsWrapper:
    y = y.dropna()
    X = design_daily(y.index, steps, slope_at)
    X = X.loc[:, X.abs().sum() > 0]
    return sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": lags})


def its_all(dd: pd.DataFrame) -> pd.DataFrame:
    rows = []
    specs = [
        ("M1_segmentada_Qatar", ["qatar"], "qatar"),
        ("M2_multievento", ["qatar", "messi", "balotaje", "cepo"], None),
    ]
    for yname in ["D_en", "D_es", "D_de", "log_ar_en"]:
        for mname, steps, slope in specs:
            res = fit_its(dd[yname], steps, slope, HAC_LAGS_D)
            ci = res.conf_int()
            for term in [c for c in res.params.index if c.startswith(("nivel_", "pendiente_", "tendencia", "pulso_wc2022"))]:
                b = res.params[term]
                rows.append(dict(serie=yname, modelo=mname, termino=term, coef=b, se_hac=res.bse[term], p=res.pvalues[term],
                                 ic95_inf=ci.loc[term, 0], ic95_sup=ci.loc[term, 1], efecto_pct=100 * (np.exp(b) - 1),
                                 efecto_pct_inf=100 * (np.exp(ci.loc[term, 0]) - 1), efecto_pct_sup=100 * (np.exp(ci.loc[term, 1]) - 1),
                                 n=int(res.nobs), r2=res.rsquared, hac_lags=HAC_LAGS_D,
                                 muestra=f"{res.model.data.row_labels[0].date()}..{res.model.data.row_labels[-1].date()}"))
    return pd.DataFrame(rows)


def quiebres(dd: pd.DataFrame, kmax: int = 10) -> pd.DataFrame:
    """Binseg (costo l2) sobre la media semanal, sin las semanas de torneos y sin fijar fechas a priori.
    El número de quiebres K se elige por BIC: n·ln(RSS_K/n) + (2K+1)·ln(n). Se informa además el orden en que
    Binseg detecta cada quiebre (1 = el más fuerte)."""
    import ruptures as rpt
    rows = []
    for yname in ["D_en", "D_es", "D_de", "log_ar_en"]:
        s = dd[yname].copy()
        s[torneo_mask(s.index).values] = np.nan
        w = s.resample("W-SUN").mean().dropna()
        x = w.values.reshape(-1, 1)
        n = len(x)
        algo = rpt.Binseg(model="l2", min_size=12).fit(x)
        bic, sets, orden = {}, {}, {}
        prev: set = set()
        for k in range(0, kmax + 1):
            bks = algo.predict(n_bkps=k) if k else [n]
            segs = zip([0] + bks[:-1], bks)
            rss = sum(float(((x[a:b] - x[a:b].mean()) ** 2).sum()) for a, b in segs)
            bic[k] = n * np.log(rss / n) + (2 * k + 1) * np.log(n)
            sets[k] = bks
            for b in set(bks[:-1]) - prev:
                orden.setdefault(b, k)
            prev = set(bks[:-1])
        kbest = min(bic, key=bic.get)
        bks = sets[kbest]
        starts = [0] + bks[:-1]
        for j, b in enumerate(bks[:-1]):
            fecha = w.index[b]
            dist = {k: (fecha - v).days for k, v in EV.items()}
            near = min(dist, key=lambda k: abs(dist[k]))
            rows.append(dict(serie=yname, metodo="Binseg l2 + BIC", k_bic=kbest, orden_deteccion=orden.get(b),
                             fecha_quiebre=fecha.date(), media_antes=float(x[starts[j]:b].mean()),
                             media_despues=float(x[b:bks[j + 1]].mean()),
                             cambio_pct=100 * (np.exp(float(x[b:bks[j + 1]].mean() - x[starts[j]:b].mean())) - 1),
                             evento_mas_cercano=near, dias_al_evento=dist[near], n_semanas=n))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------------------------
# Turismo
# ----------------------------------------------------------------------------------------------------
def turismo_mensual(t: dict, itcrm: pd.DataFrame) -> pd.DataFrame:
    d = t["dnm_raw"]
    us = d[d["pais_origen"] == "EE.UU. y Canadá"]
    tot = us.groupby("indice_tiempo")["viajes_de_turistas_no_residentes"].sum().rename("dnm_eeuu_can_total")
    aer = us[us["medio_de_transporte"] == "Aérea"].set_index("indice_tiempo")["viajes_de_turistas_no_residentes"].rename("dnm_eeuu_can_aerea")
    all_ = d.groupby("indice_tiempo")["viajes_de_turistas_no_residentes"].sum().rename("dnm_total_no_residentes")
    prov = us.groupby("indice_tiempo")["observaciones"].apply(lambda s: (s == "Dato provisorio").any()).rename("dnm_provisorio")
    e = t["eti_raw"]
    eu = e[e["pais_de_residencia"].str.startswith("EE.UU")].set_index("indice_tiempo")
    df = pd.concat([tot, aer, all_, prov,
                    eu["turistas_no_residentes"].rename("eti_eze_aep_eeuu_can_turistas"),
                    eu["estadia_media_no_residentes"].rename("eti_eze_aep_eeuu_can_estadia"),
                    ntto_south_america(t["ntto_path"]), itcrm], axis=1)
    df.index.name = "mes"
    return df.loc["2010-01-01":"2026-09-01"]


def turismo_modelo(tm: pd.DataFrame) -> pd.DataFrame:
    rows = []
    d = tm.copy()
    d["y"] = np.log(d["dnm_eeuu_can_total"])
    d["log_itcrb_eeuu_l1"] = np.log(d["itcrb_eeuu"]).shift(1)
    d["log_itcrm_l1"] = np.log(d["itcrm"]).shift(1)
    d["log_ntto_sa"] = np.log(d["ntto_us_a_sudamerica"])
    d = d.loc["2014-01-01":"2026-08-01"]
    d = d[~((d.index >= "2020-03-01") & (d.index <= "2022-03-01"))]   # cierre de fronteras y reapertura gradual
    d["tendencia"] = (d.index.year - 2014) + (d.index.month - 1) / 12
    d["post_qatar"] = (d.index >= "2023-01-01").astype(float)
    d["post_milei"] = (d.index >= "2023-12-01").astype(float)
    d["post_cepo"] = (d.index >= "2025-04-01").astype(float)
    d["mundial26"] = d.index.isin(pd.to_datetime(["2026-06-01", "2026-07-01"])).astype(float)
    for m in range(2, 13):
        d[f"mes_{m}"] = (d.index.month == m).astype(float)
    base = ["tendencia", "post_qatar", "post_milei", "post_cepo", "mundial26"] + [f"mes_{m}" for m in range(2, 13)]
    specs = {
        "T1_itcrb_eeuu": ["log_itcrb_eeuu_l1"] + base,
        "T2_itcrm": ["log_itcrm_l1"] + base,
        "T3_itcrb_eeuu+demanda_NTTO": ["log_itcrb_eeuu_l1", "log_ntto_sa"] + base,
    }
    for name, cols in specs.items():
        dd = d.dropna(subset=["y"] + cols)
        res = sm.OLS(dd["y"], sm.add_constant(dd[cols])).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS_M})
        ci = res.conf_int()
        for term in [c for c in cols if not c.startswith("mes_")]:
            b = res.params[term]
            rows.append(dict(modelo=name, termino=term, coef=b, se_hac=res.bse[term], p=res.pvalues[term],
                             ic95_inf=ci.loc[term, 0], ic95_sup=ci.loc[term, 1],
                             efecto_pct=(100 * (np.exp(b) - 1)) if not term.startswith(("log_", "tendencia")) else np.nan,
                             n=int(res.nobs), r2=res.rsquared, muestra=f"{dd.index[0].date()}..{dd.index[-1].date()} (excl. 2020-03..2022-03)"))
    return pd.DataFrame(rows)


def indec_rows(t: dict) -> pd.DataFrame:
    rows = []
    pat = re.compile(r"Estados Unidos y Canadá((?: -?[\d.]+,\d(?:\(\d\))?){8})")
    for q, (p, url) in t["indec"].items():
        txt = pdf_to_text(p)
        anchor = re.search(r"Turismo receptivo\. Cantidad de turistas, estadía promedio, gasto diario promedio y gasto total "
                           r"por país de residencia habitual\. Aeropuerto Internacional de Ezeiza y Aeroparque", txt)
        m = pat.search(txt, anchor.end())
        vals = [float(re.sub(r"\(\d\)", "", v).replace(".", "").replace(",", ".")) for v in m.group(1).split()]
        gasto_musd = vals[6] / 1000 if vals[6] > 5000 else vals[6]   # 2025: miles de USD; 2026: millones de USD
        rows.append(dict(trimestre=q, turistas_miles=vals[0], turistas_var_ia=vals[1], estadia_noches=vals[2],
                         estadia_var_ia=vals[3], gasto_diario_usd=vals[4], gasto_diario_var_ia=vals[5],
                         gasto_total_musd=gasto_musd, gasto_total_var_ia=vals[7],
                         cita=quote(txt, "Estados Unidos y Canadá" + m.group(1)), archivo=p, url=url))
    return pd.DataFrame(rows).set_index("trimestre")
