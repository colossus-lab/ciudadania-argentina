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
    return p.relative_to(ROOT).as_posix()


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
    ("mundial26", "2026-06-11", "Mundial 2026 (ARG 2.º)", "Mundial 2026 (EE.UU./México/Canadá), 11/06–19/07/2026. Argentina "
     "subcampeón: perdió la final 1-0 ante España en la prórroga (19/07/2026)",
     "Resultado y fecha de la final: P (CONMEBOL, AFA y RFEF vía Wayback; cita literal, E34–E36); inicio del torneo: S"),
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
URL_INDEC_ETI_PAG = "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-13-55"
URL_INDEC_ETI_FRAG = "https://www.indec.gob.ar/Nivel4/Tema/3/13/55"

# ----------------------------------------------------------------------------------------------------
# Mundial 2026: resultado de Argentina. fifa.com (y sus capturas en la Wayback Machine) son un cascarón JS sin el
# texto (`<div id="root"></div>`, sin JSON embebido); cxm-api.fifa.com no se usa (API no documentada). Se usan las
# notas oficiales de la confederación (CONMEBOL) y de las dos federaciones finalistas (AFA, RFEF), en capturas de la
# Wayback Machine (id_ = HTML original sin la barra de archive.org).
# ----------------------------------------------------------------------------------------------------
WB = "https://web.archive.org/web/{ts}id_/{url}"
MUNDIAL26 = {  # clave: (timestamp de la captura, URL original, nombre en data/raw)
    "conmebol": ("20260723035212", "https://www.conmebol.com/noticias/gracias-argentina/", "E_mundial26_conmebol_gracias_argentina"),
    "afa": ("20260720110542", "https://www.afa.com.ar/es/posts/hasta-el-ultimo-aliento-argentina-cayo-de-pie-en-la-final-del-mundial",
            "E_mundial26_afa_final"),
    "rfef": ("20260720000045", "https://rfef.es/es/noticias/espana-bicampeona-del-mundo", "E_mundial26_rfef_bicampeona"),
}


def load_mundial26() -> dict:
    out = {}
    for k, (ts, url, name) in MUNDIAL26.items():
        wb = WB.format(ts=ts, url=url)
        try:
            p = download(wb, name, "html")
            out[k] = (p, wb)
            ok(f"Mundial 2026 — nota oficial {k.upper()} (Wayback {ts})", wb, rel(p))
        except Exception as e:  # noqa: BLE001
            falla(f"Mundial 2026 — nota oficial {k.upper()} (Wayback)", wb, str(e)[:120], "descarga", "Resultado sin esta fuente")
    return out


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
    # La página del programa se lee bien (E29), pero el dato por país es de pago: se registra como fuente no accesible.
    falla("NTTO I-92 / APIS por país de destino", URL_NTTO_I92, "Producto de pago (USD 150 a USD 5.795)", "Licencia comercial",
          "Se usa el agregado gratuito 'South America' como control de demanda (E29)")
    # Página de la ETI en INDEC: el registro anterior apuntaba a Nivel4-Tema-3-13-56 (que es la Encuesta de Ocupación
    # Hotelera). La de la ETI es Nivel4-Tema-3-13-55; su contenido lo carga el propio sitio desde el fragmento HTML
    # /Nivel4/Tema/3/13/55 (el mismo HTML que ve el navegador; no es una API). Se guarda para documentar los cuadros.
    try:
        p = download(URL_INDEC_ETI_FRAG, "E_indec_eti_pagina_nivel4", "html")
        tx = p.read_text(encoding="utf-8", errors="ignore")
        if "Encuesta de Turismo Internacional" not in tx or "eti26_ezeyaerop_cuadros.xls" not in tx:
            raise ValueError("el fragmento no contiene la ETI ni los cuadros 2026")
        out["indec_pag"] = p
        ok("INDEC — página de la ETI (cuadros y series)", URL_INDEC_ETI_PAG, rel(p),
           f"fragmento {URL_INDEC_ETI_FRAG}; lista cuadros por paso (p. ej. eti26_ezeyaerop_cuadros.xls) y series_eti_via_aerea.xlsx")
    except Exception as e:  # noqa: BLE001
        falla("INDEC — página de la ETI", URL_INDEC_ETI_PAG, str(e)[:120], "sitio dinámico", "Se usan yvera (CKAN) y los PDF de informes")
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
    d["y"] = np.log(d["dnm_eeuu_can_total"].where(d["dnm_eeuu_can_total"] > 0))
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


def gtrends_analisis(g: pd.DataFrame) -> pd.DataFrame:
    """Cociente Argentina / promedio de controles (Chile, Uruguay, Colombia), mensual, EE.UU., desde 2016
    (Google Trends cambió su recolección el 01/01/2016 y el 01/01/2022; ver limitaciones)."""
    g = g.copy()
    g = g[g.index < pd.Timestamp(TODAY[:7] + "-01")]   # se descarta el mes en curso (parcial)
    g["ctrl"] = g[["Chile", "Uruguay", "Colombia"]].mean(axis=1)
    g["ratio_ar_ctrl"] = g["Argentina"] / g["ctrl"]
    rows = []
    torneo_meses = set()
    for a, b in TORNEOS.values():
        torneo_meses |= set(pd.date_range(pd.Timestamp(a).to_period("M").to_timestamp(), b, freq="MS"))
    torneo_meses |= {pd.Timestamp("2022-11-01"), pd.Timestamp("2022-12-01")}
    for lab, a, b in VENTANAS:
        sel = g.loc[a:b]
        sel = sel[~sel.index.isin(torneo_meses)]
        rows.append(dict(ventana=lab, meses=len(sel), argentina_media=sel["Argentina"].mean(),
                         controles_media=sel["ctrl"].mean(), ratio_medio=sel["ratio_ar_ctrl"].mean()))
    t = pd.DataFrame(rows).set_index("ventana")
    t["ratio_vs_base_pct"] = 100 * (t["ratio_medio"] / t.loc["Base pre-Qatar (ene–oct 2022)", "ratio_medio"] - 1)
    return g, t


# ----------------------------------------------------------------------------------------------------
# Gráficos (matplotlib, fondo blanco, PNG 150 dpi + SVG, fuente al pie)
# ----------------------------------------------------------------------------------------------------
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
C1, C2, C3, CGRAY = "#2a78d6", "#eb6834", "#1baf7a", "#9a9993"
EV_PLOT = ["qatar", "messi", "balotaje", "copa24", "cepo", "mundial26"]


