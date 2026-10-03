"""Módulo D — Pasaporte argentino y Visa Waiver Program (VWP) de EE.UU.

Corre de punta a punta desde las copias de data/raw (descarga solo lo que falta):
  1. Henley Passport Index: revisa los términos de uso de henleyglobal.com ANTES de tocar la API. Si prohíben el
     acceso automatizado o el uso comercial, NO se usa la API y se registra la falla.
  2. 8 U.S.C. §1187 (Cornell LII; uscode.house.gov estaba "Under Maintenance" el 2026-10-03): citas literales de los
     requisitos de designación (umbral de rechazo, pasaporte electrónico, intercambio de información, overstay).
  3. Serie de tasa ajustada de rechazo de visas B (DoS, RefusalRates/FY{yy}.pdf) FY2006–FY2025 vía Wayback Machine
     (travel.state.gov devuelve 403 a clientes automatizados). Se registra la URL y fecha de cada captura.
  4. Precedentes: designación de Chile (Federal Register 2014), baja de Argentina (Federal Register 2002), lista DHS
     de países VWP (incluye Romania 2025), declaración de intención AR–EE.UU. (DHS y Presidencia, 28/07/2025).
  5. Overstay: DHS/CBP Entry/Exit Overstay Reports FY2022–FY2024 (AR, CL, UY, BR).
  6. NIV emitidas (B1/B2) a argentinos: NIV Detail Tables (DoS) vía Wayback.
  7. Canadá (IRCC): acceso sin visa / eTA para AR, CL, UY, BR, MX (sustituto parcial y primario del Henley).

Salidas: data/processed/D_*.csv, outputs/charts/D_*.{png,svg}, docs/claims/claims_D.csv.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from common import (CHARTS, PROCESSED, RAW, TODAY, download, get, local_text, norm_ws, quote, raw_path, sha256,
                    write_ledger)

MODULO = "D"
ROOT = RAW.parents[1]
FAILS: list[dict] = []  # fuentes fallidas de esta corrida (se vuelcan a data/processed/D_fuentes_fallidas.csv)


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def fail(fuente: str, url: str, error: str, causa: str, accion: str) -> None:
    FAILS.append(dict(fecha=TODAY, fuente=fuente, url=url, error=error, causa=causa, accion=accion))
    print(f"  [FALLA] {fuente}: {error}")


# ---------------------------------------------------------------------------------------------------------------
# Fuentes directas (P = primaria)
# ---------------------------------------------------------------------------------------------------------------
SOURCES = {
    # id: (url, nombre local, ext, descripción, tipo)
    # Copia ya descargada por el Módulo B (se reutiliza; no se vuelve a pedir a henleyglobal.com)
    "henley_terms": ("https://www.henleyglobal.com/terms-of-use", "B_henley_terms_of_use", "html",
                     "Henley & Partners, Website Terms of Use (henleyglobal.com; copia del Módulo B)", "R"),
    "pi_tidy": ("https://raw.githubusercontent.com/imorte/passport-index-data/main/passport-index-tidy-iso3.csv",
                "B_passportindex_tidy_iso3", "csv",
                "Passport Index Data (imorte/passport-index-data, MIT, actualizado 17/02/2026; compilado a partir de "
                "passportindex.org; copia del Módulo B)", "R"),
    "usc1187": ("https://www.law.cornell.edu/uscode/text/8/1187", "D_usc_8_1187_cornell", "html",
                "8 U.S.C. §1187 (INA §217), Visa Waiver Program — texto vía Cornell LII", "P"),
    "dhs_vwp": ("https://www.dhs.gov/visa-waiver-program", "D_dhs_vwp", "html",
                "DHS, U.S. Visa Waiver Program (lista de países y requisitos)", "P"),
    "fr_chile": ("https://www.govinfo.gov/content/pkg/FR-2014-03-31/html/2014-07254.htm", "D_fr_2014-07254_chile", "html",
                 "Federal Register 79 FR 17852 (31/03/2014), 'Designation of Chile for the Visa Waiver Program' (GPO/govinfo)", "P"),
    "fr_arg2002": ("https://www.govinfo.gov/content/pkg/FR-2002-02-21/html/02-4260.htm", "D_fr_02-4260_argentina", "html",
                   "Federal Register 67 FR 7943 (21/02/2002), 'Termination of the Designation of Argentina' (GPO/govinfo)", "P"),
    "dhs_ar2025": ("https://www.dhs.gov/news/2025/07/28/secretary-noem-kickstarts-process-argentina-rejoin-visa-waiver-program",
                   "D_dhs_argentina_vwp_2025-07-28", "html",
                   "DHS, comunicado 28/07/2025 'Secretary Noem Kickstarts Process for Argentina to Rejoin Visa Waiver Program'", "P"),
    "arg_decl": ("https://www.argentina.gob.ar/noticias/argentina-y-estados-unidos-firmaron-una-declaracion-de-intencion-para-el-ingreso-al",
                 "D_presidencia_declaracion_vwp_2025-07-28", "html",
                 "Presidencia de la Nación, noticia 28/07/2025 (declaración de intención VWP)", "P"),
    "dhs_ro2025": ("https://www.dhs.gov/news/2025/05/02/dhs-announces-rescission-romanias-designation-visa-waiver-program",
                   "D_dhs_romania_rescission_2025-05-02", "html",
                   "DHS, comunicado 02/05/2025, rescisión de la designación de Rumania en el VWP", "P"),
    "ov_fy24": ("https://www.dhs.gov/sites/default/files/2025-08/25_0826_cbp_entry-exit-overstay-report-fiscal-year-2024.pdf",
                "D_dhs_overstay_report_FY2024", "pdf", "DHS/CBP, Entry/Exit Overstay Report FY2024 (16/07/2025)", "P"),
    "ov_fy23": ("https://www.dhs.gov/sites/default/files/2024-10/24_1011_CBP-Entry-Exit-Overstay-Report-FY23-Data.pdf",
                "D_dhs_overstay_report_FY2023", "pdf", "DHS/CBP, Entry/Exit Overstay Report FY2023 (incluye FY2022 en anexo)", "P"),
    "ircc": ("https://www.canada.ca/en/immigration-refugees-citizenship/services/visit-canada/entry-requirements-country.html",
             "D_ircc_entry_requirements", "html", "IRCC (Gobierno de Canadá), Entry requirements by country/territory", "P"),
}

WB_AVAIL = "https://archive.org/wayback/available?url={url}&timestamp={ts}"
WB_RAW = "https://web.archive.org/web/{ts}id_/{url}"
REFUSAL_URL = "https://travel.state.gov/content/dam/visas/Statistics/Non-Immigrant-Statistics/RefusalRates/FY{yy:02d}.pdf"
NIV_URL = "https://travel.state.gov/content/dam/visas/Statistics/Non-Immigrant-Statistics/NIVDetailTables/FY{yy:02d}NIVDetailTable.{ext}"
FY_RANGE = range(2006, 2026)
COUNTRIES = {"Argentina": "AR", "Chile": "CL", "Uruguay": "UY", "Brazil": "BR"}


# ---------------------------------------------------------------------------------------------------------------
# Wayback
# ---------------------------------------------------------------------------------------------------------------
def wayback_lookup(url: str, name: str, ts_hints: list[str]) -> dict | None:
    """Busca la captura más cercana con la API de disponibilidad (archive.org). Guarda la respuesta JSON en data/raw."""
    cached = sorted(RAW.glob(f"{name}_wbavail_*.json"))
    if cached:
        snap = json.loads(cached[-1].read_text()).get("archived_snapshots", {}).get("closest")
        if snap and snap.get("status") == "200":
            return snap
    for ts in ts_hints:
        try:
            r = get(WB_AVAIL.format(url=url.replace("https://", ""), ts=ts), timeout=40)
            j = r.json()
        except Exception:  # noqa: BLE001
            continue
        snap = j.get("archived_snapshots", {}).get("closest")
        if snap and snap.get("status") == "200":
            raw_path(f"{name}_wbavail", "json").write_text(json.dumps(j, indent=1))
            return snap
    return None


def wayback_download(url: str, name: str, ext: str, ts_hints: list[str]) -> tuple[Path | None, str, str]:
    """Devuelve (archivo local, url de captura, timestamp). Reutiliza copias locales."""
    snap = wayback_lookup(url, name, ts_hints)
    if not snap:
        fail(f"Wayback: {name}", url, "sin captura 200 en la API de disponibilidad", "No archivado o API intermitente",
             "Se omite ese año de la serie (no se rellena)")
        return None, "", ""
    ts = snap["timestamp"]
    orig = snap["url"].split(f"/web/{ts}/", 1)[1]
    cap = WB_RAW.format(ts=ts, url=orig)
    existing = sorted(RAW.glob(f"{name}_*.{ext}"))
    if existing:
        return existing[-1], cap, ts
    try:
        p = download(cap, name, ext, timeout=90)
    except Exception as e:  # noqa: BLE001
        fail(f"Wayback: {name}", cap, f"{type(e).__name__}: {str(e)[:90]}",
             "web.archive.org resetea la conexión (TCP reset) desde este entorno", "Reintentar más tarde; el año queda vacío")
        return None, cap, ts
    head = p.read_bytes()[:5]
    if ext == "pdf" and head != b"%PDF-":
        p.unlink()
        fail(f"Wayback: {name}", cap, "la respuesta no es un PDF", "Captura inválida", "Se omite")
        return None, cap, ts
    return p, cap, ts


# ---------------------------------------------------------------------------------------------------------------
# Tasa ajustada de rechazo de visas B
# ---------------------------------------------------------------------------------------------------------------
RATE_RE = re.compile(r"^(?P<name>[A-Za-z][A-Za-z ,.'()\-&]+?)\s+(?P<rate>\d{1,3}\.\d{1,2})\s?%?$")


def parse_refusal_pdf(p: Path) -> dict[str, tuple[float, str]]:
    """Devuelve {país: (tasa %, línea literal)} para los países de interés."""
    import pdfplumber
    out: dict[str, tuple[float, str]] = {}
    with pdfplumber.open(p) as pdf:
        for page in pdf.pages:
            for line in (page.extract_text() or "").split("\n"):
                line = norm_ws(line)
                for c in COUNTRIES:
                    # Formato habitual "Argentina 2.53%"; a veces varias columnas por línea.
                    for m in re.finditer(rf"(?<![A-Za-z]){c}\s+(\d{{1,3}}\.\d{{1,2}})\s?%?", line):
                        if c not in out:
                            out[c] = (float(m.group(1)), norm_ws(m.group(0)))
    return out


def refusal_series() -> tuple[list[dict], dict]:
    rows, meta = [], {}
    for fy in FY_RANGE:
        yy = fy % 100
        url = REFUSAL_URL.format(yy=yy)
        name = f"D_dos_refusal_rates_FY{yy:02d}"
        hints = [f"{fy + 1}1231", f"{fy + 2}0630", f"{fy + 4}0101", "2026"]
        p, cap, ts = wayback_download(url, name, "pdf", hints)
        meta[fy] = dict(url=url, captura=cap, ts=ts, archivo=rel(p) if p else "")
        if not p:
            continue
        vals = parse_refusal_pdf(p)
        txt = local_text(p)
        title = re.search(r"Fiscal Year (\d{4})", txt)
        if title and int(title.group(1)) != fy:
            fail(f"DoS refusal FY{yy:02d}", cap, f"el PDF dice 'Fiscal Year {title.group(1)}'", "Archivo inesperado",
                 "Se omite")
            continue
        for c, (rate, lit) in vals.items():
            rows.append(dict(fy=fy, pais=c, iso2=COUNTRIES[c], tasa_rechazo_ajustada_B=rate, cita=lit,
                             fuente_url=url, captura_wayback=cap, timestamp_captura=ts, archivo_local=rel(p),
                             sha256=sha256(p)))
        missing = set(COUNTRIES) - set(vals)
        if missing:
            print(f"  FY{fy}: sin fila para {sorted(missing)}")
    return rows, meta


# ---------------------------------------------------------------------------------------------------------------
# NIV emitidas (B1/B2) a argentinos
# ---------------------------------------------------------------------------------------------------------------
def niv_series() -> list[dict]:
    import pandas as pd
    rows = []
    for fy in FY_RANGE:
        yy = fy % 100
        got = None
        for ext in ("xlsx", "xls"):
            url = NIV_URL.format(yy=yy, ext=ext)
            name = f"D_dos_niv_detail_FY{yy:02d}"
            if not sorted(RAW.glob(f"{name}_*.{ext}")):
                snap = wayback_lookup(url, name, [f"{fy + 1}1231", "2026"])
                if not snap:
                    continue
            p, cap, ts = wayback_download(url, name, ext, [f"{fy + 1}1231", "2026"])
            if p:
                got = (p, cap, ts, url)
                break
        if not got:
            continue
        p, cap, ts, url = got
        try:
            xl = pd.read_excel(p, sheet_name=None, header=None)
        except Exception as e:  # noqa: BLE001
            fail(f"NIV detail FY{yy:02d}", cap, f"{type(e).__name__}: {str(e)[:80]}", "Formato no legible", "Se omite")
            continue
        for sheet, df in xl.items():
            df = df.astype(str)
            hdr_idx = None
            for i in range(min(15, len(df))):
                vals = [v.strip() for v in df.iloc[i].tolist()]
                if any(v in ("B-1,2", "B1/B2", "B-1/B-2", "B1/B2/BCC") or v.replace("-", "").replace(" ", "") in ("B12", "B1B2")
                       for v in vals):
                    hdr_idx = i
                    break
            if hdr_idx is None:
                continue
            hdr = [v.strip() for v in df.iloc[hdr_idx].tolist()]
            for i in range(hdr_idx + 1, len(df)):
                first = df.iloc[i, 0].strip()
                if first.lower() == "argentina":
                    rec = dict(zip(hdr, [v.strip() for v in df.iloc[i].tolist()]))
                    for col in hdr:
                        key = col.replace("-", "").replace(" ", "").replace("/", "")
                        if key in ("B12", "B1B2", "B1,2"):
                            rows.append(dict(fy=fy, pais="Argentina", clase=col, emitidas=rec[col].replace(",", ""),
                                             hoja=sheet, fila=i, fuente_url=url, captura_wayback=cap,
                                             timestamp_captura=ts, archivo_local=rel(p), sha256=sha256(p)))
                    break
            break
    return rows


# ---------------------------------------------------------------------------------------------------------------
# Destinos sin visa (Passport Index Data; misma definición que el Módulo B, claim B36)
# ---------------------------------------------------------------------------------------------------------------
SIN_VISA = {"visa free", "visa on arrival", "eta"}  # + cualquier número de días
PASS = {"ARG": "Argentina", "CHL": "Chile", "URY": "Uruguay", "BRA": "Brasil", "MEX": "México"}
KEY_DEST = {"USA": "EE.UU.", "CAN": "Canadá", "GBR": "Reino Unido", "DEU": "Alemania (Schengen)", "JPN": "Japón",
            "AUS": "Australia", "CHN": "China", "IND": "India", "RUS": "Rusia", "ZAF": "Sudáfrica"}


def passport_counts(path: Path) -> tuple[list[dict], list[dict]]:
    import pandas as pd
    d = pd.read_csv(path, dtype=str)
    d = d[d["Requirement"] != "-1"]
    d["sin_visa"] = d["Requirement"].str.isdigit() | d["Requirement"].isin(SIN_VISA)
    cnt = d.groupby("Passport")["sin_visa"].sum().astype(int)
    rank = cnt.rank(method="min", ascending=False).astype(int)  # puesto: 1 + cantidad de pasaportes con más destinos
    out = [dict(pasaporte=iso, nombre=PASS[iso], destinos_sin_visa=int(cnt[iso]), puesto=int(rank[iso]),
                pasaportes_totales=int(len(cnt)),
                localizador=f"Passport={iso}; Requirement ∈ {{número de días, 'visa free', 'visa on arrival', 'eta'}}; "
                            f"count={int(cnt[iso])}; puesto=1+#(pasaportes con count mayor)")
           for iso in PASS]
    req = {(a, b): r for a, b, r in d[["Passport", "Destination", "Requirement"]].itertuples(index=False)}
    mat = [dict(pasaporte=iso, nombre=PASS[iso], destino=dest, destino_nombre=nm, requisito=req.get((iso, dest), ""))
           for iso in PASS for dest, nm in KEY_DEST.items() if dest != iso]
    return out, mat


def chart_passports(counts: list[dict]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    c = sorted(counts, key=lambda r: r["destinos_sin_visa"])
    fig, ax = plt.subplots(figsize=(8, 4.2))
    fig.subplots_adjust(left=0.14, right=0.95, top=0.78, bottom=0.17)
    _style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ys = range(len(c))
    cols = [SERIES["Argentina"] if r["pasaporte"] == "ARG" else "#b9b8b2" for r in c]
    ax.barh(list(ys), [r["destinos_sin_visa"] for r in c], color=cols, height=0.6)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([r["nombre"] for r in c], fontsize=9.5, color=INK)
    for y, r in zip(ys, c):
        ax.text(r["destinos_sin_visa"] + 1.5, y, f"{r['destinos_sin_visa']} (puesto {r['puesto']})", va="center",
                fontsize=8.5, color=INK)
    ax.set_xlim(0, max(r["destinos_sin_visa"] for r in c) * 1.18)
    ax.set_xlabel("Destinos sin visa previa (sin visa, visa a la llegada o ETA), de 198", fontsize=9, color=INK2)
    by = {r["pasaporte"]: r["destinos_sin_visa"] for r in counts}
    title = ("Argentina y Chile empatan en destinos sin visa: la diferencia está en EE.UU. y Canadá"
             if by["ARG"] == by["CHL"] else "Destinos sin visa: Argentina frente a sus comparables")
    fig.suptitle(title,
                 x=0.01, ha="left", fontsize=12.5, color=INK, fontweight="bold")
    fig.text(0.01, 0.86, "Destinos sin visa previa por pasaporte, febrero de 2026 (puesto entre 199 pasaportes)",
             fontsize=9, color=INK2)
    _save(fig, "destinos_sin_visa_AR_comparables",
          "Passport Index Data (MIT, 17/02/2026), compilado a partir de passportindex.org; no es el Henley Passport Index")
    plt.close(fig)


# ---------------------------------------------------------------------------------------------------------------
# Claims
# ---------------------------------------------------------------------------------------------------------------
CLAIMS = [
    # (claim_id, etiqueta, afirmación, valor, fuente, cita literal)
    ("D01", "DATO", "Los términos de uso de henleyglobal.com prohíben el acceso automatizado al sitio (robots, scrapers)",
     "Prohibido", "henley_terms",
     "Use any robot, spider, scraper, or other automated means to access the website for any purpose"),
    ("D02", "DATO", "Los términos de uso de Henley exigen licencia para uso comercial del contenido", "Requiere licencia",
     "henley_terms",
     "You must not use any part of the content on our website for commercial purposes without obtaining a license to do so from us or our licensors"),
    ("D03", "DATO", "INA §217(c)(1): la designación es facultativa ('may') del Secretario de DHS, en consulta con el Secretario de Estado",
     "Discrecional", "usc1187",
     "The Secretary of Homeland Security , in consultation with the Secretary of State, may designate any country as a program country if it meets the requirements of paragraph (2)"),
    ("D04", "DATO", "Umbral de rechazo (vía ii): tasa de rechazo de visas de visitante del año fiscal completo anterior < 3,0%",
     "< 3,0%", "usc1187",
     "such refusal rate for nationals of that country during the previous full fiscal year was less than 3.0 percent"),
    ("D05", "DATO", "Umbral de rechazo (vía i): promedio de los dos años fiscales previos < 2,0% Y cada uno de esos años < 2,5%",
     "< 2,0% promedio y < 2,5% cada año", "usc1187",
     "the two previous full fiscal years was less than 2.0 percent of the total number of nonimmigrant visitor visas for nationals of that country which were granted or refused during those years; and (II) either of such two previous full fiscal years was less than 2.5 percent"),
    ("D06", "DATO", "Pasaporte electrónico obligatorio (desde 01/04/2016) con datos biográficos y biométricos",
     "ePassport", "usc1187",
     "the passport is an electronic passport that is fraud-resistant, contains relevant biographic and biometric information"),
    ("D07", "DATO", "Requisito de seguridad: DHS debe determinar que la designación no compromete la seguridad y el cumplimiento de la ley de EE.UU.",
     "Evaluación DHS", "usc1187",
     "determines that such interests would not be compromised by the designation of the country"),
    ("D08", "DATO", "Requisito de intercambio de información sobre viajeros que representen amenaza",
     "Acuerdo de intercambio", "usc1187",
     "The government of the country enters into an agreement with the United States to share information regarding whether citizens and nationals of that country traveling to the United States represent a threat to the security or welfare of the United States or its citizens, and fully implements such agreement"),
    ("D09", "DATO", "Requisito de reporte de pasaportes perdidos o robados dentro de las 24 horas",
     "24 horas", "usc1187",
     "information about the theft or loss of passports not later than 24 hours after becoming aware of the theft or loss"),
    ("D10", "DATO", "Requisito de repatriación de nacionales con orden de remoción en no más de tres semanas",
     "3 semanas", "usc1187",
     "accepts for repatriation any citizen, former citizen, or national of the country against whom a final executable order of removal is issued not later than three weeks after the issuance of the final order of removal"),
    ("D11", "DATO", "Excepción hasta 10% de rechazo o tope de overstay: solo tras certificar un sistema de salida aérea (97%); la facultad quedó suspendida desde el 01/07/2009 hasta esa notificación",
     "≤10% / overstay máx.", "usc1187",
     "the rate of refusals for nonimmigrant visitor visas for nationals of the country during the previous full fiscal year was not more than ten percent; or (II) the visa overstay rate for the country for the previous full fiscal year does not exceed the maximum visa overstay rate"),
    ("D12", "DATO", "Suspensión de la facultad de dispensa del umbral de rechazo desde el 01/07/2009 (sin notificación biométrica de salida)",
     "Suspendida desde 01/07/2009", "usc1187",
     "the Secretary’s waiver authority under subparagraph (B) shall be suspended beginning on July 1, 2009 , until such time as the Secretary makes such notification"),
    ("D13", "DATO", "Definición legal de 'visa overstay rate'", "Definición", "usc1187",
     "the term “ visa overstay rate ” means, with respect to a country, the ratio of"),
    ("D14", "DATO", "DHS: requisito de tasa anual de rechazo de visas B menor al 3%", "< 3%", "dhs_vwp",
     "Has an annual temporary visitor visa (i.e., B visa) refusal rate of less than three percent"),
    ("D15", "DATO", "DHS: la designación inicial exige además una evaluación de inteligencia independiente (DHS I&A, por el DNI)",
     "Evaluación de inteligencia", "dhs_vwp",
     "an independent intelligence assessment produced by the DHS Office of Intelligence and Analysis (on behalf of the Director of National Intelligence)"),
    ("D16", "DATO", "DHS (2022): requisito de intercambio de información (EBSP) para países VWP actuales y aspirantes, con cotejo biométrico",
     "EBSP", "dhs_vwp",
     "In 2022, the Secretary of Homeland Security announced an information sharing requirement for all current and aspiring VWP countries"),
    ("D17", "DATO", "DHS (2017): países VWP con overstay ≥2% deben lanzar campaña pública de información",
     "2%", "dhs_vwp",
     "VWP countries having a 2% or greater rate of business or tourism nonimmigrant visitors overstaying the terms of their admission into the United States must initiate a public information campaign"),
    ("D18", "DATO", "Chile: viaje VWP desde el 31/03/2014 (único país latinoamericano en la lista actual de DHS)",
     "31/03/2014", "dhs_vwp", "Chile Mar. 31, 2014"),
    ("D19", "DATO", "Argentina fue país VWP entre el 08/07/1996 y el 21/02/2002", "1996–2002", "dhs_vwp",
     "Argentina July 8, 1996 Feb. 21, 2002"),
    ("D20", "DATO", "Uruguay fue país VWP entre el 09/08/1999 y el 15/04/2003", "1999–2003", "dhs_vwp",
     "Uruguay Aug. 9, 1999 Apr. 15, 2003"),
    ("D21", "DATO", "Rumania fue designada el 09/01/2025 y la designación se rescindió el 02/05/2025 sin implementarse",
     "Rescindida", "dhs_vwp",
     "Romania was designated on January 9, 2025 but that designation was not implemented before rescission on May 2, 2025"),
    ("D22", "DATO", "DHS justificó la rescisión de Rumania por su foco en seguridad fronteriza y migratoria (discrecionalidad)",
     "02/05/2025", "dhs_ro2025",
     "given this Administration’s focus on border and immigration security, DHS decided that Romania’s designation should be rescinded"),
    ("D23", "DATO", "Chile fue designado país VWP el 28/02/2014", "28/02/2014", "fr_chile",
     "On February 28, 2014, the Secretary of Homeland Security, in consultation with the Secretary of State designated Chile as a country that is eligible to participate in the Visa Waiver Program"),
    ("D24", "DATO", "El Departamento de Estado nominó a Chile el 03/06/2013 (≈9 meses antes de la designación)", "03/06/2013",
     "fr_chile", "The Secretary of State nominated Chile for participation in the VWP on June 3, 2013"),
    ("D25", "DATO", "La regla de designación de Chile rige desde el 31/03/2014", "31/03/2014", "fr_chile",
     "This final rule is effective on March 31, 2014."),
    ("D26", "DATO", "Baja de Argentina (2002): crisis económica y aumento de argentinos que usaban el programa para vivir y trabajar ilegalmente",
     "21/02/2002", "fr_arg2002",
     "Due to the current economic crisis in Argentina and the increase in the number of Argentine nationals attempting to use the program to live and work illegally in the United States"),
    ("D27", "DATO", "En 2002 EE.UU. señaló falta de integridad en el proceso para obtener los documentos base del pasaporte argentino",
     "Integridad documental", "fr_arg2002",
     "While the Argentine passport itself is a relatively secure document, the process for obtaining the documents to procure a passport lacks integrity, adding to the risk of successful organized smuggling of aliens into the United States"),
    ("D28", "DATO", "Declaración de intención DHS–Argentina para el reingreso al VWP (28/07/2025)", "28/07/2025", "dhs_ar2025",
     "signed a statement of intent to work toward Argentina’s reentry to the Visa Waiver Program (VWP)"),
    ("D29", "DATO", "DHS (Sec. Noem) afirma que Argentina tiene la menor tasa de overstay de América Latina", "Declaración DHS",
     "dhs_ar2025", "Argentina now has the lowest visa overstay rate in all of Latin America"),
    ("D30", "DATO", "DHS: la designación lleva tiempo; la declaración indica apoyo para que Argentina cumpla los criterios 'en los próximos años'",
     "Sin fecha", "dhs_ar2025",
     "The Visa Waiver Program designation process takes time, as partners must meet strong security requirements, but the statement of intent indicates DHS’s support and commitment to working with Argentina as it works diligently to meet eligibility criteria in the coming years"),
    ("D31", "DATO", "Presidencia argentina: firma de la declaración de intención para el ingreso al Programa de Exención de Visas",
     "28/07/2025", "arg_decl",
     "La República Argentina y los Estados Unidos de América firmaron una declaración de intención para el ingreso al Programa de Exención de Visas"),
    ("D32", "DATO", "Overstay total FY2024, visitantes B1/B2, Argentina (países no VWP)", "0,81%", "ov_fy24",
     "ARGENTINA 594,000 221 4,580 4,801 0.81% 0.77%"),
    ("D33", "DATO", "Overstay total FY2024, visitantes de negocios/turismo (VWP+B1/B2), Chile", "2,32%", "ov_fy24",
     "CHILE 438,861 1,109 9,088 10,197 2.32% 2.07%"),
    ("D34", "DATO", "Overstay total FY2024, visitantes B1/B2, Uruguay", "1,97%", "ov_fy24",
     "URUGUAY 58,355 41 1,109 1,150 1.97% 1.90%"),
    ("D35", "DATO", "Overstay total FY2024, visitantes B1/B2, Brasil", "1,25%", "ov_fy24",
     "BRAZIL 1,708,258 1,172 20,168 21,340 1.25% 1.18%"),
    ("D36", "DATO", "Overstay total FY2023, visitantes B1/B2, Argentina", "0,97%", "ov_fy23",
     "ARGENTINA 561,808 312 5,118 5,430 0.97% 0.91%"),
    ("D37", "DATO", "Overstay total FY2023, visitantes de negocios/turismo, Chile", "2,62%", "ov_fy23",
     "CHILE 466,799 1,347 10,886 12,233 2.62% 2.33%"),
    ("D38", "DATO", "Overstay total FY2022, visitantes B1/B2, Argentina", "1,38%", "ov_fy23",
     "ARGENTINA 354,225 315 4,560 4,875 1.38% 1.29%"),
    ("D39", "DATO", "Overstay total FY2022, visitantes de negocios/turismo, Chile", "2,97%", "ov_fy23",
     "CHILE 390,806 1,280 10,309 11,589 2.97% 2.64%"),
    ("D40", "DATO", "Overstay total de países VWP (visitantes de negocios/turismo) FY2024", "0,49%", "ov_fy24",
     "The Fiscal Year 2024 Visa Waiver Program countries’ total overstay rate is 0.49 percent"),
    ("D41", "DATO", "Canadá: Argentina es país con visa requerida; algunos ciudadanos pueden usar eTA si cumplen requisitos",
     "Visa / eTA condicional", "ircc",
     "Argentina (Some citizens of Argentina may be eligible for an eTA if they meet certain requirements .)"),
    ("D42", "DATO", "Canadá: Chile figura entre los países que solo requieren eTA (sin visa)", "eTA (sin visa)", "ircc",
     "Brunei Darussalam Bulgaria Chile Croatia"),
    ("D43", "DATO", "Canadá: lista de países con visa requerida elegibles para eTA (incluye AR, BR, MX, UY)",
     "eTA condicional", "ircc",
     "Eligible visa-required countries Antigua and Barbuda Argentina Brazil Costa Rica Indonesia Malaysia Mexico Morocco Panama Philippines St. Kitts and Nevis St. Lucia St. Vincent and the Grenadines Seychelles Thailand Trinidad and Tobago Uruguay"),
]

OVERSTAY = [  # (fy, país, claim_id, overstay total %, categoría)
    (2022, "Argentina", "D38", 1.38, "B1/B2 (no VWP)"), (2022, "Chile", "D39", 2.97, "VWP+B1/B2"),
    (2023, "Argentina", "D36", 0.97, "B1/B2 (no VWP)"), (2023, "Chile", "D37", 2.62, "VWP+B1/B2"),
    (2024, "Argentina", "D32", 0.81, "B1/B2 (no VWP)"), (2024, "Chile", "D33", 2.32, "VWP+B1/B2"),
    (2024, "Uruguay", "D34", 1.97, "B1/B2 (no VWP)"), (2024, "Brazil", "D35", 1.25, "B1/B2 (no VWP)"),
]


# ---------------------------------------------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------------------------------------------
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SERIES = {"Argentina": "#2a78d6", "Chile": "#eb6834", "Uruguay": "#1baf7a", "Brazil": "#eda100"}
ES = {"Argentina": "Argentina", "Chile": "Chile", "Uruguay": "Uruguay", "Brazil": "Brasil"}


def _style(ax):
    ax.set_facecolor("white")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(AXIS)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _save(fig, name, fuente):
    fig.text(0.01, 0.01, f"Fuente: {fuente}. Elaboración: Colossus Lab.", fontsize=7, color=INK2, ha="left", va="bottom")
    CHARTS.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(CHARTS / f"D_{name}.{ext}", dpi=150, facecolor="white")


def chart_refusal(rows: list[dict]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 5.2))
    fig.subplots_adjust(left=0.08, right=0.86, top=0.84, bottom=0.16)
    _style(ax)
    ymax = 0
    for c in ["Argentina", "Chile", "Uruguay", "Brazil"]:
        pts = sorted((r["fy"], r["tasa_rechazo_ajustada_B"]) for r in rows if r["pais"] == c)
        if not pts:
            continue
        xs, ys = zip(*pts)
        ymax = max(ymax, max(ys))
        main = c in ("Argentina", "Chile")
        ax.plot(xs, ys, color=SERIES[c], lw=2 if main else 1.3, alpha=1 if main else 0.75, marker="o",
                ms=4 if main else 3, label=ES[c], zorder=3 if main else 2)
        ax.annotate(f"{ES[c]} {ys[-1]:.1f}%".replace(".", ","), (xs[-1], ys[-1]), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=8.5, color=INK)
    ax.axhline(3.0, color=INK2, lw=1, ls=(0, (4, 3)), zorder=1)
    ax.text(FY_RANGE.start - 0.3, 3.0, "Umbral legal VWP: 3%", fontsize=8, color=INK2, va="bottom")
    ax.axvline(2014, color=MUTED, lw=1, zorder=1)
    ax.text(2014.1, ymax * 1.02 if ymax else 10, "Chile designado\n28/02/2014 (FY2014)", fontsize=8, color=INK2, va="top")
    ax.set_xlim(FY_RANGE.start - 0.5, FY_RANGE.stop - 0.5)
    ax.set_ylim(0, max(ymax * 1.1, 4))
    ax.set_xticks(list(range(FY_RANGE.start, FY_RANGE.stop, 2)))
    ax.set_ylabel("Tasa ajustada de rechazo de visas B (%)", fontsize=9, color=INK2)
    ax.set_xlabel("Año fiscal de EE.UU.", fontsize=9, color=INK2)
    ax.legend(frameon=False, fontsize=8.5, loc="upper right", bbox_to_anchor=(1.18, 1.0))
    fig.suptitle("Chile entró al VWP tras bajar del 3%; Argentina sigue por encima del umbral",
                 x=0.01, ha="left", fontsize=12.5, color=INK, fontweight="bold")
    fig.text(0.01, 0.905, "Tasa ajustada de rechazo de visas de turismo/negocios (B) por nacionalidad, FY2006–FY2025",
             fontsize=9, color=INK2)
    _save(fig, "tasa_rechazo_B_AR_CL", "U.S. Department of State, Adjusted Refusal Rate – B Visas Only (copias Wayback Machine)")
    plt.close(fig)


def chart_overstay() -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4.8))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.80, bottom=0.18)
    _style(ax)
    years = [2022, 2023, 2024]
    w = 0.36
    for k, c in enumerate(["Argentina", "Chile"]):
        vals = [next(v for (fy, p, _, v, _) in OVERSTAY if fy == y and p == c) for y in years]
        xs = [y + (k - 0.5) * w for y in years]
        ax.bar(xs, vals, width=w - 0.04, color=SERIES[c], label=f"{c} ({'VWP' if c == 'Chile' else 'con visa B'})")
        for x, v in zip(xs, vals):
            ax.text(x, v + 0.05, f"{v:.2f}%".replace(".", ","), ha="center", fontsize=8.5, color=INK)
    ax.axhline(2.0, color=INK2, lw=1, ls=(0, (4, 3)))
    ax.text(2021.55, 2.03, "2%: umbral DHS de campaña pública (países VWP)", fontsize=8, color=INK2, va="bottom")
    ax.set_xticks(years)
    ax.set_xticklabels([f"FY{y}" for y in years])
    ax.set_ylabel("Overstay total (%)", fontsize=9, color=INK2)
    ax.set_ylim(0, 3.5)
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    fig.suptitle("Los argentinos exceden su estadía en EE.UU. menos que los chilenos",
                 x=0.01, ha="left", fontsize=12.5, color=INK, fontweight="bold")
    fig.text(0.01, 0.875, "Tasa de overstay de visitantes de negocios/turismo llegados por aire o mar", fontsize=9,
             color=INK2)
    _save(fig, "overstay_AR_CL", "DHS/CBP, Entry/Exit Overstay Reports FY2023 y FY2024")
    plt.close(fig)


def chart_niv(rows: list[dict]) -> None:
    if not rows:
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pts = sorted((r["fy"], int(float(r["emitidas"]))) for r in rows)
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    fig.subplots_adjust(left=0.1, right=0.97, top=0.80, bottom=0.17)
    _style(ax)
    xs, ys = zip(*pts)
    ax.bar(xs, [y / 1000 for y in ys], color=SERIES["Argentina"], width=0.7)
    i = ys.index(max(ys))
    ax.text(xs[i], ys[i] / 1000 + 4, f"{ys[i]/1000:,.0f} mil".replace(",", "."), ha="center", fontsize=8.5, color=INK)
    ax.text(xs[-1], ys[-1] / 1000 + 4, f"{ys[-1]/1000:,.0f} mil".replace(",", "."), ha="center", fontsize=8.5, color=INK)
    ax.set_ylabel("Visas B1/B2 emitidas (miles)", fontsize=9, color=INK2)
    ax.set_xticks(list(xs)[::2])
    fig.suptitle("Visas de turismo/negocios (B1/B2) emitidas a argentinos", x=0.01, ha="left", fontsize=12.5,
                 color=INK, fontweight="bold")
    fig.text(0.01, 0.875, "Por año fiscal de EE.UU.; columna B1/B2 de las NIV Detail Tables", fontsize=9, color=INK2)
    _save(fig, "visas_B1B2_argentinos", "U.S. Department of State, Nonimmigrant Visa Detail Tables (copias Wayback Machine)")
    plt.close(fig)


# ---------------------------------------------------------------------------------------------------------------
def main() -> None:
    files, texts = {}, {}
    for sid, (url, name, ext, desc, _t) in SOURCES.items():
        try:
            files[sid] = download(url, name, ext)
            if ext in ("html", "htm", "pdf"):
                texts[sid] = local_text(files[sid])
        except Exception as e:  # noqa: BLE001
            fail(desc, url, f"{type(e).__name__}: {str(e)[:90]}", "Descarga fallida", "Se omiten sus afirmaciones")

    # 1) Henley: decisión según términos
    henley_ok = "henley_terms" in texts and "automated means to access the website" not in texts["henley_terms"]
    if not henley_ok:
        fail("Henley Passport Index (API api.henleypassportindex.com y henleyglobal.com/passport-index)",
             "https://api.henleypassportindex.com/api/v3/countries",
             "No usada", "Términos de uso lo prohíben: 'robot, spider, scraper, or other automated means to access the "
             "website for any purpose' y uso comercial sin licencia (D01, D02); henleypassportindex.com redirige a "
             "henleyglobal.com", "No se usa ningún dato de Henley. Sustituto: Passport Index Data (MIT, tipo R, compilado "
             "de passportindex.org) + fuentes primarias DHS e IRCC")

    rows = []
    for cid, label, claim, value, sid, needle in CLAIMS:
        if sid not in texts:
            continue
        url, _n, _e, desc, tipo = SOURCES[sid]
        rows.append(dict(claim_id=cid, etiqueta=label, afirmacion=claim, valor=value, fuente=desc, tipo_fuente=tipo,
                         url=url, archivo_local=rel(files[sid]), sha256=sha256(files[sid]),
                         cita_textual=quote(texts[sid], needle)))

    # Conteo de países VWP actuales (ESTIMACIÓN a partir de la lista DHS)
    if "dhs_vwp" in texts:
        t = texts["dhs_vwp"]
        seg = t[t.find("Current Program Countries"):t.find("Former Program Countries")]
        n = len(re.findall(r"(?:Jan|Feb|Mar|Apr|May|June|July|Aug|Sept|Oct|Nov|Dec)\.? \d{1,2}, \d{4}", seg))
        rows.append(dict(claim_id="D44", etiqueta="ESTIMACIÓN",
                         afirmacion="Cantidad de países con designación VWP vigente según la lista DHS (Chile es el único de América Latina)",
                         valor=str(n), fuente=SOURCES["dhs_vwp"][3], tipo_fuente="P", url=SOURCES["dhs_vwp"][0],
                         archivo_local=rel(files["dhs_vwp"]), sha256=sha256(files["dhs_vwp"]),
                         cita_textual="Conteo de fechas 'VWP Travel Began' entre 'Current Program Countries' y 'Former Program Countries' (incluye D18)"))

    # 1b) Destinos sin visa (Passport Index Data, tipo R) — sustituto del Henley
    pcounts, pmat = [], []
    if "pi_tidy" in files:
        pcounts, pmat = passport_counts(files["pi_tidy"])
        PROCESSED.mkdir(parents=True, exist_ok=True)
        with (PROCESSED / "D_destinos_sin_visa.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(pcounts[0]))
            w.writeheader()
            w.writerows(pcounts)
        with (PROCESSED / "D_requisitos_destinos_clave.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(pmat[0]))
            w.writeheader()
            w.writerows(pmat)
        url, _n, _e, desc, tipo = SOURCES["pi_tidy"]
        for k, r in enumerate(pcounts):
            rows.append(dict(claim_id=f"D6{k}", etiqueta="ESTIMACIÓN",
                             afirmacion=f"Destinos sin visa previa del pasaporte de {r['nombre']} (definición del Módulo B, B36) y puesto entre {r['pasaportes_totales']} pasaportes",
                             valor=f"{r['destinos_sin_visa']} de 198; puesto {r['puesto']}", fuente=desc, tipo_fuente=tipo,
                             url=url, archivo_local=rel(files["pi_tidy"]), sha256=sha256(files["pi_tidy"]),
                             cita_textual=r["localizador"]))
        for k, (iso, dest) in enumerate([("ARG", "USA"), ("CHL", "USA"), ("ARG", "CAN"), ("CHL", "CAN")]):
            r = next(x for x in pmat if x["pasaporte"] == iso and x["destino"] == dest)
            rows.append(dict(claim_id=f"D6{k + 5}", etiqueta="DATO",
                             afirmacion=f"Requisito de entrada a {r['destino_nombre']} para el pasaporte de {r['nombre']} (Passport Index Data)",
                             valor=r["requisito"], fuente=desc, tipo_fuente=tipo, url=url,
                             archivo_local=rel(files["pi_tidy"]), sha256=sha256(files["pi_tidy"]),
                             cita_textual=f"Passport={iso}; Destination={dest}; Requirement={r['requisito']}"))
    fail("Henley Passport Index — serie histórica del puesto de Argentina", "https://www.henleyglobal.com/passport-index/ranking",
         "No usada", "Términos de uso lo prohíben (acceso automatizado y uso comercial sin licencia)",
         "Serie histórica sin fuente; el dato actual se sustituye por Passport Index Data (tipo R)")
    fail("uscode.house.gov (8 U.S.C. §1187)",
         "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title8-section1187&num=0&edition=prelim",
         "HTTP 200 con página 'Under Maintenance'", "Mantenimiento del sitio de la Cámara", "Se usó el texto de Cornell LII")
    fail("FederalRegister.gov (texto completo HTML/TXT)", "https://www.federalregister.gov/documents/full_text/html/2014/03/31/2014-07254.html",
         "Página 'Request Access' (CAPTCHA)", "Bloqueo anti-scraping; solo la API JSON está abierta",
         "Se usó la API para ubicar el documento y la copia oficial de GPO/govinfo.gov")

    # 2) Serie de rechazo
    ref_rows, meta = refusal_series()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    with (PROCESSED / "D_tasa_rechazo_B.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["fy", "pais", "iso2", "tasa_rechazo_ajustada_B", "bajo_umbral_3pct", "cita",
                                          "fuente_url", "captura_wayback", "timestamp_captura", "archivo_local", "sha256"])
        w.writeheader()
        for r in sorted(ref_rows, key=lambda r: (r["pais"], r["fy"])):
            w.writerow({**r, "bajo_umbral_3pct": r["tasa_rechazo_ajustada_B"] < 3.0})
    with (PROCESSED / "D_wayback_capturas.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["fy", "url", "captura", "ts", "archivo"])
        w.writeheader()
        for fy, m in meta.items():
            w.writerow(dict(fy=fy, **m))

    def rr(c, fy):
        return next((r for r in ref_rows if r["pais"] == c and r["fy"] == fy), None)

    n = 45
    for c, fy, txt in [("Argentina", 2025, "Tasa ajustada de rechazo de visas B, Argentina, FY2025 (último dato)"),
                       ("Argentina", 2024, "Tasa ajustada de rechazo de visas B, Argentina, FY2024"),
                       ("Chile", 2012, "Tasa ajustada de rechazo de visas B, Chile, FY2012 (año previo a la nominación)"),
                       ("Chile", 2013, "Tasa ajustada de rechazo de visas B, Chile, FY2013 (año previo a la designación)"),
                       ("Chile", 2025, "Tasa ajustada de rechazo de visas B, Chile, FY2025"),
                       ("Uruguay", 2025, "Tasa ajustada de rechazo de visas B, Uruguay, FY2025"),
                       ("Brazil", 2025, "Tasa ajustada de rechazo de visas B, Brasil, FY2025")]:
        r = rr(c, fy)
        if r:
            rows.append(dict(claim_id=f"D{n}", etiqueta="DATO", afirmacion=txt,
                             valor=f"{r['tasa_rechazo_ajustada_B']:.2f}%",
                             fuente=f"U.S. Department of State, Adjusted Refusal Rate - B-Visas Only, FY{fy} (captura Wayback {r['timestamp_captura']})",
                             tipo_fuente="P", url=r["captura_wayback"], archivo_local=r["archivo_local"], sha256=r["sha256"],
                             cita_textual=quote(local_text(ROOT / r["archivo_local"]), r["cita"])))
        n += 1
    ar = sorted((r["fy"], r["tasa_rechazo_ajustada_B"]) for r in ref_rows if r["pais"] == "Argentina")
    if ar:
        below = [fy for fy, v in ar if v < 3.0]
        rows.append(dict(claim_id=f"D{n}", etiqueta="ESTIMACIÓN",
                         afirmacion="Años fiscales (de los disponibles FY2006–FY2025) en que Argentina estuvo por debajo del 3%",
                         valor=f"{len(below)} de {len(ar)}" + (f" ({', '.join(map(str, below))})" if below else ""),
                         fuente="Cálculo propio sobre data/processed/D_tasa_rechazo_B.csv", tipo_fuente="P",
                         url="", archivo_local="data/processed/D_tasa_rechazo_B.csv", sha256=sha256(PROCESSED / "D_tasa_rechazo_B.csv"),
                         cita_textual="count(tasa_rechazo_ajustada_B < 3.0 | pais=Argentina); insumos D45–D46 y serie completa"))
    n += 1

    # 3) Overstay (CSV procesado)
    with (PROCESSED / "D_overstay.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fy", "pais", "categoria", "overstay_total_pct", "claim_id"])
        for fy, p, cid, v, cat in OVERSTAY:
            w.writerow([fy, p, cat, v, cid])

    # 4) NIV
    niv = niv_series()
    with (PROCESSED / "D_visas_B1B2_argentinos.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["fy", "pais", "clase", "emitidas", "hoja", "fila", "fuente_url",
                                          "captura_wayback", "timestamp_captura", "archivo_local", "sha256"])
        w.writeheader()
        w.writerows(niv)
    for fy in (2013, 2019, 2024, 2025):
        r = next((x for x in niv if x["fy"] == fy), None)
        if r:
            rows.append(dict(claim_id=f"D{n}", etiqueta="DATO", afirmacion=f"Visas B1/B2 emitidas a argentinos, FY{fy}",
                             valor=r["emitidas"], fuente=f"U.S. Department of State, FY{fy} NIV Detail Table (captura Wayback {r['timestamp_captura']})",
                             tipo_fuente="P", url=r["captura_wayback"], archivo_local=r["archivo_local"], sha256=r["sha256"],
                             cita_textual=f"hoja={r['hoja']}; fila_índice={r['fila']}; país=Argentina; columna={r['clase']}; valor={r['emitidas']}"))
        n += 1

    write_ledger(MODULO, rows)

    # 5) Gráficos
    if ref_rows:
        chart_refusal(ref_rows)
    chart_overstay()
    chart_niv(niv)
    if pcounts:
        chart_passports(pcounts)

    with (PROCESSED / "D_fuentes_fallidas.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["fecha", "fuente", "url", "error", "causa", "accion"])
        w.writeheader()
        w.writerows(FAILS)

    print(f"{len(rows)} afirmaciones -> docs/claims/claims_D.csv; {len(ref_rows)} filas de rechazo; {len(niv)} filas NIV; "
          f"{len(FAILS)} fallas")
    for c in COUNTRIES:
        s = sorted((r["fy"], r["tasa_rechazo_ajustada_B"]) for r in ref_rows if r["pais"] == c)
        print(f"  {c}: " + ", ".join(f"{fy}:{v}" for fy, v in s))


if __name__ == "__main__":
    main()
