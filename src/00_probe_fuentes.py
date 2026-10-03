"""Prueba de disponibilidad de fuentes (paso 0). Escribe docs/probe_fuentes.csv.

No descarga datos: solo verifica que la URL responde, el tipo de contenido y el tamaño.
"""
from __future__ import annotations

import csv
import datetime as dt

from common import DOCS, TODAY, get

Y = dt.date.today().strftime("%Y%m%d")

SOURCES = [
    # (modulo, id, descripcion, url)
    ("A", "anuncio_mecon", "Anuncio oficial programa CBI", "https://www.argentina.gob.ar/noticias/luis-caputo-anuncio-la-puesta-en-marcha-del-programa-de-ciudadania-por-inversion-de"),
    ("A", "bo_dec524_2025", "Decreto 524/2025 (BO)", "https://www.boletinoficial.gob.ar/detalleAviso/primera/329061/20250731"),
    ("A", "bo_dec285_2026", "Decreto 285/2026 (BO, PDF)", "https://www.boletinoficial.gob.ar/pdf/aviso/primera/341227/20260428"),
    ("A", "bo_dec366_2025", "DNU 366/2025 (BO)", "https://www.boletinoficial.gob.ar/detalleAviso/primera/326096/20250529"),
    ("A", "infoleg_dec366", "DNU 366/2025 texto (argentina.gob.ar/normativa)", "https://www.argentina.gob.ar/normativa/nacional/decreto-366-2025-413297/texto"),
    ("A", "hcdn_bicameral", "HCDN Bicameral Trámite Legislativo", "https://www.hcdn.gob.ar/comisiones/especiales/"),
    ("A", "senado_comisiones", "Senado - Comisiones", "https://www.senado.gob.ar/parlamentario/comisiones/"),
    # B
    ("B", "fed_dfa_zip", "Fed DFA descarga CSV", "https://www.federalreserve.gov/releases/z1/dataviz/download/zips/dfa.zip"),
    ("B", "fed_scf2022_summary", "SCF 2022 summary extract (Stata)", "https://www.federalreserve.gov/econres/files/scfp2022s.zip"),
    ("B", "fed_scf_index", "SCF índice", "https://www.federalreserve.gov/econres/scfindex.htm"),
    ("B", "ubs_gwr", "UBS Global Wealth Report", "https://www.ubs.com/global/en/wealthmanagement/insights/global-wealth-report.html"),
    ("B", "knightfrank_wr", "Knight Frank Wealth Report", "https://www.knightfrank.com/wealthreport"),
    ("B", "altrata_wuwr", "Altrata World Ultra Wealth Report", "https://altrata.com/reports/world-ultra-wealth-report-2026"),
    ("B", "henley_api", "Henley Passport Index API", "https://api.henleypassportindex.com/api/v3/countries"),
    ("B", "henley_web", "Henley Passport Index web", "https://www.henleyglobal.com/passport-index/ranking"),
    # C
    ("C", "eurlex_vanuatu", "EUR-Lex búsqueda Vanuatu visa suspension", "https://eur-lex.europa.eu/search.html?text=Vanuatu%20visa%20suspension&scope=EURLEX&type=quick&lang=en"),
    ("C", "curia_c181_23", "CJEU C-181/23 Comisión c. Malta", "https://curia.europa.eu/juris/liste.jsf?num=C-181/23&language=en"),
    ("C", "dominica_cbiu", "Dominica CBIU", "https://cbiu.gov.dm/"),
    ("C", "stkitts_ciu", "St Kitts & Nevis CIU", "https://ciu.gov.kn/"),
    ("C", "antigua_cip", "Antigua & Barbuda CIU", "https://cip.gov.ag/"),
    ("C", "grenada_ibu", "Grenada CBI", "https://www.imm.gov.gd/"),
    ("C", "stlucia_cip", "St Lucia CIP", "https://www.cipsaintlucia.com/"),
    ("C", "imf_api", "IMF DataMapper API (PBI)", "https://www.imf.org/external/datamapper/api/v1/NGDPD/DMA"),
    ("C", "imf_dominica", "IMF Dominica country page", "https://www.imf.org/en/Countries/DMA"),
    # D
    ("D", "dos_refusal_fy25", "DoS adjusted refusal rate B FY25", "https://travel.state.gov/content/dam/visas/Statistics/Non-Immigrant-Statistics/RefusalRates/FY25.pdf"),
    ("D", "dos_refusal_page", "DoS refusal rates página", "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/nonimmigrant-visa-statistics.html"),
    ("D", "dos_visa_office_report", "Report of the Visa Office índice", "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-statistics/annual-reports.html"),
    ("D", "uscode_1187", "8 U.S.C. §1187 (uscode.house.gov)", "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title8-section1187&num=0&edition=prelim"),
    ("D", "cornell_1187", "8 U.S.C. §1187 (Cornell LII)", "https://www.law.cornell.edu/uscode/text/8/1187"),
    ("D", "dhs_vwp", "DHS Visa Waiver Program", "https://www.dhs.gov/visa-waiver-program"),
    # E
    ("E", "wikimedia_pv", "Wikimedia Pageviews API", f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/Argentina/monthly/20150701/{Y}"),
    ("E", "google_trends", "Google Trends (explore)", "https://trends.google.com/trends/api/explore?hl=en-US&tz=0&req=%7B%22comparisonItem%22%3A%5B%7B%22keyword%22%3A%22Argentina%22%2C%22geo%22%3A%22US%22%2C%22time%22%3A%22all%22%7D%5D%2C%22category%22%3A0%2C%22property%22%3A%22%22%7D"),
    ("E", "yvera_datos", "datos.yvera.gob.ar (CKAN API)", "https://datos.yvera.gob.ar/api/3/action/package_search?q=eti"),
    ("E", "indec_eti", "INDEC ETI", "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-13-56"),
    ("E", "ntto_i92", "NTTO (trade.gov) outbound", "https://www.trade.gov/us-international-air-travel-statistics-i-92-data"),
    ("E", "ntto_outbound", "NTTO outbound overview", "https://www.trade.gov/travel-and-tourism-research"),
    ("E", "bcra_itcrm", "BCRA ITCRM serie (xlsx)", "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/ITCRMSerie.xlsx"),
    ("E", "bcra_api", "BCRA API estadísticas v4", "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias"),
    ("E", "census_api", "Census ACS API B05006", "https://api.census.gov/data/2023/acs/acs1?get=NAME,group(B05006)&for=us:1"),
    ("E", "dhs_yearbook", "DHS OHSS Yearbook", "https://ohss.dhs.gov/topics/immigration/yearbook"),
    # F
    ("F", "wb_wgi", "World Bank API WGI", "https://api.worldbank.org/v2/country/ARG/indicator/GOV_WGI_RL.EST?format=json&source=3"),
    ("F", "wb_api", "World Bank API (inflación)", "https://api.worldbank.org/v2/country/ARG/indicator/FP.CPI.TOTL.ZG?format=json"),
    ("F", "iep_gpi", "Global Peace Index (Vision of Humanity)", "https://www.visionofhumanity.org/maps/"),
    ("F", "faostat_api", "FAOSTAT API", "https://faostatservices.fao.org/api/v1/en/definitions/domain"),
    ("F", "faostat_bulk", "FAOSTAT bulk (Food Balance)", "https://bulks-faostat.fao.org/production/FoodBalanceSheets_E_All_Data_(Normalized).zip"),
    ("F", "energia_datos", "datos.energia.gob.ar CKAN", "https://datos.energia.gob.ar/api/3/action/package_search?q=produccion"),
    ("F", "usgs_lithium", "USGS MCS Lithium 2026", "https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-lithium.pdf"),
    ("F", "unesco_whc", "UNESCO WHC list XML", "https://whc.unesco.org/en/list/xml/"),
    ("F", "wjp", "WJP Rule of Law Index", "https://worldjusticeproject.org/rule-of-law-index/"),
    ("F", "datos_gob_series", "API Series de Tiempo (datos.gob.ar)", "https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELNAL_DICI_M_26&limit=5"),
    ("F", "indec_ipc", "INDEC IPC", "https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31"),
    # G
    ("G", "bcra_reservas", "BCRA API variables (reservas)", "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias/1?limit=5"),
    ("G", "finanzas_deuda", "Sec. Finanzas - deuda pública", "https://www.argentina.gob.ar/economia/finanzas/deuda-publica"),
    # Copias de archivo (Wayback Machine) para fuentes primarias que bloquean clientes automatizados (403)
    ("D", "wb_dos_refusal_fy25", "Wayback: DoS refusal rate B FY25", "https://archive.org/wayback/available?url=travel.state.gov/content/dam/visas/Statistics/Non-Immigrant-Statistics/RefusalRates/FY25.pdf"),
    ("F", "wb_unesco_whc", "Wayback: UNESCO WHC list XML", "https://archive.org/wayback/available?url=whc.unesco.org/en/list/xml/"),
]


def main() -> None:
    out = DOCS / "probe_fuentes.csv"
    rows = []
    for mod, sid, desc, url in SOURCES:
        try:
            r = get(url, retries=2, timeout=40, stream=True)
            size = r.headers.get("Content-Length", "")
            ctype = r.headers.get("Content-Type", "").split(";")[0]
            status = r.status_code
            final = r.url
            r.close()
            note = ""
        except Exception as e:  # noqa: BLE001
            status, ctype, size, final, note = "ERR", "", "", "", type(e).__name__ + ": " + str(e)[:120]
        ok = isinstance(status, int) and 200 <= status < 300
        rows.append(dict(modulo=mod, id=sid, descripcion=desc, url=url, status=status, ok=ok,
                         content_type=ctype, bytes=size, url_final=final, nota=note, fecha=TODAY))
        print(f"[{mod}] {sid:24s} {status} {ctype:28s} {'OK' if ok else 'FALLA'} {note}")
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\n{sum(r['ok'] for r in rows)}/{len(rows)} fuentes responden. -> {out}")


if __name__ == "__main__":
    main()