def _style():
    import matplotlib as mpl
    mpl.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "grid.linestyle": "-",
        "axes.spines.top": False, "axes.spines.right": False, "font.size": 9, "axes.titlesize": 10,
        "lines.linewidth": 1.6, "lines.solid_capstyle": "round", "legend.frameon": False,
        "svg.fonttype": "none", "font.family": "DejaVu Sans"})


def _events(ax, keys=EV_PLOT, ymax_frac=0.98):
    import matplotlib.transforms as mt
    tr = mt.blended_transform_factory(ax.transData, ax.transAxes)
    lab = {e[0]: e[2] for e in EVENTOS}
    for i, k in enumerate(keys):
        ax.axvline(EV[k], color="#b9b8b2", lw=0.8, zorder=0)
        ax.text(EV[k], ymax_frac - 0.07 * (i % 2), " " + lab[k], transform=tr, fontsize=7, color=INK2, va="top", ha="left")


def _save(fig, name, fuente):
    fig.text(0.01, 0.01, f"Fuente: {fuente}. Elaboración: Colossus Lab.", fontsize=7, color=INK2, ha="left", va="bottom")
    CHARTS.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(CHARTS / f"E_{name}.{ext}", dpi=150)
    import matplotlib.pyplot as plt
    plt.close(fig)


def charts(pv, dd, gt, tm, acs, ohss, its):
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    _style()
    WM = "Wikimedia Pageviews API (agent=user)"
    # 1. Artículo Argentina en/es/de, media diaria mensual (escala log)
    mo = pv.resample("MS").mean()
    fig, ax = plt.subplots(figsize=(10, 5.2))
    for k, c, lab in (("ar_en", C1, "en: Argentina"), ("ar_es", C2, "es: Argentina"), ("ar_de", C3, "de: Argentinien")):
        ax.plot(mo.index, mo[k], color=c, label=lab)
        ax.text(mo.index[-1], mo[k].iloc[-1], f"  {lab}", color=INK, fontsize=8, va="center")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
    ax.set_ylabel("Vistas diarias promedio del mes (escala log)")
    _events(ax)
    ax.legend(loc="lower left", fontsize=8)
    ax.set_xlim(mo.index[0], mo.index[-1] + pd.Timedelta(days=500))
    ax.set_title("El artículo 'Argentina' tiene picos en cada torneo y vuelve a su nivel: en 2026 está por debajo de 2022",
                 loc="left", color=INK)
    fig.subplots_adjust(bottom=0.12, top=0.92, left=0.08, right=0.97)
    _save(fig, "pageviews_argentina_eventos", WM)

    # 2. Argentina relativo a controles (índice base pre-Qatar = 100), mensual, sin días de torneo
    tmask = torneo_mask(dd.index)
    rel_ = dd[["D_en", "D_es", "D_de"]].copy()
    rel_[tmask.values] = np.nan
    rm = rel_.resample("MS").mean()
    base = rel_.loc["2022-01-01":"2022-10-31"].mean()
    idx = 100 * np.exp(rm - base)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    for k, c, lab in (("D_en", C1, "en (vs Chile, Uruguay, Brazil, Colombia)"), ("D_es", C2, "es (vs mismos países)"),
                      ("D_de", C3, "de (vs mismos países)")):
        ax.plot(idx.index, idx[k], color=c, label=lab)
    ax.axhline(100, color=INK2, lw=0.8)
    ax.set_ylabel("Índice: vistas de 'Argentina' / media geométrica de controles\n(ene–oct 2022 = 100; sin días de torneo)")
    _events(ax)
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title("Frente a sus vecinos, la atención relativa a Argentina subió tras Qatar y en 2025–26 volvió cerca de la base",
                 loc="left", color=INK)
    fig.subplots_adjust(bottom=0.12, top=0.92, left=0.09, right=0.97)
    _save(fig, "argentina_vs_controles", WM + "; controles en/es/de")

    # 3. Temas: Messi, Milei, Buenos Aires, Patagonia (small multiples)
    fig, axs = plt.subplots(2, 2, figsize=(10, 6), sharex=True)
    for ax, (k, lab) in zip(axs.flat, (("messi_en", "Lionel Messi (en)"), ("milei_en", "Javier Milei (en)"),
                                        ("bsas_en", "Buenos Aires (en)"), ("patagonia_en", "Patagonia (en)"))):
        ax.plot(mo.index, mo[k], color=C1)
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
        ax.yaxis.set_minor_formatter(plt.NullFormatter())
        ax.set_title(lab, loc="left", fontsize=9, color=INK)
        for e in EV_PLOT:
            ax.axvline(EV[e], color="#b9b8b2", lw=0.8, zorder=0)
    fig.suptitle("Messi y Milei concentran la atención en sus propios artículos; Buenos Aires y Patagonia no despegan",
                 x=0.01, ha="left", color=INK, fontsize=10)
    fig.text(0.01, 0.035, "Líneas verticales: final Qatar, Messi-Miami, balotaje, Copa América 2024, fin del cepo (PH), Mundial 2026. "
             "Vistas diarias promedio del mes, escala log.", fontsize=7, color=INK2)
    fig.subplots_adjust(bottom=0.12, top=0.9, left=0.07, right=0.98, hspace=0.3)
    _save(fig, "pageviews_temas", WM)

    # 4. Google Trends EE.UU.
    if gt is not None:
        fig, ax = plt.subplots(figsize=(10, 4.8))
        g = gt.loc["2016-01-01":]
        ax.plot(g.index, g["ratio_ar_ctrl"], color=C1)
        ax.axhline(1, color=INK2, lw=0.8)
        ax.set_ylabel("Interés de búsqueda 'Argentina' / promedio\n(Chile, Uruguay, Colombia), EE.UU.")
        _events(ax)
        ax.set_title("En Google (EE.UU.), fuera de los torneos el interés relativo por Argentina sube sólo un escalón moderado",
                     loc="left", color=INK)
        fig.subplots_adjust(bottom=0.13, top=0.9, left=0.09, right=0.97)
        _save(fig, "google_trends_eeuu", "Google Trends (pytrends), geo=US, mensual, índice 0–100")

    # 5. Turismo: dos paneles (sin doble eje)
    t12 = tm[["dnm_eeuu_can_total", "ntto_us_a_sudamerica"]].rolling(12, min_periods=12).sum()
    b19 = t12.loc["2019-12-01"]
    ti = 100 * t12 / b19
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    a1.plot(ti.index, ti["dnm_eeuu_can_total"], color=C1, label="Llegadas a Argentina de residentes de EE.UU. y Canadá (DNM, todas las vías)")
    a1.plot(ti.index, ti["ntto_us_a_sudamerica"], color=CGRAY, label="Salidas aéreas de ciudadanos de EE.UU. a Sudamérica (NTTO)")
    a1.axhline(100, color=INK2, lw=0.8)
    a1.set_ylabel("Suma móvil 12 meses\n(año 2019 = 100)")
    a1.legend(loc="lower left", fontsize=8)
    _events(a1)
    yr = tm[["dnm_eeuu_can_total", "ntto_us_a_sudamerica"]].resample("YE").sum(min_count=12)
    g_ar = 100 * (yr.loc["2025-12-31", "dnm_eeuu_can_total"] / yr.loc["2019-12-31", "dnm_eeuu_can_total"] - 1)
    g_sa = 100 * (yr.loc["2025-12-31", "ntto_us_a_sudamerica"] / yr.loc["2019-12-31", "ntto_us_a_sudamerica"] - 1)
    a1.set_title(f"Turismo de EE.UU.+Canadá a Argentina: {pct(g_ar, 0)} vs 2019 en 2025, contra {pct(g_sa, 0)} del viaje de EE.UU. a Sudamérica",
                 loc="left", color=INK, fontsize=9.5)
    a2.plot(tm.index, tm["itcrb_eeuu"], color=C2)
    a2.set_ylabel("ITCR bilateral EE.UU.\n(17-12-15 = 100; más alto = AR más barata)")
    for e in EV_PLOT:
        a2.axvline(EV[e], color="#b9b8b2", lw=0.8, zorder=0)
    a2.set_xlim(pd.Timestamp("2015-01-01"), tm.index[-1])
    fig.subplots_adjust(bottom=0.09, top=0.94, left=0.1, right=0.93, hspace=0.12)
    _save(fig, "turismo_eeuu_itcrm", "datos.yvera.gob.ar (DNM/INDEC), NTTO trade.gov, BCRA ITCRM")

    # 6. Diáspora y migración
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.6))
    a = acs.copy()
    a1.errorbar(a.index, a["argentina_est"] / 1000, yerr=a["argentina_moe"] / 1000, fmt="o", color=C1, ms=5,
                ecolor=CGRAY, elinewidth=1, capsize=0, mec="white", mew=1.5)
    a1.set_title("Nacidos en Argentina residentes en EE.UU. (miles)", loc="left", fontsize=9, color=INK)
    a1.set_xticks([2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024])
    a1.text(2020, a["argentina_est"].min() / 1000, "2020: sin ACS 1 año", fontsize=7, color=INK2, ha="center")
    if ohss is not None:
        a2.plot(ohss.index, ohss["lpr_nacidos_argentina"], color=C1, marker="o", ms=4, label="Residencias permanentes (LPR)")
        a2.plot(ohss.index, ohss["naturalizaciones_nacidos_argentina"], color=C2, marker="o", ms=4, label="Naturalizaciones")
        a2.legend(loc="upper left", fontsize=8)
        a2.set_title("Nacidos en Argentina: LPR y naturalizaciones (año fiscal)", loc="left", fontsize=9, color=INK)
    fig.suptitle("La diáspora argentina en EE.UU. crece despacio; las green cards a argentinos subieron en FY2023–24",
                 x=0.01, ha="left", color=INK, fontsize=10)
    fig.subplots_adjust(bottom=0.14, top=0.84, left=0.07, right=0.98, wspace=0.25)
    _save(fig, "diaspora_eeuu", "Census ACS 1 año B05006 (Summary File; barras = MOE 90%); DHS OHSS Yearbook FY2024 tablas 3 y 22")

    # 7. Coeficientes ITS (modelo multievento)
    m2 = its[(its["modelo"] == "M2_multievento") & its["termino"].str.startswith("nivel_")]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    terms = ["nivel_qatar", "nivel_messi", "nivel_balotaje", "nivel_cepo"]
    names = {"nivel_qatar": "Post final Qatar", "nivel_messi": "Post Messi-Miami", "nivel_balotaje": "Post balotaje (Milei)",
             "nivel_cepo": "Post fin del cepo (PH)"}
    off = {"D_en": -0.2, "D_es": 0.0, "D_de": 0.2}
    col = {"D_en": C1, "D_es": C2, "D_de": C3}
    for s_, o in off.items():
        sub = m2[m2["serie"] == s_].set_index("termino").loc[terms]
        y = np.arange(len(terms)) + o
        ax.errorbar(sub["efecto_pct"], y, xerr=[sub["efecto_pct"] - sub["efecto_pct_inf"], sub["efecto_pct_sup"] - sub["efecto_pct"]],
                    fmt="o", color=col[s_], ecolor=col[s_], elinewidth=1.2, ms=5, mec="white", mew=1.5,
                    label={"D_en": "en", "D_es": "es", "D_de": "de"}[s_] + " (relativo a controles)")
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(range(len(terms)))
    ax.set_yticklabels([names[t] for t in terms])
    ax.invert_yaxis()
    ax.set_xlabel("Cambio de nivel estimado (%), IC 95% HAC Newey-West — ESTIMACIÓN")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title("Sólo Qatar deja un escalón positivo; los eventos posteriores lo erosionan", loc="left", color=INK)
    fig.subplots_adjust(bottom=0.16, top=0.9, left=0.22, right=0.97)
    _save(fig, "its_coeficientes", WM + "; regresión segmentada propia")


# ----------------------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------------------
def fmt(x: float, d: int = 0) -> str:
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x: float, d: int = 1) -> str:
    return ("+" if x >= 0 else "") + fmt(x, d) + "%"


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    claims: list[dict] = []

    def add(cid, etq, afirm, valor, fuente, tipo, url, archivo, cita):
        p = Path(archivo) if archivo else None
        claims.append(dict(claim_id=cid, etiqueta=etq, afirmacion=afirm, valor=valor, fuente=fuente, tipo_fuente=tipo, url=url,
                           archivo_local=rel(p) if p and p.is_absolute() else (archivo or ""),
                           sha256=sha256(p if p.is_absolute() else ROOT / p) if p else "", cita_textual=cita))

    # --- Datos ---
    pv = load_pageviews()
    gt_raw = load_gtrends()
    t = load_turismo()
    itcrm, p_itcrm = load_itcrm()
    acs = load_acs()
    ohss = load_ohss()
    p_a8226 = download(URL_A8226, "E_bcra_com_A8226", "pdf")
    ok("BCRA Comunicación A 8226", URL_A8226, rel(p_a8226))
    m26 = load_mundial26()

    # --- Atención ---
    dd = build_daily(pv)
    pv.to_csv(PROCESSED / "E_pageviews_diarias.csv")
    pv.resample("MS").mean().round(1).to_csv(PROCESSED / "E_pageviews_mensuales.csv")
    dd.round(5).to_csv(PROCESSED / "E_atencion_relativa_diaria.csv")
    vt = ventanas_table(pv, dd)
    vt.round(3).to_csv(PROCESSED / "E_atencion_ventanas.csv")
    its = its_all(dd)
    its.to_csv(PROCESSED / "E_its_resultados.csv", index=False)
    qb = quiebres(dd)
    qb.to_csv(PROCESSED / "E_quiebres.csv", index=False)
    pd.DataFrame([dict(id=e[0], fecha=e[1], etiqueta=e[2], descripcion=e[3], fuente_estado=e[4]) for e in EVENTOS]).to_csv(
        PROCESSED / "E_eventos.csv", index=False)

    gt, gtw = (None, None)
    if gt_raw is not None:
        gt, gtw = gtrends_analisis(gt_raw)
        gt.round(4).to_csv(PROCESSED / "E_google_trends_eeuu.csv")
        gtw.round(4).to_csv(PROCESSED / "E_google_trends_ventanas.csv")

    # --- Turismo ---
    tm = turismo_mensual(t, itcrm)
    tm.to_csv(PROCESSED / "E_turismo_mensual.csv")
    tmod = turismo_modelo(tm)
    tmod.to_csv(PROCESSED / "E_turismo_modelo.csv", index=False)
    ind = indec_rows(t)
    ind.drop(columns=["archivo"]).to_csv(PROCESSED / "E_indec_eti_eeuu_canada_trimestral.csv")
    anual = tm.resample("YE").sum(min_count=12)[["dnm_eeuu_can_total", "dnm_eeuu_can_aerea", "dnm_total_no_residentes",
                                                  "eti_eze_aep_eeuu_can_turistas", "ntto_us_a_sudamerica"]]
    anual.index = anual.index.year
    for c in ["dnm_eeuu_can_total", "dnm_eeuu_can_aerea", "ntto_us_a_sudamerica", "dnm_total_no_residentes"]:
        anual[f"{c}_vs2019_pct"] = 100 * (anual[c] / anual.loc[2019, c] - 1)
    anual.round(2).to_csv(PROCESSED / "E_turismo_anual.csv")
    jan_aug = {y: tm.loc[f"{y}-01-01":f"{y}-08-01", "dnm_eeuu_can_total"].sum() for y in (2019, 2024, 2025, 2026)}

    # --- Diáspora ---
    acs.drop(columns=[c for c in acs.columns if c.endswith("_loc")]).to_csv(PROCESSED / "E_diaspora_acs_b05006.csv")
    if ohss is not None:
        ohss.to_csv(PROCESSED / "E_dhs_lpr_naturalizaciones.csv")

    # --- Gráficos ---
    charts(pv, dd, gt, tm, acs, ohss, its)

    # =========================== CLAIMS ===========================
    WMF = "Wikimedia Pageviews API, agent=user, all-access, diaria"
    fpv = lambda proj, a: sorted(RAW.glob(f"E_wikimedia_pv_{proj}_{a}_*.json"))[-1]  # noqa: E731
    url_pv = lambda proj, a: PV_URL.format(p=proj, a=a)  # noqa: E731
    v = int(pv.loc["2022-12-18", "ar_en"])
    add("E01", "DATO", "Pico diario de vistas del artículo 'Argentina' (Wikipedia en inglés): día de la final de Qatar", fmt(v),
        WMF, "P", url_pv("en", "Argentina"), fpv("en", "Argentina"), f"items[timestamp=2022121800].views; valor={v}")
    v2 = int(pv.loc["2026-07-19", "ar_en"])
    add("E02", "DATO", "Vistas del artículo 'Argentina' (en) el 19/07/2026, día de la final del Mundial 2026 (2.º mayor registro diario de la serie)",
        fmt(v2), WMF, "P", url_pv("en", "Argentina"), fpv("en", "Argentina"), f"items[timestamp=2026071900].views; valor={v2}")
    b = "Base pre-Qatar (ene–oct 2022)"
    r25, r26 = vt.loc["2025", "gm_ar_en_vs_base_pct"], vt.loc["2026 ago–sep (post-Mundial)", "gm_ar_en_vs_base_pct"]
    add("E03", "ESTIMACIÓN", "Vistas diarias del artículo 'Argentina' (en), media geométrica sin días de torneo, frente a ene–oct 2022",
        f"2023 {pct(vt.loc['2023 (sin dic-22)', 'gm_ar_en_vs_base_pct'])}; 2025 {pct(r25)}; ago–sep 2026 {pct(r26)}",
        WMF, "P", url_pv("en", "Argentina"), "data/processed/E_atencion_ventanas.csv",
        "exp(mean(log(vistas))) por ventana / misma métrica en ene–oct 2022 − 1; insumo E01 (misma serie); ventanas en E_atencion_ventanas.csv")
    ctrl25 = np.mean([vt.loc["2025", f"gm_{k}_vs_base_pct"] for k in CTRL["en"]])
    add("E04", "ESTIMACIÓN", "Los artículos de control (Chile, Uruguay, Brazil, Colombia, en) también caen: promedio simple de sus variaciones 2025 vs ene–oct 2022",
        pct(ctrl25), WMF, "P", url_pv("en", "Chile"), "data/processed/E_atencion_ventanas.csv",
        "promedio de gm_{cl,uy,br,co}_en_vs_base_pct, fila 2025")
    add("E05", "ESTIMACIÓN", "Atención relativa a 'Argentina' (en) vs controles, índice ene–oct 2022 = 100",
        f"2023 {pct(vt.loc['2023 (sin dic-22)', 'relativo_en_vs_base_pct'])}; 2024 {pct(vt.loc['2024 (sin Copa América)', 'relativo_en_vs_base_pct'])}; "
        f"2025 {pct(vt.loc['2025', 'relativo_en_vs_base_pct'])}; ago–sep 2026 {pct(vt.loc['2026 ago–sep (post-Mundial)', 'relativo_en_vs_base_pct'])}",
        WMF, "P", url_pv("en", "Argentina"), "data/processed/E_atencion_ventanas.csv",
        "exp(mean(D_en)) por ventana / base − 1, con D_en = log(vistas Argentina) − media(log vistas controles); sin días de torneo")
    add("E06", "ESTIMACIÓN", "Atención relativa 2025 vs ene–oct 2022 en otros idiomas (es: vs Chile/Uruguay/Brasil/Colombia; de: ídem)",
        f"es {pct(vt.loc['2025', 'relativo_es_vs_base_pct'])}; de {pct(vt.loc['2025', 'relativo_de_vs_base_pct'])}",
        WMF, "P", url_pv("es", "Argentina"), "data/processed/E_atencion_ventanas.csv", "Ídem E05 con D_es y D_de")
    r = its[(its.serie == "D_en") & (its.modelo == "M1_segmentada_Qatar")].set_index("termino")
    lvl, slo = r.loc["nivel_qatar"], r.loc["pendiente_qatar"]
    t_zero = EV["qatar"] + pd.Timedelta(days=float(-lvl.coef / slo.coef * 365.25))
    add("E07", "ESTIMACIÓN", "ITS segmentada (D_en): salto de nivel tras la final de Qatar y cambio de pendiente posterior; fecha en que el efecto se anula",
        f"nivel {pct(lvl.efecto_pct)} [IC95 {pct(lvl.efecto_pct_inf)}; {pct(lvl.efecto_pct_sup)}]; pendiente {fmt(slo.coef * 100, 1)} pp log/año "
        f"(p={lvl.p:.3f}/{slo.p:.3f}); efecto neto ≈ 0 hacia {t_zero:%m/%Y}",
        "Regresión propia sobre " + WMF, "P", url_pv("en", "Argentina"), "data/processed/E_its_resultados.csv",
        "OLS D_en ~ tendencia + nivel_qatar + pendiente_qatar + pulsos de torneos + dummies mes y día; HAC Newey-West 30 rezagos; "
        "fecha cero = 18/12/2022 + (−nivel/pendiente) años")
    m2 = its[(its.serie == "D_en") & (its.modelo == "M2_multievento")].set_index("termino")
    add("E08", "ESTIMACIÓN", "ITS multievento (D_en): cambios de nivel acumulativos por evento",
        "; ".join(f"{k.replace('nivel_', '')} {pct(m2.loc[k, 'efecto_pct'])} (p={m2.loc[k, 'p']:.2f})"
                  for k in ["nivel_qatar", "nivel_messi", "nivel_balotaje", "nivel_cepo"]),
        "Regresión propia sobre " + WMF, "P", url_pv("en", "Argentina"), "data/processed/E_its_resultados.csv",
        "OLS D_en ~ tendencia + escalones (qatar 18/12/22, messi 15/07/23, balotaje 19/11/23, cepo 14/04/25) + pulsos + mes + día; HAC 30")
    cc = its[(its.modelo == "M2_multievento") & its.termino.isin(["nivel_qatar", "nivel_cepo"]) & its.serie.isin(["D_en", "D_es", "D_de"])]
    add("E09", "ESTIMACIÓN", "Robustez por idioma (M2): escalón Qatar y escalón post-cepo en en/es/de",
        "; ".join(f"{row.serie} {row.termino.replace('nivel_', '')} {pct(row.efecto_pct)}" for row in cc.itertuples()),
        "Regresión propia sobre " + WMF, "P", url_pv("de", "Argentinien"), "data/processed/E_its_resultados.csv", "Ídem E08 para D_es y D_de")
    qe = qb[qb.serie == "D_en"]
    add("E10", "ESTIMACIÓN", "Quiebres estructurales sin fecha a priori (Binseg l2 + BIC, semanal, D_en sin semanas de torneo)",
        "; ".join(f"{r_.fecha_quiebre} ({pct(r_.cambio_pct)}, evento más cercano: {r_.evento_mas_cercano} a {r_.dias_al_evento} d)"
                  for r_ in qe.itertuples()),
        "Cálculo propio sobre " + WMF, "P", url_pv("en", "Argentina"), "data/processed/E_quiebres.csv",
        "ruptures.Binseg(model='l2', min_size=12); K = argmin n·ln(RSS/n) + (2K+1)·ln(n), K≤10")
    if gt is not None:
        pg = sorted(RAW.glob("E_gtrends_us_*.csv"))[-1]
        add("E11", "DATO", "Google Trends EE.UU.: interés en 'Argentina' (índice 0–100 relativo al máximo del período 2004–2026)",
            f"dic-2022 = {int(gt_raw.loc['2022-12-01', 'Argentina'])}; jul-2026 = {int(gt_raw.loc['2026-07-01', 'Argentina'])}; "
            f"sep-2026 = {int(gt_raw.loc['2026-09-01', 'Argentina'])}", "Google Trends vía pytrends (geo=US, date=all)", "R", GT_URL, pg,
            f"date=2022-12-01/2026-07-01/2026-09-01; Argentina={int(gt_raw.loc['2022-12-01', 'Argentina'])}/"
            f"{int(gt_raw.loc['2026-07-01', 'Argentina'])}/{int(gt_raw.loc['2026-09-01', 'Argentina'])}")
        add("E12", "ESTIMACIÓN", "Google Trends EE.UU.: cociente Argentina / promedio(Chile, Uruguay, Colombia) sin meses de torneo, vs ene–oct 2022",
            "; ".join(f"{k} {pct(gtw.loc[k, 'ratio_vs_base_pct'])}" for k in ["2023 (sin dic-22)", "2024 (sin Copa América)", "2025",
                                                                               "2026 ago–sep (post-Mundial)"]),
            "Cálculo propio sobre Google Trends", "R", GT_URL, "data/processed/E_google_trends_ventanas.csv",
            "media mensual de Argentina/mean(Chile,Uruguay,Colombia) por ventana / base − 1; insumo E11")
    pdnm = rel(t["dnm_path"])
    add("E13", "ESTIMACIÓN", "Llegadas de turistas residentes en EE.UU. y Canadá, total país (DNM, todas las vías), suma anual",
        f"2019 {fmt(anual.loc[2019, 'dnm_eeuu_can_total'])}; 2023 {fmt(anual.loc[2023, 'dnm_eeuu_can_total'])}; "
        f"2024 {fmt(anual.loc[2024, 'dnm_eeuu_can_total'])}; 2025 {fmt(anual.loc[2025, 'dnm_eeuu_can_total'])} "
        f"({pct(100 * (anual.loc[2025, 'dnm_eeuu_can_total'] / anual.loc[2024, 'dnm_eeuu_can_total'] - 1))} vs 2024)",
        "datos.yvera.gob.ar — Turismo internacional total país (DNM)", "P", URL_DNM, pdnm,
        "suma de viajes_de_turistas_no_residentes con pais_origen='EE.UU. y Canadá' (3 medios), por año calendario")
    add("E14", "ESTIMACIÓN", "Llegadas EE.UU.+Canadá ene–ago 2026 vs ene–ago 2025 (2025–26 = dato provisorio)",
        f"{fmt(jan_aug[2026])} vs {fmt(jan_aug[2025])} ({pct(100 * (jan_aug[2026] / jan_aug[2025] - 1))}); ene–ago 2019: {fmt(jan_aug[2019])}",
        "datos.yvera.gob.ar — DNM", "P", URL_DNM, pdnm, "suma ene–ago por año; insumo E13")
    add("E15", "ESTIMACIÓN", "Recuperación vs 2019: llegadas EE.UU.+Canadá a Argentina vs salidas aéreas de ciudadanos de EE.UU. a Sudamérica (NTTO)",
        f"Argentina 2023 {pct(anual.loc[2023, 'dnm_eeuu_can_total_vs2019_pct'])}, 2025 {pct(anual.loc[2025, 'dnm_eeuu_can_total_vs2019_pct'])}; "
        f"EE.UU.→Sudamérica 2023 {pct(anual.loc[2023, 'ntto_us_a_sudamerica_vs2019_pct'])}, 2025 {pct(anual.loc[2025, 'ntto_us_a_sudamerica_vs2019_pct'])}",
        "DNM (yvera) y NTTO trade.gov", "P", URL_NTTO, rel(t["ntto_path"]),
        "suma anual / suma 2019 − 1 para cada serie; NTTO: primera fila 'South America' de cada hoja anual; insumo E13")
    v = tm.loc["2026-08-01", "dnm_eeuu_can_aerea"]
    add("E16", "DATO", "Llegadas por vía aérea de residentes en EE.UU. y Canadá, agosto 2026, total país (dato provisorio)", fmt(v),
        "datos.yvera.gob.ar — DNM", "P", URL_DNM, pdnm,
        f"indice_tiempo=2026-08-01; medio_de_transporte=Aérea; pais_origen=EE.UU. y Canadá; viajes_de_turistas_no_residentes={int(v)}")
    for cid, q in zip(["E17", "E18", "E19", "E20"], ["2025T1", "2025T3", "2026T1", "2026T2"]):
        rr = ind.loc[q]
        add(cid, "DATO", f"INDEC ETI {q}, Ezeiza y Aeroparque, turismo receptivo de residentes en EE.UU. y Canadá: turistas (miles), var. i.a., "
            "estadía, gasto diario, gasto total", f"{fmt(rr.turistas_miles, 1)} mil ({pct(rr.turistas_var_ia)}); estadía {fmt(rr.estadia_noches, 1)} n; "
            f"gasto diario USD {fmt(rr.gasto_diario_usd, 1)}; gasto total USD {fmt(rr.gasto_total_musd, 1)} M ({pct(rr.gasto_total_var_ia)})",
            f"INDEC, Estadísticas de turismo internacional ({q})", "P", rr.url, rr.archivo, rr.cita)
    if "caba" in t:
        pc, uc = t["caba"]
        tc = local_text(pc)
        add("E21", "DATO", "Ente de Turismo CABA: llegadas de turistas estadounidenses a la Ciudad en 2025 (puesto #3) y variación interanual",
            "284.609 (−11% i.a.)", "Ente de Turismo de la Ciudad de Buenos Aires, Perfil de mercado EE.UU. 2025", "P", uc, pc,
            quote(tc, "284.609") + " | " + quote(tc, "(-11% i.a.)") + " | " + quote(tc, "LLEGADAS DE TURISTAS ESTADOUNIDENSE EN 2025"))
    add("E22", "DATO", "Tipo de cambio real bilateral con EE.UU. (BCRA, prom. mensual, base 17-12-15=100; más alto = Argentina más barata)",
        f"dic-2022 {fmt(itcrm.loc['2022-12-01', 'itcrb_eeuu'], 1)}; ene-2024 {fmt(itcrm.loc['2024-01-01', 'itcrb_eeuu'], 1)}; "
        f"abr-2025 {fmt(itcrm.loc['2025-04-01', 'itcrb_eeuu'], 1)}; sep-2026 {fmt(itcrm.loc['2026-09-01', 'itcrb_eeuu'], 1)}",
        "BCRA, ITCRMSerie.xlsx, hoja 'ITCRM y bilaterales prom. mens.'", "P", URL_ITCRM, p_itcrm,
        f"hoja 'ITCRM y bilaterales prom. mens.'; columna 'ITCRB Estados Unidos'; período 2024-01-31; valor={float(itcrm.loc['2024-01-01', 'itcrb_eeuu'])!r}; "
        f"período 2026-09-30 -> {float(itcrm.loc['2026-09-01', 'itcrb_eeuu'])!r}")
    tt = tmod.set_index(["modelo", "termino"])
    e1 = tt.loc[("T1_itcrb_eeuu", "log_itcrb_eeuu_l1")]
    q1, q3 = tt.loc[("T1_itcrb_eeuu", "post_qatar")], tt.loc[("T3_itcrb_eeuu+demanda_NTTO", "post_qatar")]
    add("E23", "ESTIMACIÓN", "Modelo de turismo: elasticidad de llegadas EE.UU.+Canadá al ITCR bilateral (t−1) y escalón post-Qatar",
        f"elasticidad {fmt(e1.coef, 2)} [IC95 {fmt(e1.ic95_inf, 2)}; {fmt(e1.ic95_sup, 2)}]; post-Qatar {pct(q1.efecto_pct)} (p={q1.p:.2f}); "
        f"con control de demanda NTTO: {pct(q3.efecto_pct)} (p={q3.p:.2f})",
        "Regresión propia (DNM, BCRA, NTTO)", "P", URL_DNM, "data/processed/E_turismo_modelo.csv",
        "OLS log(llegadas) ~ log(ITCRB_EEUU t−1) + tendencia + post_qatar(2023-01) + post_milei(2023-12) + post_cepo(2025-04) + mundial26 + mes; "
        "2014-01..2026-08 sin 2020-03..2022-03; HAC 12; insumos E13, E22")
    loc19, loc24 = acs.loc[2019, "argentina_loc"], acs.loc[2024, "argentina_loc"]
    add("E24", "DATO", "Población nacida en Argentina residente en EE.UU. (ACS 1 año, B05006), estimación ± MOE 90%",
        f"2010 {fmt(acs.loc[2010, 'argentina_est'])} ± {fmt(acs.loc[2010, 'argentina_moe'])}; 2019 {fmt(acs.loc[2019, 'argentina_est'])} ± "
        f"{fmt(acs.loc[2019, 'argentina_moe'])}; 2024 {fmt(acs.loc[2024, 'argentina_est'])} ± {fmt(acs.loc[2024, 'argentina_moe'])}",
        "U.S. Census Bureau, ACS 1-year Summary File, tabla B05006", "P", acs.loc[2024, "url"], loc24.split(" ::")[0],
        f"{loc24}; valor={int(acs.loc[2024, 'argentina_est'])}; 2019: {loc19}; valor={int(acs.loc[2019, 'argentina_est'])}")
    se = lambda y: acs.loc[y, "argentina_moe"] / 1.645  # noqa: E731
    z = (acs.loc[2024, "argentina_est"] - acs.loc[2022, "argentina_est"]) / np.sqrt(se(2024) ** 2 + se(2022) ** 2)
    add("E25", "ESTIMACIÓN", "Cambio de la población nacida en Argentina 2022→2024 (ACS) y su significancia",
        f"{pct(100 * (acs.loc[2024, 'argentina_est'] / acs.loc[2022, 'argentina_est'] - 1))} (z = {z:.2f}; |z|<1,96: no significativo)",
        "Cálculo propio sobre ACS B05006", "P", acs.loc[2024, "url"], "data/processed/E_diaspora_acs_b05006.csv",
        "z = (est2024 − est2022) / sqrt(SE2024² + SE2022²), SE = MOE/1,645; insumo E24")
    if ohss is not None:
        pl, pn = ohss.attrs["paths"]
        add("E26", "DATO", "Residencias permanentes (LPR) otorgadas a nacidos en Argentina, por año fiscal (DHS, Tabla 3)",
            f"FY2019 {fmt(ohss.loc[2019, 'lpr_nacidos_argentina'])}; FY2022 {fmt(ohss.loc[2022, 'lpr_nacidos_argentina'])}; "
            f"FY2023 {fmt(ohss.loc[2023, 'lpr_nacidos_argentina'])}; FY2024 {fmt(ohss.loc[2024, 'lpr_nacidos_argentina'])}",
            "DHS OHSS, Yearbook of Immigration Statistics FY2024, LPR Tabla 3", "P", URL_OHSS_LPR, pl,
            "hoja 'Table 3'; fila 'Argentina'; columnas 2019/2022/2023/2024 -> "
            + "/".join(str(int(ohss.loc[y, 'lpr_nacidos_argentina'])) for y in (2019, 2022, 2023, 2024))
            + f"; valor={int(ohss.loc[2024, 'lpr_nacidos_argentina'])}")
        add("E27", "DATO", "Naturalizaciones de nacidos en Argentina, por año fiscal (DHS, Tabla 22)",
            f"FY2019 {fmt(ohss.loc[2019, 'naturalizaciones_nacidos_argentina'])}; FY2024 {fmt(ohss.loc[2024, 'naturalizaciones_nacidos_argentina'])}",
            "DHS OHSS, Yearbook FY2024, Naturalizations Tabla 22", "P", URL_OHSS_NATZ, pn,
            "hoja 'Table 22'; fila 'Argentina'; columnas 2019/2024 -> "
            + "/".join(str(int(ohss.loc[y, 'naturalizaciones_nacidos_argentina'])) for y in (2019, 2024))
            + f"; valor={int(ohss.loc[2024, 'naturalizaciones_nacidos_argentina'])}")
    ta = pdf_to_text(p_a8226)
    add("E28", "DATO", "Salida (parcial) del cepo: la Com. BCRA \"A\" 8226 del 11/04/2025 rige desde el 14/04/2025 y habilita a personas humanas "
        "a comprar moneda extranjera sin conformidad previa", "14/04/2025", "BCRA, Comunicación \"A\" 8226", "P", URL_A8226, p_a8226,
        quote(ta, "COMUNICACIÓN “A” 8226 11/04/2025") + " | " + quote(ta, "con vigencia a partir del 14/04/25") + " | "
        + quote(ta, "las entidades podrán dar acceso al mercado de cambios a las personas humanas residentes, sin conformidad previa"))
    ti = local_text(t["i92_path"])
    add("E29", "DATO", "NTTO: el detalle I-92/APIS por país de destino es de pago (no hay serie pública EE.UU.→Argentina)",
        "USD 150 a USD 5.795", "NTTO / trade.gov, página del programa I-92", "P", URL_NTTO_I92, t["i92_path"],
        quote(ti, "The prices range from $150, for a single monthly print-file issue to $5,795 for an annual subscription"))
    pe = rel(t["eti_path"])
    est = tm.loc["2019-01-01":"2019-12-01", "eti_eze_aep_eeuu_can_estadia"].mean(), tm.loc["2025-01-01":"2025-12-01", "eti_eze_aep_eeuu_can_estadia"].mean()
    add("E30", "ESTIMACIÓN", "Estadía media de residentes de EE.UU. y Canadá en Ezeiza+Aeroparque (promedio simple de los 12 meses)",
        f"2019 {fmt(est[0], 1)} noches; 2025 {fmt(est[1], 1)} noches", "datos.yvera.gob.ar — INDEC ETI mensual", "P", URL_ETI_M, pe,
        "promedio de estadia_media_no_residentes, pais_de_residencia='EE.UU y Canadá', ene–dic de cada año")

    sh = 100 * anual["dnm_eeuu_can_total"] / anual["dnm_total_no_residentes"]
    add("E33", "ESTIMACIÓN", "Participación de EE.UU.+Canadá en el total de turistas no residentes (DNM, total país) — el mercado norteamericano "
        "resistió mejor que el total, que cayó por Brasil/Chile/limítrofes",
        f"2019 {fmt(sh[2019], 1)}%; 2023 {fmt(sh[2023], 1)}%; 2025 {fmt(sh[2025], 1)}% (total no residentes 2025 "
        f"{pct(anual.loc[2025, 'dnm_total_no_residentes_vs2019_pct'])} vs 2019)",
        "datos.yvera.gob.ar — DNM", "P", URL_DNM, pdnm, "suma anual EE.UU. y Canadá / suma anual de todos los orígenes; insumo E13")
    li = np.log(itcrm["itcrb_eeuu"]).shift(1)
    dlog = li.loc["2025-01-01":"2025-12-01"].mean() - li.loc["2024-01-01":"2024-12-01"].mean()
    obs = np.log(anual.loc[2025, "dnm_eeuu_can_total"] / anual.loc[2024, "dnm_eeuu_can_total"])
    add("E31", "ESTIMACIÓN", "Parte de la caída 2025 de llegadas EE.UU.+Canadá atribuible a la apreciación real del peso (elasticidad del modelo T1)",
        f"Δlog ITCRB EE.UU. (t−1) 2025 vs 2024 = {fmt(dlog, 3)} → efecto {pct(100 * (np.exp(e1.coef * dlog) - 1))} vs caída observada "
        f"{pct(100 * (np.exp(obs) - 1))}", "Cálculo propio (BCRA, DNM)", "P", URL_ITCRM, "data/processed/E_turismo_modelo.csv",
        "exp(elasticidad_T1 × (media 2025 − media 2024 de log ITCRB_EEUU t−1)) − 1; insumos E22, E23, E13")
    # --- Mundial 2026: resultado de Argentina (notas oficiales, capturas Wayback) ---
    if "conmebol" in m26:
        pm, um = m26["conmebol"]
        tm_ = local_text(pm)
        add("E34", "DATO", "Mundial 2026: resultado de Argentina (CONMEBOL, nota oficial del 19/07/2026)",
            "Subcampeón: perdió la final 1-0 ante España, en la prórroga (19/07/2026)",
            "CONMEBOL, nota '¡Gracias, Argentina!' (captura Wayback del 23/07/2026)", "P", um, pm,
            quote(tm_, "julio 19, 2026") + " | "
            + quote(tm_, "Argentina cerró su participación en la Copa Mundial de la FIFA 2026™ con el subcampeonato tras ceder 1-0 "
                         "frente a España en la Gran Final") + " | "
            + quote(tm_, "Luego de igualar sin goles durante el tiempo reglamentario, la definición llegó en la prórroga"))
    if "afa" in m26:
        pa, ua = m26["afa"]
        ta_ = local_text(pa)
        add("E35", "DATO", "Mundial 2026: resultado de la final según la AFA (federación argentina)",
            "Argentina 0-1 España en la final, con un jugador menos en el alargue",
            "AFA, sitio oficial (captura Wayback del 20/07/2026)", "P", ua, pa,
            quote(ta_, "Hasta el último aliento: Argentina cayó de pie en la final del Mundial") + " | "
            + quote(ta_, "con un hombre menos durante el alargue") + " | "
            + quote(ta_, "Argentina cayó 1-0 frente a España en la final de la Copa del Mundo"))
    if "rfef" in m26:
        pr, ur = m26["rfef"]
        tr_ = local_text(pr)
        add("E36", "DATO", "Mundial 2026: resultado de la final según la RFEF (federación del campeón)",
            "España campeón (1-0 a Argentina en la final, en Nueva Jersey)",
            "RFEF, sitio oficial (captura Wayback del 20/07/2026)", "P", ur, pr,
            quote(tr_, "España, bicampeona del mundo") + " | "
            + quote(tr_, "esta vez ha sido Nueva Jersey el lugar en el que se han hecho realidad los sueños de la Selección") + " | "
            + quote(tr_, "tras vencer a Argentina en la gran final (1-0)"))

    rel26 = vt.loc["2026 ago–sep (post-Mundial)", "relativo_en_vs_base_pct"]
    gt25 = gtw.loc["2025", "ratio_vs_base_pct"] if gtw is not None else float("nan")
    add("E32", "HIPÓTESIS", "Veredicto sobre la tesis 'Argentina es más popular desde Qatar 2022'",
        f"SE SOSTIENE PARCIALMENTE. A favor: escalón post-Qatar en la atención relativa (E07–E09) e interés relativo en Google EE.UU. "
        f"todavía {pct(gt25, 0)} sobre la base en 2025 (E12). En contra: en Wikipedia (en) la atención relativa volvió a la base "
        f"({pct(rel26)} en ago–sep 2026, E05) y en valores absolutos está por debajo de 2022 (E03), aun después de que Argentina "
        f"llegara a la final del Mundial 2026 en EE.UU. (E34); el turismo EE.UU.+Canadá creció "
        f"{pct(anual.loc[2025, 'dnm_eeuu_can_total_vs2019_pct'], 0)} vs 2019 contra {pct(anual.loc[2025, 'ntto_us_a_sudamerica_vs2019_pct'], 0)} "
        f"del viaje de EE.UU. a Sudamérica (E15) y cayó en 2025 (E13, E21)",
        "Síntesis de E03–E34", "—", "", "", "Síntesis de E03, E05, E07, E08, E09, E10, E12, E13, E15, E21, E23, E31, E33, E34; "
        "ver docs/modulos/E_popularidad.md, sección Veredicto")
    write_ledger(MODULO, claims)

    # --- Estado de fuentes ---
    pd.DataFrame(ESTADO).to_csv(PROCESSED / "E_fuentes_estado.csv", index=False)
    pd.DataFrame(FALLAS, columns=["fecha", "fuente", "url", "error", "causa", "accion"]).to_csv(PROCESSED / "E_fuentes_fallidas.csv", index=False)

    # --- Resumen en consola ---
    print(f"{len(claims)} afirmaciones -> docs/claims/claims_{MODULO}.csv")
    for c in claims:
        print(f"{c['claim_id']} [{c['etiqueta']}] {c['afirmacion'][:90]} => {c['valor']}")
    print("Fallas:", len(FALLAS))
    for f in FALLAS:
        print("  -", f["fuente"], "|", f["error"][:80])


if __name__ == "__main__":
    main()
