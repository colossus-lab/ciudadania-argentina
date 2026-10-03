"""Módulo C — Benchmark de programas de ciudadanía por inversión (CBI).

Responde, con fuente primaria descargada a data/raw/:
  1. Montos mínimos vigentes (fuente gubernamental: web oficial del programa o reglamento SRO/SI).
  2. Recaudación CBI en USD y % del PBI por año (FMI: Article IV, tablas extraídas con pdfplumber;
     PBI de la API DataMapper del FMI).
  3. Casos regulatorios (UE: Vanuatu, Reg. 2025/2441, TJUE C-181/23; EE.UU.: proclamación 2025;
     cierres de golden visas en Portugal, España, Reino Unido, Irlanda).
  4. Posicionamiento de Argentina (monto y pasaporte, con data/processed/B_pasaportes_destinos.csv).
  5. Gráficos: outputs/charts/C_montos_minimos.{png,svg} y C_recaudacion_pbi.{png,svg}.

Salidas: data/processed/C_*.csv, outputs/charts/C_*, docs/claims/claims_C.csv (vía write_ledger).
Corre de punta a punta desde las copias de data/raw (solo descarga lo que falte).
"""
from __future__ import annotations

import csv
import json
import re
import time
from pathlib import Path

import pdfplumber
import requests

from common import (CHARTS, PROCESSED, RAW, ROOT, download, local_text, norm_ws, quote, sha256,
                    write_ledger)

MODULO = "C"
UA_IMF = "https://www.imf.org/-/media/Files/Publications/CR/{y}/English/{f}"
CELLAR = "https://publications.europa.eu/resource/celex/{}"
CELLAR_H = {"Accept": "application/xhtml+xml", "Accept-Language": "eng"}
EC_PER_USD = 2.70  # paridad fija del dólar del Caribe Oriental (claim C42)

# --------------------------------------------------------------------------------------------------
# Fuentes: id -> (url, nombre local, ext, descripción, tipo, headers)
# --------------------------------------------------------------------------------------------------
SOURCES: dict[str, tuple] = {
    # ---- Montos (gobiernos) ----
    "kna_sisc": ("https://ciu.gov.kn/sustainable-island-state-contribution/", "C_kna_ciu_sisc", "html",
                 "St Kitts y Nevis, Citizenship Unit: Sustainable Island State Contribution (ciu.gov.kn)", "P", None),
    "kna_re": ("https://ciu.gov.kn/real-estate-investment/", "C_kna_ciu_real_estate", "html",
               "St Kitts y Nevis, Citizenship Unit: Real Estate Investment (ciu.gov.kn)", "P", None),
    "kna_notices": ("https://ciu.gov.kn/government-notices/", "C_kna_ciu_government_notices", "html",
                    "St Kitts y Nevis, Citizenship Unit: Government Notices (lista de SRO)", "P", None),
    "kna_sro20": ("https://ciu.gov.kn/wp-content/uploads/2025/01/sro-20-of-2024.pdf", "C_kna_sro20_2024", "pdf",
                  "St Kitts y Nevis, SRO No. 20 of 2024 (Citizenship by Substantial Investment Regulations, 8/7/2024)", "P", None),
    "kna_sro43": ("https://ciu.gov.kn/wp-content/uploads/2025/01/SRO-43-of-2024.pdf", "C_kna_sro43_2024", "pdf",
                  "St Kitts y Nevis, SRO No. 43 of 2024 (Amendment Regulations, 25/10/2024)", "P", None),
    "atg_ndf": ("https://cip.gov.ag/investment-options/ndf/", "C_atg_cip_ndf", "html",
                "Antigua y Barbuda, Citizenship by Investment Unit: National Development Fund (cip.gov.ag)", "P", None),
    "atg_re": ("https://cip.gov.ag/investment-options/real-estate/", "C_atg_cip_real_estate", "html",
               "Antigua y Barbuda, Citizenship by Investment Unit: Real Estate (cip.gov.ag)", "P", None),
    "atg_si50": ("https://cip.gov.ag/wp-content/uploads/2024/08/Antigua-and-Barbuda-Citizenship-By-Investment-Amendment-Regulations-2024.pdf",
                 "C_atg_si50_2024", "pdf",
                 "Antigua y Barbuda, Citizenship by Investment (Amendment) Regulations 2024, S.I. 2024 No. 50 (PDF escaneado)", "P", None),
    "grd_sro15": ("https://www.laws.gov.gd/index.php/s-r-o/1527-sr-o-15-of-2024-grenada-citizenship-by-investment-amendment-no-2-regulations/download",
                  "C_grd_sro15_2024", "pdf",
                  "Granada, SRO No. 15 of 2024 (Grenada Citizenship by Investment (Amendment) (No. 2) Regulations), laws.gov.gd", "P", None),
    "lca_cbi": ("https://www.cipsaintlucia.com/citizenship-by-investment", "C_lca_cip_cbi", "html",
                "Santa Lucía, Citizenship by Investment Unit: Citizenship by Investment (cipsaintlucia.com)", "P", None),
    "lca_si106": ("https://www.cipsaintlucia.com/s/SI-No-106-of-2024-Citizenship-by-Investment-Amendment-No-2-Regulations.pdf",
                  "C_lca_si106_2024", "pdf", "Santa Lucía, S.I. No. 106 of 2024 (CBI (Amendment) (No. 2) Regulations)", "P", None),
    "lca_si57": ("https://www.cipsaintlucia.com/s/SI-57-of-2026-Citizenship-by-Investment-Amendment-Regulations.pdf",
                 "C_lca_si57_2026", "pdf", "Santa Lucía, S.I. No. 57 of 2026 (CBI (Amendment) Regulations, 23/3/2026)", "P", None),
    "tur_yon": ("https://www.mevzuat.gov.tr/MevzuatMetin/21.5.2010139.pdf", "C_tur_yonetmelik_2010_139", "pdf",
                "Turquía, Türk Vatandaşlığı Kanununun Uygulanmasına İlişkin Yönetmelik (texto consolidado, mevzuat.gov.tr)", "P", None),
    "nru_contrib": ("https://www.ecrcp.gov.nr/contribution", "C_nru_ecrcp_contribution", "html",
                    "Nauru, Economic and Climate Resilience Citizenship Program: Contribution (ecrcp.gov.nr)", "P", None),
    "nru_fact25": ("https://www.ecrcp.gov.nr/files/N_Factsheet_250313_1_Digital.pdf", "C_nru_factsheet_2025-03", "pdf",
                   "Nauru, ECRCP Factsheet (marzo 2025, ecrcp.gov.nr)", "P", None),
    "mlt_act21": ("https://legislation.mt/eli/act/2025/21/eng/pdf", "C_mlt_act_XXI_2025", "pdf",
                  "Malta, Act No. XXI of 2025 (Maltese Citizenship (Amendment) Act, 2025), legislation.mt", "P", None),
    # ---- FMI: Article IV ----
    "imf_dma25": (UA_IMF.format(y=2025, f="1dmaea2025001-print-pdf.ashx"), "C_imf_dma_cr25-130", "pdf",
                  "FMI, Dominica: 2025 Article IV (Country Report 25/130)", "P", None),
    "imf_dma22": (UA_IMF.format(y=2022, f="1DMAEA2022001.ashx"), "C_imf_dma_cr22-40", "pdf",
                  "FMI, Dominica: 2021 Article IV (Country Report 22/40)", "P", None),
    "imf_kna25": (UA_IMF.format(y=2025, f="1knaea2025001-print-pdf.ashx"), "C_imf_kna_cr25-107", "pdf",
                  "FMI, St Kitts y Nevis: 2025 Article IV (Country Report 25/107)", "P", None),
    "imf_kna18": (UA_IMF.format(y=2022, f="1KNAEA2022001.ashx"), "C_imf_kna_cr22-351", "pdf",
                  "FMI, St Kitts y Nevis: 2018 Article IV (publicado como Country Report 22/351)", "P", None),
    "imf_atg25": (UA_IMF.format(y=2025, f="1atgea2025001-print-pdf.ashx"), "C_imf_atg_cr25-96", "pdf",
                  "FMI, Antigua y Barbuda: 2025 Article IV (Country Report 25/96)", "P", None),
    "imf_grd25": (UA_IMF.format(y=2025, f="1grdea2025001-print-pdf.ashx"), "C_imf_grd_cr25-39", "pdf",
                  "FMI, Granada: 2024 Article IV (Country Report 25/39)", "P", None),
    "imf_lca25": (UA_IMF.format(y=2025, f="1lcaea2025001-print-pdf.ashx"), "C_imf_lca_cr25-65", "pdf",
                  "FMI, Santa Lucía: 2024 Article IV (Country Report 25/65)", "P", None),
    "imf_vut24": (UA_IMF.format(y=2024, f="1vutea2024001-print-pdf.ashx"), "C_imf_vut_cr24-278", "pdf",
                  "FMI, Vanuatu: 2024 Article IV (Country Report 24/278)", "P", None),
    "imf_dm": ("https://www.imf.org/external/datamapper/api/v1/NGDPD/DMA/KNA/ATG/GRD/LCA/VUT",
               "C_imf_datamapper_NGDPD", "json", "FMI, API DataMapper, serie NGDPD (PBI nominal, miles de millones de USD)", "P", None),
    # ---- Casos regulatorios ----
    "eu_vut_2022": (CELLAR.format("32022D0366"), "C_eu_dec2022_366_vanuatu", "html",
                    "Decisión (UE) 2022/366 del Consejo (suspensión parcial del acuerdo de exención de visados con Vanuatu), Oficina de Publicaciones de la UE", "P", CELLAR_H),
    "eu_vut_2024": (CELLAR.format("32024R2059"), "C_eu_reg2024_2059_vanuatu", "html",
                    "Reglamento Delegado (UE) 2024/2059 (prórroga de la suspensión temporal para Vanuatu), Oficina de Publicaciones de la UE", "P", CELLAR_H),
    "eu_vut_2025": (CELLAR.format("32025R0011"), "B_eu_reg2025_11_vanuatu", "html",
                    "Reglamento (UE) 2025/11 (Vanuatu pasa al Anexo I), Oficina de Publicaciones de la UE (copia del Módulo B)", "P", CELLAR_H),
    "eu_vsm": (CELLAR.format("32025R2441"), "C_eu_reg2025_2441_mecanismo_suspension", "html",
               "Reglamento (UE) 2025/2441 (revisión del mecanismo de suspensión de visados), Oficina de Publicaciones de la UE", "P", CELLAR_H),
    "cjeu_c181": (CELLAR.format("62023CJ0181"), "C_tjue_C-181-23_es", "html",
                  "TJUE (Gran Sala), sentencia de 29/04/2025, C-181/23, Comisión c. Malta (versión ES, Oficina de Publicaciones de la UE)", "P",
                  {"Accept": "application/xhtml+xml", "Accept-Language": "spa"}),
    "us_procl": ("https://www.govinfo.gov/content/pkg/FR-2025-12-19/pdf/2025-23570.pdf", "C_us_fr_2025-23570_proclamacion", "pdf",
                 "EE.UU., Proclamación presidencial 'Restricting and Limiting the Entry of Foreign Nationals…', Federal Register 2025-23570 (19/12/2025)", "P", None),
    "atg_us_stmt": ("https://cip.gov.ag/statement-by-sir-ronald-sanders/", "C_atg_statement_us_restrictions", "html",
                    "Antigua y Barbuda, CIU: Statement on U.S. Visa Restrictions (19/12/2025)", "P", None),
    "esp_lo1": ("https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-76", "C_esp_boe_lo1_2025", "html",
                "España, Ley Orgánica 1/2025 (BOE-A-2025-76)", "P", None),
    "prt_l56": ("https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/legislacao/diplomas_legislativos/Documents/Lei_56_2023.pdf",
                "C_prt_lei56_2023", "pdf", "Portugal, Lei n.º 56/2023 (Mais Habitação), texto consolidado del Portal das Finanças (AT)", "P", None),
    "gbr_t1": ("https://www.gov.uk/government/news/tier-1-investor-visa-route-closes-over-security-concerns", "C_gbr_tier1_cierre", "html",
               "Reino Unido, Home Office: 'Tier 1 Investor Visa route closes over security concerns' (gov.uk, 17/02/2022)", "P", None),
    "irl_iip": ("https://www.irishimmigration.ie/minister-harris-announces-closure-of-the-immigrant-investor-programme/", "C_irl_iip_cierre", "html",
                "Irlanda, Immigration Service Delivery (Dept. of Justice): cierre del Immigrant Investor Programme", "P", None),
    # ---- Argentina (Módulo A) ----
    "anuncio": ("https://www.argentina.gob.ar/noticias/luis-caputo-anuncio-la-puesta-en-marcha-del-programa-de-ciudadania-por-inversion-de",
                "A_anuncio_mecon", "html", "Ministerio de Economía, anuncio del 02/10/2026 (copia del Módulo A)", "P", None),
}

# Fuentes que fallaron (intentos registrados el 2026-10-03). Se escriben a data/processed/C_fuentes_fallidas.csv.
FAILED = [
    ("Dominica — CBIU (montos y SRO 8/2024)", "https://www.cbiu.gov.dm/investment-options/",
     "HTTP 202 + redirección a /.well-known/sgcaptcha/", "Captcha anti-bots (SiteGround) en todo el sitio, incluidos los PDF",
     "Wayback: web.archive.org inaccesible (conexión reiniciada por el proxy); fila de Dominica queda 'no verificado'"),
    ("Dominica — Gobierno (S.R.O. 1 y 8 de 2024)", "https://www.dominica.gov.dm/laws/2024/commonwealth_of_dominica_citizenship_by_investment_regulations_sro_8_of_2024.pdf",
     "502 Bad Gateway (CONNECT) / connection reset", "Host caído o bloqueado", "Sin alternativa gubernamental; se usa solo el piso regional del MoA (FMI) como contexto"),
    ("Wayback Machine (copias de sitios bloqueados)", "https://web.archive.org/web/20260916071416id_/https://www.cbiu.gov.dm/investment-options/",
     "Connection reset (ws_closed_mid_exchange)", "El túnel al host web.archive.org se corta; archive.org/wayback/available sí responde",
     "Se registra la captura existente (20260916071416) pero no se pudo descargar"),
    ("Granada — imm.gov.gd", "https://www.imm.gov.gd/", "502 Bad Gateway (CONNECT)", "Host caído",
     "Se usó laws.gov.gd (SRO 15/2024, texto oficial)"),
    ("Granada — Investment Migration Agency (imagrenada.gd)", "https://imagrenada.gd/wp-content/uploads/2024/07/S.R.O.-15-of-2024-Grenada-Citizenship-by-Investment-Amendment-No.-2-Regulations.pdf",
     "HTTP 202 + sgcaptcha", "Captcha anti-bots", "Se usó la misma SRO desde laws.gov.gd"),
    ("Vanuatu — legislación CBI (PacLII)", "https://www.paclii.org/vu/legis/num_reg/", "HTTP 403", "Bloqueo anti-bots",
     "Monto mínimo de Vanuatu queda 'no verificado' (la prensa no se usa)"),
    ("Vanuatu — Citizenship Office", "https://citizenship.gov.vu/", "502 Bad Gateway (CONNECT)", "Host caído o inexistente",
     "Idem; se usa el FMI (Article IV 2024) solo para la recaudación ECP"),
    ("Jordania — Jordan Investment Commission", "https://www.jic.gov.jo/en/", "Connection reset by peer", "Host inaccesible",
     "moin.gov.jo redirige todo a la portada árabe; monto de Jordania 'no verificado'"),
    ("Egipto — decreto del Primer Ministro 876/2023", "https://www.state.gov/reports/2024-investment-climate-statements/egypt/",
     "HTTP 403 (state.gov); no se halló el Boletín Oficial egipcio en línea", "Anti-bots / fuente no publicada en abierto",
     "Monto de Egipto 'no verificado'"),
    ("FMI — Article IV 2026 (St Kitts CR 26/93, Dominica CR 26/117)", "https://www.imf.org/en/publications/cr/issues/2026/05/07/st-575691",
     "HTTP 403 (páginas imf.org); eLibrary devuelve 202 vacío", "Anti-bots; los PDF 2026 no siguen el patrón -/media/…ashx",
     "Serie de recaudación cortada en 2024 (estimación de los Article IV 2025)"),
    ("FMI — Antigua 2022 Article IV (CR 23/184), tablas fiscales", "https://www.imf.org/-/media/Files/Publications/CR/2023/English/1ATGEA2023001.ashx",
     "Descarga OK; tablas como imagen", "Sin capa de texto en las tablas", "Antigua solo 2020–2024"),
    ("EUR-Lex (HTML de reglamentos)", "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32025R2441",
     "HTTP 202 con cuerpo vacío", "Desafío anti-bots (WAF)", "Mismo texto oficial vía Oficina de Publicaciones (publications.europa.eu/resource/celex/…)"),
    ("Curia (TJUE)", "https://curia.europa.eu/juris/liste.jsf?num=C-181/23&language=en",
     "200, pero redirige a infocuria (aplicación JavaScript)", "Contenido renderizado en el navegador", "Sentencia oficial vía Oficina de Publicaciones (CELEX 62023CJ0181)"),
    ("Portugal — Diário da República", "https://diariodarepublica.pt/dr/detalhe/lei/56-2023-221792115",
     "200 con 2 KB (aplicación JavaScript)", "Contenido renderizado en el navegador", "Texto consolidado de la AT (Portal das Finanças)"),
    ("Turquía — Resmî Gazete 13/05/2022 (C.K. 5554)", "https://www.resmigazete.gov.tr/eskiler/2022/05/20220513-20.pdf",
     "PDF sin capa de texto", "Escaneo", "Texto consolidado del reglamento en mevzuat.gov.tr"),
]

# --------------------------------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------------------------------
_page_cache: dict[Path, list[str]] = {}


def pages(path: Path) -> list[str]:
    if path not in _page_cache:
        with pdfplumber.open(path) as pdf:
            _page_cache[path] = [p.extract_text() or "" for p in pdf.pages]
    return _page_cache[path]


def fetch(sid: str) -> Path:
    url, name, ext, _d, _t, headers = SOURCES[sid]
    kw = {"headers": headers} if headers else {}
    for i in range(4):
        try:
            p = download(url, name, ext, **kw)
            if ext == "pdf" and not p.read_bytes()[:5].startswith(b"%PDF"):
                p.unlink()
                raise ValueError(f"{sid}: la respuesta no es un PDF")
            return p
        except (requests.HTTPError, requests.ConnectionError, ValueError) as e:
            if i == 3:
                raise
            print(f"  reintento {sid}: {e}")
            time.sleep(10 * (i + 1))
    raise RuntimeError(sid)


def find_page(path: Path, needle: str) -> int:
    n = norm_ws(needle)
    for i, t in enumerate(pages(path), 1):
        if n in norm_ws(t):
            return i
    raise ValueError(f"{path.name}: no se encontró en ninguna página: {n[:60]}")


def table_row(path: Path, page: int, label: str, n: int, occurrence: int = 1) -> tuple[list[float], str]:
    """Busca en la página la fila que empieza con `label` (comparación sin espacios) y devuelve
    los primeros n valores numéricos y la cita literal (etiqueta + esos n valores)."""
    key = re.sub(r"\s", "", label).lower()
    hits = [ln for ln in pages(path)[page - 1].split("\n") if re.sub(r"\s", "", ln).lower().startswith(key)]
    if len(hits) < occurrence:
        raise ValueError(f"{path.name} p.{page}: fila '{label}' no encontrada")
    line = hits[occurrence - 1]
    toks = line.split()
    nums: list[str] = []
    for tok in reversed(toks):
        if re.fullmatch(r"-?[\d,]*\d(\.\d+)?", tok):
            nums.append(tok)
        else:
            break
    nums.reverse()
    first = len(toks) - len(nums)
    vals = nums[:n]
    if len(vals) < n:
        raise ValueError(f"{path.name} p.{page}: fila '{label}' tiene menos de {n} valores")
    cita = " ".join(toks[: first + n])
    return [float(v.replace(",", "")) for v in vals], cita


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


# --------------------------------------------------------------------------------------------------
# 1. Montos mínimos: (claim_id, país, programa/vía, tipo, monto USD, familia tipo USD, vigencia, fuente, citas)
# --------------------------------------------------------------------------------------------------
MONTOS = [
    ("C01", "St Kitts y Nevis", "Sustainable Island State Contribution (SISC)", "Donación a fondo", 250000, 250000,
     "SRO 20/2024 (8/7/2024)", "kna_sisc", ["Main Applicant or Family (up to four members): US$250,000"]),
    ("C02", "St Kitts y Nevis", "SISC — texto reglamentario", "Donación a fondo", 250000, 250000, "SRO 20/2024 (8/7/2024)", "kna_sro20",
     ["(a) US$250,000 (Two Hundred and Fifty Thousand United States Dollars) for a main applicant or a family with up to four total persons"]),
    ("C03", "St Kitts y Nevis", "Inversión inmobiliaria en desarrollo aprobado", "Inmobiliario", 325000, None,
     "SRO 43/2024 (publicado 25/10/2024)", "kna_sro43",
     ["US$325,000 (Three Hundred and Twenty-Five Thousand United States Dollars)",
      "Published 25th October 2024, Extra-Ordinary Gazette No. 66 of 2024"]),
    ("C04", "Antigua y Barbuda", "National Development Fund (NDF)", "Donación a fondo", 230000, 230000,
     "S.I. 2024 No. 50 (hecho 25/7/2024; oferta previa vencida 31/7/2024)", "atg_ndf",
     ["A. For a single applicant US$230,000 contribution", "B. For a family of 4 or less US$230,000 contribution"]),
    ("C06", "Antigua y Barbuda", "Inmueble aprobado", "Inmobiliario", 300000, None, "Web oficial (consulta 03/10/2026)", "atg_re",
     ["may choose to purchase property valued at minimum US$300,000"]),
    ("C07", "Granada", "National Transformation Fund (NTF)", "Donación a fondo", 235000, 235000, "SRO 15/2024, en vigor 1/7/2024",
     "grd_sro15", ["National Transformation Fund $235,000.00 Main Applicant and up to 3 dependants",
                   "These Regulations shall come into force on the first day of July 2024."]),
    ("C09", "Granada", "Unidad en proyecto aprobado (cuota) / proyecto aprobado", "Inmobiliario", 270000, None,
     "SRO 15/2024, en vigor 1/7/2024", "grd_sro15", ["under Section 11– $270,000.00", "11 $350,000.00"]),
    ("C10", "Santa Lucía", "National Economic Fund (NEF)", "Donación a fondo", 240000, 240000,
     "S.I. 106/2024, en vigor (retroactivo) 1/7/2024", "lca_cbi",
     ["Applicant alone with up to three other qualifying dependents: US $240,000"]),
    ("C11", "Santa Lucía", "NEF — texto reglamentario", "Donación a fondo", 240000, 240000, "S.I. 106/2024", "lca_si106",
     ["These Regulations are deemed to have come into force on the 1st day of July, 2024.",
      "Applicant applying with up to US$ 240,000 three qualifying dependents"]),
    ("C14", "Turquía", "Compra de inmueble (3 años sin vender)", "Inmobiliario", 400000, None,
     "Reglamento 2010/139 art. 20, mod. RG 31711 (6/1/2022) y RG 31834 (13/5/2022)", "tur_yon",
     ["b) (Değişik:RG-6/1/2022-31711-C.K-5072/1 md.) En az 400.000 Amerikan Doları"]),
    ("C15", "Turquía", "Capital fijo, depósito bancario o bonos del Estado (3 años)", "Inversión / depósito / bono", 500000, None,
     "Reglamento 2010/139 art. 20, mod. RG 31711 (6/1/2022)", "tur_yon",
     ["a) (Değişik:RG-6/1/2022-31711-C.K-5072/1 md.) En az 500.000 Amerikan Doları veya karşılığı döviz tutarında sabit sermaye yatırımı",
      "En az 500.000 Amerikan Doları veya karşılığı döviz tutarında Devlet borçlanma araçlarını üç yıl tutmak şartıyla"]),
    ("C16", "Nauru", "ECRCP — oferta por tiempo limitado", "Donación a fondo", 90000, None,
     "Desde 3/2/2026, solicitudes hasta 31/12/2026", "nru_contrib",
     ["A discount of USD 25,000 will apply to the contribution amount from 3 February 2026 for all current or new applications filed prior to 31 December 2026.",
      "USD 90,000 for a Principal Applicant (limited time offer available until 31 December 2026)"]),
    ("C17", "Nauru", "ECRCP — monto regular", "Donación a fondo", 105000, None, "Factsheet oficial, marzo 2025", "nru_fact25",
     ["starting at USD 105,000 for a single Principal Applicant."]),
]

# Filas de la tabla final (país, vía, tipo, USD principal, familia tipo, vigencia, estado, claim_ids)
TABLA_EXTRA = [
    ("Dominica", "Economic Diversification Fund", "Donación a fondo", None, None, "—",
     "NO VERIFICADO: cbiu.gov.dm con captcha anti-bots y dominica.gov.dm caído; piso regional MoA 03/2024 = USD 200.000 (C20)", "C20"),
    ("Vanuatu", "Development Support Program", "Donación a fondo", None, None, "—",
     "NO VERIFICADO: sin fuente gubernamental accesible (PacLII 403; sitio oficial caído)", ""),
    ("Egipto", "Decreto PM 876/2023", "Donación / inmueble / depósito", None, None, "—",
     "NO VERIFICADO: decreto no disponible en abierto; state.gov 403", ""),
    ("Jordania", "Criterios del Consejo de Ministros", "Depósito / bonos / inversión", None, None, "—",
     "NO VERIFICADO: jic.gov.jo inaccesible; moin.gov.jo redirige a portada", ""),
    ("Malta", "MEIN (naturalización por inversión directa)", "Donación + inmueble", None, None, "Derogado (Act XXI 2025, 24/7/2025)",
     "SIN PROGRAMA: tras C-181/23 la vía por inversión fue sustituida por naturalización 'por mérito'", "C18; C19; C56"),
]


def montos(files, texts) -> tuple[list[dict], list[dict]]:
    rows, ledger = [], []
    for cid, pais, via, tipo, usd, fam, vig, sid, needles in MONTOS:
        f = files[sid]
        citas = []
        for nd in needles:
            q = quote(texts[sid], nd)
            pref = f"[p. {find_page(f, nd)}] " if f.suffix == ".pdf" else ""
            citas.append(pref + q)
        url, _n, _e, desc, tipo_f, _h = SOURCES[sid]
        ledger.append(dict(claim_id=cid, etiqueta="DATO",
                           afirmacion=f"{pais}: monto mínimo — {via} ({tipo})" + (f"; familia tipo {fam:,} USD" if fam else ""),
                           valor=f"USD {usd:,}".replace(",", "."), fuente=desc, tipo_fuente=tipo_f, url=url,
                           archivo_local=rel(f), sha256=sha256(f), cita_textual=" | ".join(citas)))
        if "texto reglamentario" not in via:
            rows.append(dict(pais=pais, via=via, tipo_aporte=tipo, monto_min_principal_usd=usd,
                             monto_familia_tipo_usd=fam if fam else "", vigencia=vig, estado="verificado",
                             claim_id=cid, fuente=desc, url=url))
    # Antigua S.I. 2024 No. 50: PDF escaneado sin capa de texto -> lectura visual (no verificable con quote()).
    f = files["atg_si50"]
    assert not "".join(pages(f)).strip(), "El S.I. 50/2024 ahora tiene texto: reemplazar la lectura visual por quote()"
    url, _n, _e, desc, tipo_f, _h = SOURCES["atg_si50"]
    ledger.append(dict(
        claim_id="C05", etiqueta="DATO",
        afirmacion="Antigua y Barbuda: el S.I. 2024 No. 50 fija la contribución al NDF en USD 230.000 (soltero o familia) y pone fin a la 'limited time offer' el 31/7/2024",
        valor="USD 230.000; vigencia desde 1/8/2024", fuente=desc, tipo_fuente=tipo_f, url=url, archivo_local=rel(f), sha256=sha256(f),
        cita_textual="[LECTURA VISUAL — PDF escaneado sin capa de texto; no verificable con quote(). p. 7, reg. 7(1): "
                     "'a contribution to the National Development Fund and where that contribution is in the amount of Two Hundred and "
                     "Thirty Thousand (US$230,000.00) dollars'; reg. 7(2): 'until the 31st July 2024 at 11:59 p.m. after which this limited "
                     "time offer shall cease'; p. 9: 'MADE this 25th day of July, 2024'; 'Passed by Resolution of the House of "
                     "Representatives this 18th day of July 2024']"))
    for pais, via, tipo, usd, fam, vig, estado, cids in TABLA_EXTRA:
        rows.append(dict(pais=pais, via=via, tipo_aporte=tipo, monto_min_principal_usd="", monto_familia_tipo_usd="",
                         vigencia=vig, estado=estado, claim_id=cids, fuente="", url=""))
    return rows, ledger


# --------------------------------------------------------------------------------------------------
# 2. Recaudación CBI (FMI)
# --------------------------------------------------------------------------------------------------
# (claim_id, iso3, sid, page, label, years, unidad, concepto, occurrence)
SERIES = [
    ("C30", "DMA", "imf_dma25", 35, "Citizenship-by-Investment", list(range(2020, 2025)), "ecd_m", "fiscal", 1),
    ("C31", "DMA", "imf_dma25", 35, "Citizenship By Investment, fiscal year (U.S. million dollars)", list(range(2020, 2025)), "usd_m", "fiscal", 1),
    ("C32", "DMA", "imf_dma25", 36, "Citizenship-by-Investment", list(range(2020, 2025)), "pct", "fiscal", 1),
    ("C33", "DMA", "imf_dma22", 34, "Citizenship-by-Investment", list(range(2016, 2020)), "ecd_m", "fiscal", 1),
    ("C34", "DMA", "imf_dma22", 35, "Citizenship-by-Investment", list(range(2016, 2020)), "pct", "fiscal", 1),
    ("C35", "DMA", "imf_dma25", 34, "of which Citizenship By Investment", list(range(2020, 2025)), "usd_m", "bdp", 1),
    ("C36", "KNA", "imf_kna25", 4, "o/w CBI fees", list(range(2020, 2025)), "pct", "fiscal", 1),
    ("C37", "KNA", "imf_kna25", 4, "(in millions of EC$)", list(range(2020, 2025)), "gdp_ecd_m", "pib", 1),
    ("C38", "KNA", "imf_kna18", 4, "o/w CBI fees", list(range(2015, 2018)), "pct", "fiscal", 1),
    ("C39", "KNA", "imf_kna18", 4, "Nominal GDP at market prices (in millions of EC$)", list(range(2015, 2018)), "gdp_ecd_m", "pib", 1),
    ("C40", "ATG", "imf_atg25", 31, "o/w CIP revenue", list(range(2020, 2025)), "ecd_m", "fiscal", 1),
    ("C41", "ATG", "imf_atg25", 32, "o/w CIP revenue", list(range(2020, 2025)), "pct", "fiscal", 1),
    ("C43", "GRD", "imf_grd25", 33, "Government CBI revenue (Percent of GDP)", list(range(2019, 2025)), "pct", "fiscal", 1),
    ("C44", "GRD", "imf_grd25", 33, "Citizenship-by-Investment (CBI) inflows (percent of GDP)", list(range(2019, 2025)), "pct", "bdp", 1),
    ("C45", "GRD", "imf_grd25", 33, "Nominal GDP (millions of EC$)", list(range(2019, 2025)), "gdp_ecd_m", "pib", 1),
    ("C46", "LCA", "imf_lca25", 28, "o.w . Citi zen by Investm ent Program (CIP)", list(range(2020, 2025)), "pct", "fiscal", 1),
    ("C47", "LCA", "imf_lca25", 28, "Nominal GDP fiscal year (EC$ millions)", list(range(2020, 2025)), "gdp_ecd_m", "pib", 1),
    ("C48", "VUT", "imf_vut24", 32, "ECP Revenues", list(range(2020, 2025)), "pct", "bdp", 1),
    ("C49", "VUT", "imf_vut24", 32, "Nominal GDP (in millions of U.S. dollars)", list(range(2020, 2025)), "gdp_usd_m", "pib", 1),
]
NOMBRE = {"DMA": "Dominica", "KNA": "St Kitts y Nevis", "ATG": "Antigua y Barbuda", "GRD": "Granada",
          "LCA": "Santa Lucía", "VUT": "Vanuatu"}
AÑO_FISCAL = {"DMA": "jul–jun (año = inicio del ejercicio)", "LCA": "abr–mar (año = inicio del ejercicio)"}
# Último año de cada informe que el FMI rotula como estimación/preliminar (encabezados 'Est.'/'Prel.')
ULTIMO_EST = {"imf_dma25": 2024, "imf_kna25": 2024, "imf_atg25": 2024, "imf_grd25": 2024, "imf_lca25": 2024, "imf_vut24": 2024}


def recaudacion(files) -> tuple[dict, list[dict]]:
    data: dict = {}
    ledger = []
    for cid, iso, sid, pg, label, years, unit, concepto, occ in SERIES:
        f = files[sid]
        vals, cita = table_row(f, pg, label, len(years), occ)
        data[(iso, unit, concepto, sid)] = dict(zip(years, vals))
        url, _n, _e, desc, tipo_f, _h = SOURCES[sid]
        unit_txt = {"ecd_m": "millones de EC$", "usd_m": "millones de USD", "pct": "% del PBI",
                    "gdp_ecd_m": "PBI nominal, millones de EC$", "gdp_usd_m": "PBI nominal, millones de USD"}[unit]
        conc_txt = {"fiscal": "ingreso fiscal CBI", "bdp": "flujo CBI en balanza de pagos", "pib": "PBI"}[concepto]
        ledger.append(dict(
            claim_id=cid, etiqueta="DATO",
            afirmacion=f"{NOMBRE[iso]}: {conc_txt} ({unit_txt}), {years[0]}–{years[-1]}, según tabla del FMI",
            valor="; ".join(f"{y}={v:g}" for y, v in zip(years, vals)), fuente=f"{desc}, p. {pg}", tipo_fuente=tipo_f,
            url=url, archivo_local=rel(f), sha256=sha256(f), cita_textual=f"[p. {pg}] {quote(local_text(f), cita)}"))
    return data, ledger


def build_revenue(data, gdp_dm) -> list[dict]:
    def g(iso, unit, conc, sid):
        return data.get((iso, unit, conc, sid), {})
    out = []

    def add(iso, y, conc, usd, pct_imf, metodo, sid, cids):
        gdp = gdp_dm.get(iso, {}).get(str(y))
        pct_dm = round(100 * usd / (gdp * 1000), 2) if (usd is not None and gdp) else None
        out.append(dict(iso3=iso, pais=NOMBRE[iso], anio=y, concepto=conc, anio_fiscal=AÑO_FISCAL.get(iso, "calendario"),
                        recaudacion_usd_m=round(usd, 1) if usd is not None else "", pct_pib_fmi=pct_imf if pct_imf is not None else "",
                        pib_usd_bn_datamapper=gdp if gdp else "", pct_pib_datamapper=pct_dm if pct_dm is not None else "",
                        estimacion_fmi="sí" if y >= ULTIMO_EST.get(sid, 9999) else "no",
                        metodo_usd=metodo, claim_ids=cids, informe=SOURCES[sid][3]))
    # Dominica (fiscal): USD directo 2020-24; EC$/2.7 para 2016-19
    usd = g("DMA", "usd_m", "fiscal", "imf_dma25"); pct = g("DMA", "pct", "fiscal", "imf_dma25")
    for y in sorted(usd):
        add("DMA", y, "ingreso fiscal", usd[y], pct.get(y), "DATO: fila en USD del FMI", "imf_dma25", "C31; C32")
    ec = g("DMA", "ecd_m", "fiscal", "imf_dma22"); pct = g("DMA", "pct", "fiscal", "imf_dma22")
    for y in sorted(ec):
        add("DMA", y, "ingreso fiscal", ec[y] / EC_PER_USD, pct.get(y), "ESTIMACIÓN: EC$ / 2,70", "imf_dma22", "C33; C34; C42")
    bop = g("DMA", "usd_m", "bdp", "imf_dma25")
    for y in sorted(bop):
        add("DMA", y, "flujo BdP", bop[y], None, "DATO: fila en USD del FMI", "imf_dma25", "C35")
    # St Kitts: % x PBI EC$ / 2.7
    for sid, cp, cg in (("imf_kna18", "C38", "C39"), ("imf_kna25", "C36", "C37")):
        pct = g("KNA", "pct", "fiscal", sid); gdp = g("KNA", "gdp_ecd_m", "pib", sid)
        for y in sorted(pct):
            add("KNA", y, "ingreso fiscal", pct[y] / 100 * gdp[y] / EC_PER_USD, pct[y], "ESTIMACIÓN: % × PBI EC$ / 2,70",
                sid, f"{cp}; {cg}; C42")
    # Antigua: EC$/2.7
    ec = g("ATG", "ecd_m", "fiscal", "imf_atg25"); pct = g("ATG", "pct", "fiscal", "imf_atg25")
    for y in sorted(ec):
        add("ATG", y, "ingreso fiscal", ec[y] / EC_PER_USD, pct.get(y), "ESTIMACIÓN: EC$ / 2,70", "imf_atg25", "C40; C41; C42")
    # Granada: % x PBI EC$ / 2.7 (ingreso fiscal y flujo BdP)
    gdp = g("GRD", "gdp_ecd_m", "pib", "imf_grd25")
    for conc, key, cid in (("ingreso fiscal", "fiscal", "C43"), ("flujo BdP", "bdp", "C44")):
        pct = g("GRD", "pct", key, "imf_grd25")
        for y in sorted(pct):
            add("GRD", y, conc, pct[y] / 100 * gdp[y] / EC_PER_USD, pct[y], "ESTIMACIÓN: % × PBI EC$ / 2,70", "imf_grd25",
                f"{cid}; C45; C42")
    # Santa Lucía
    pct = g("LCA", "pct", "fiscal", "imf_lca25"); gdp = g("LCA", "gdp_ecd_m", "pib", "imf_lca25")
    for y in sorted(pct):
        add("LCA", y, "ingreso fiscal", pct[y] / 100 * gdp[y] / EC_PER_USD, pct[y], "ESTIMACIÓN: % × PBI EC$ (año fiscal) / 2,70",
            "imf_lca25", "C46; C47; C42")
    # Vanuatu (ECP, balanza de pagos)
    pct = g("VUT", "pct", "bdp", "imf_vut24"); gdp = g("VUT", "gdp_usd_m", "pib", "imf_vut24")
    for y in sorted(pct):
        add("VUT", y, "flujo BdP (ECP)", pct[y] / 100 * gdp[y], pct[y], "ESTIMACIÓN: % × PBI USD", "imf_vut24", "C48; C49")
    return out


# --------------------------------------------------------------------------------------------------
# 3. Casos regulatorios
# --------------------------------------------------------------------------------------------------
CASOS = [
    # (claim_id, caso, fecha, afirmación, valor, sid, citas)
    ("C50", "Vanuatu", "2022-03-03", "La UE suspendió parcialmente el acuerdo de exención de visados con Vanuatu (pasaportes emitidos desde el 25/5/2015) por sus programas de ciudadanía para inversores",
     "Decisión (UE) 2022/366", "eu_vut_2022",
     ["COUNCIL DECISION (EU) 2022/366 of 3 March 2022 on the partial suspension of the application of the Agreement between the European Union and the Republic of Vanuatu on the short-stay visa waiver",
      "The suspension of the application of the Agreement should be limited to ordinary passports issued as of 25 May 2015"]),
    ("C51", "Vanuatu", "2024-05-31", "La Comisión prorrogó la suspensión total de la exención para todos los nacionales de Vanuatu hasta el 3/2/2025 porque persistían los riesgos de su CBI (sin requisito de residencia)",
     "Reg. Delegado (UE) 2024/2059", "eu_vut_2024",
     ["It shall apply from 4 August 2024 to 3 February 2025.",
      "The investor citizenship schemes operated by Vanuatu still do not contain any requirement of effective residence or physical presence in Vanuatu for the applicants."]),
    ("C52", "Vanuatu", "2024-12-19", "Vanuatu pasó del Anexo II al Anexo I (visa obligatoria para el espacio Schengen) por el Reg. (UE) 2025/11, publicado el 14/1/2025 y vigente 20 días después",
     "Reg. (UE) 2025/11", "eu_vut_2025",
     ["REGULATION (EU) 2025/11 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 19 December 2024 amending Regulation (EU) 2018/1806 as regards Vanuatu",
      "This Regulation shall enter into force on the twentieth day following that of its publication in the Official Journal of the European Union ."]),
    ("C53", "Vanuatu", "2024-12-19", "Según la UE, en 2023 la mayoría de las solicitudes al CBI de Vanuatu provenía de China (519) y Rusia (237)",
     "China 519; Rusia 237", "eu_vut_2025", ["In 2023, most applications were from nationals of China (519) and Russia (237)."]),
    ("C54", "UE — mecanismo de suspensión", "2025-11-26", "El Reg. (UE) 2025/2441 agrega como causal de suspensión de la exención de visado la operación de un programa de ciudadanía por inversión sin vínculo genuino",
     "Art. 8, causal (e)", "eu_vsm",
     ["REGULATION (EU) 2025/2441 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL of 26 November 2025 amending Regulation (EU) 2018/1806 as regards the revision of the suspension mechanism",
      "(e) the operation, by a third country listed in Annex II, of an investor citizenship scheme under which citizenship is granted to a person, in exchange for pre-determined payments or investments, without that person having any genuine link to that third country;"]),
    ("C55", "UE — mecanismo de suspensión", "2025-12-10", "El Reg. (UE) 2025/2441 cita el lavado de dinero y la corrupción como riesgos de seguridad de los programas CBI",
     "Considerando 7", "eu_vsm",
     ["poses several serious security risks for Union citizens, such as those stemming from money laundering and corruption"]),
    ("C56", "Malta (TJUE C-181/23)", "2025-04-29", "El TJUE (Gran Sala) declaró que Malta incumplió el art. 20 TFUE y el art. 4.3 TUE con su programa de ciudadanía por inversión, por constituir una comercialización de la ciudadanía de la Unión",
     "Incumplimiento declarado", "cjeu_c181",
     ["SENTENCIA DEL TRIBUNAL DE JUSTICIA (Gran Sala) de 29 de abril de 2025",
      "que establece un procedimiento transaccional de naturalización a cambio de pagos o de inversiones predeterminados y que se asemeja, por tanto, a una comercialización de la concesión de la nacionalidad de un Estado miembro y, por extensión, de la del estatuto de ciudadano de la Unión, la República de Malta ha incumplido las obligaciones que le incumben en virtud del artículo 20 TFUE y del artículo 4 TUE, apartado 3.",
      "2) Condenar en costas a la República de Malta."]),
    ("C57", "EE.UU. — Antigua y Dominica", "2025-12-16", "La proclamación presidencial de EE.UU. suspendió la entrada como inmigrantes y con visas B, F, M y J de nacionales de Antigua y Barbuda y de Dominica, citando su CBI sin residencia",
     "Restricción parcial", "us_procl",
     ["Antigua and Barbuda has historically had CBI without residency.",
      "Dominica has historically had CBI without residency.",
      "The entry into the United States of nationals of Antigua and Barbuda as immigrants, and as nonimmigrants on B–1, B–2, B–1/B–2, F, M, and J visas, is hereby suspended."]),
    ("C58", "EE.UU. — Antigua y Dominica", "2025-12-19", "La CIU de Antigua publicó la declaración de su embajador ante EE.UU. sobre las restricciones de visado (19/12/2025)",
     "Declaración oficial", "atg_us_stmt", ["For Immediate Release 19th December 2025 Statement by Sir Ronald Sanders Ambassador of Antigua and Barbuda to the United States"]),
    ("C59", "España", "2025-01-02", "La Ley Orgánica 1/2025 dejó sin contenido los artículos 63 a 67 de la Ley 14/2013 (residencia para inversores: no solo la vía inmobiliaria), con entrada en vigor general a los tres meses de su publicación (BOE 3/1/2025)",
     "Arts. 63–67 Ley 14/2013 derogados", "esp_lo1",
     ["Se dejan sin contenido los artículos 63, 64, 65, 66 y 67.",
      "Publicado en: « BOE » núm. 3, de 3 de enero de 2025",
      "La presente ley entrará en vigor a los tres meses de su publicación en el Boletín oficial del Estado."]),
    ("C60", "Portugal", "2023-10-06", "La Lei 56/2023 (Mais Habitação) dejó de admitir nuevas autorizaciones de residencia para actividad de inversión de las subalíneas I), III) y IV) (incluida la inmobiliaria)",
     "Art. 42 Lei 56/2023", "prt_l56",
     ["Não são admitidos novos pedidos de autorização de residência para atividade de investimento, concedidos ao abrigo do disposto nas subalíneas I), III) e IV) da alínea d) do n.º 1 do artigo 3.º da Lei n.º 23/2007",
      "À revogação das autorizações de residência para atividade de investimento imobiliário"]),
    ("C61", "Reino Unido", "2022-02-17", "El Home Office cerró la ruta Tier 1 (Investor) por razones de seguridad",
     "Cierre 17/02/2022", "gbr_t1",
     ["Tier 1 Investor Visa route closes over security concerns",
      "Home Office takes action as route failing to deliver for the UK people and gives opportunities for corrupt elites to access the UK."]),
    ("C62", "Irlanda", "2023-02-15", "Irlanda cerró el Immigrant Investor Programme a nuevas solicitudes desde el cierre del 15/2/2023; había aprobado ~€1.252 M de inversión",
     "Cierre 15/02/2023", "irl_iip",
     ["to close the Immigrant Investor Programme (IIP) to further applications from close of business tomorrow, February 15th 2023",
      "Since its inception, the Programme has approved investment of almost €1.252bn"]),
    ("C18", "Malta", "2025-07-24", "Malta (Act XXI de 2025, sancionada el 24/7/2025) eliminó la definición de 'individual investor programme' de su ley de ciudadanía",
     "Act XXI 2025", "mlt_act21",
     ["24th July, 2025 ACT No. XXI of 2025", "the definition \"individual investor programme\" shall be deleted"]),
    ("C19", "Malta", "2025-07-24", "La nueva redacción del art. 10(9) habilita la naturalización 'por mérito' (servicios o contribuciones excepcionales) en lugar de la vía por inversión",
     "Art. 10(9) nuevo", "mlt_act21",
     ["the Minister may grant a certificate of naturalisation as a citizen of Malta by merit to an alien or stateless person"]),
]


def casos(files, texts) -> tuple[list[dict], list[dict]]:
    rows, ledger = [], []
    for cid, caso, fecha, afirm, valor, sid, needles in CASOS:
        f = files[sid]
        citas = []
        for nd in needles:
            q = quote(texts[sid], nd)
            citas.append((f"[p. {find_page(f, nd)}] " if f.suffix == ".pdf" else "") + q)
        url, _n, _e, desc, tipo_f, _h = SOURCES[sid]
        ledger.append(dict(claim_id=cid, etiqueta="DATO", afirmacion=afirm, valor=valor, fuente=desc, tipo_fuente=tipo_f,
                           url=url, archivo_local=rel(f), sha256=sha256(f), cita_textual=" | ".join(citas)))
        rows.append(dict(claim_id=cid, caso=caso, fecha=fecha, hecho=afirm, fuente=desc, url=url))
    return rows, ledger


# --------------------------------------------------------------------------------------------------
# Otras afirmaciones (FMI, texto)
# --------------------------------------------------------------------------------------------------
TEXTOS_FMI = [
    ("C20", "Los cinco países CBI del Caribe Oriental firmaron en marzo de 2024 un Memorando de Acuerdo regional con un precio mínimo de USD 200.000",
     "USD 200.000", "imf_kna25", ["the ECCU countries signed a regional Memorandum of Agreement (MoA) in March 2024,",
                                  "including setting the minimum pricing of US$200,000"]),
    ("C21", "St Kitts: el ingreso CBI cayó a 8% del PBI en 2024 desde 22% en 2023, tras endurecer la debida diligencia y subir precios",
     "22% → 8% del PBI", "imf_kna25", ["CBI revenue fell to 8 percent of GDP in 2024—from 22 percent of GDP in 2023—due to"]),
    ("C22", "FMI: la dependencia del CBI desincentivó la recaudación tributaria en St Kitts, que tiene la menor presión tributaria de la región",
     "Menor ratio impuestos/PBI de la región", "imf_kna25",
     ["this dependence has disincentivized and limited tax revenue growth in St. Kitts and Nevis through",
      "resulting in the lowest tax-to-GDP ratio in the region"]),
    ("C23", "FMI: se espera que el ingreso CBI regional caiga de 7% del PBI de la ECCU en 2024 a 4% en 2029",
     "7% → 4% del PBI (ECCU)", "imf_kna25",
     ["regional CBI revenue is expected to gradually decline from 7 percent of ECCU GDP in 2024 to 4 percent of GDP in 2029"]),
    ("C24", "St Kitts duplicó en julio de 2023 el precio de la opción en efectivo (USD 125.000 → 250.000 para un solicitante)",
     "125k → 250k", "imf_kna25", ["The cash option for a single applicant and for a family of four doubled from $125K and $170K to $250K and $350K, respectively."]),
    ("C25", "Vanuatu: el FMI señala que el ECP (CBI) es un riesgo relevante de lavado de dinero en su evaluación de riesgo ALA/CFT",
     "Riesgo ALA/CFT", "imf_vut24", ["the 2026 FATF/APG Mutual Evaluation has highlighted the ECP as an important risk to Vanuatu’s"]),
    ("C26", "Vanuatu: los ingresos del ECP fueron ~14% del PBI en 2020 y cayeron a 5,4% en 2023",
     "14% → 5,4% del PBI", "imf_vut24", ["ECP revenues were around 14 percent of GDP in 2020, but have declined to 5.4 percent of"]),
    ("C27", "Santa Lucía: el S.I. 57/2026 fija un máximo de 1.500 solicitudes CBI aprobadas por año",
     "1.500/año", "lca_si57", ["the Board may approve a maximum of one thousand and five hundred applications for citizenship by investment, annually."]),
    ("C42", "El dólar del Caribe Oriental está fijado en EC$ 2,70 por USD desde julio de 1976",
     "2,70 EC$/USD", "imf_kna25", ["pegged to the U.S. dollar at the rate of EC$2.70 per U.S. dollar since July 1976"]),
]


def textos(files, texts) -> list[dict]:
    out = []
    for cid, afirm, valor, sid, needles in TEXTOS_FMI:
        f = files[sid]
        citas = [(f"[p. {find_page(f, nd)}] " if f.suffix == ".pdf" else "") + quote(texts[sid], nd) for nd in needles]
        url, _n, _e, desc, tipo_f, _h = SOURCES[sid]
        out.append(dict(claim_id=cid, etiqueta="DATO", afirmacion=afirm, valor=valor, fuente=desc, tipo_fuente=tipo_f, url=url,
                        archivo_local=rel(f), sha256=sha256(f), cita_textual=" | ".join(citas)))
    return out


# --------------------------------------------------------------------------------------------------
# Gráficos
# --------------------------------------------------------------------------------------------------
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
BLUE, ORANGE, NEUTRAL = "#2a78d6", "#eb6834", "#a9b8cc"


def _style(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9, length=0)


def ar(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def chart_montos(rows_plot):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows_plot = sorted(rows_plot, key=lambda r: r[2])
    fig, ax = plt.subplots(figsize=(9, 6.4), facecolor="white")
    y = range(len(rows_plot))
    cols = [ORANGE if r[0] == "Argentina" else (BLUE if r[3] == "don" else NEUTRAL) for r in rows_plot]
    ax.barh(list(y), [r[2] / 1000 for r in rows_plot], color=cols, height=0.62, edgecolor="white", linewidth=2)
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{r[0]} — {r[1]}" for r in rows_plot], fontsize=9, color=INK)
    for i, r in zip(y, rows_plot):
        ax.text(r[2] / 1000 + 8, i, f"{ar(r[2] / 1000)}", va="center", fontsize=8.5, color=INK2,
                fontweight="bold" if r[0] == "Argentina" else "normal")
    ax.set_xlabel("Monto mínimo para el solicitante principal (miles de USD)", fontsize=9, color=INK2)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    _style(ax)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=ORANGE, label="Argentina (anuncio 02/10/2026)"),
                       Patch(color=BLUE, label="Donación no reembolsable"),
                       Patch(color=NEUTRAL, label="Inversión recuperable (inmueble, bono, depósito)")],
              loc="lower right", fontsize=8.5, frameon=False)
    fig.suptitle("El aporte argentino (USD 350.000) es 40–50% más caro que la donación\nmínima del Caribe y el bono (USD 800.000) el umbral más alto",
                 x=0.02, ha="left", fontsize=12.5, color=INK, fontweight="bold")
    fig.text(0.02, 0.012, "Fuente: CIU St Kitts y Nevis (SRO 20 y 43/2024), CIU Antigua y Barbuda, Granada SRO 15/2024, CIU Santa Lucía (S.I. 106/2024), "
             "Turquía (Reglamento 2010/139, mevzuat.gov.tr),\nNauru ECRCP, MECON (Argentina). Dominica, Vanuatu, Egipto y Jordania: sin fuente gubernamental accesible; "
             "Malta: programa derogado (2025). Elaboración: Colossus Lab.", fontsize=7, color=MUTED, ha="left")
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    CHARTS.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(CHARTS / f"C_montos_minimos.{ext}", dpi=150, facecolor="white")
    plt.close(fig)


def chart_recaudacion(rev):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    order = ["DMA", "KNA", "GRD", "ATG", "LCA", "VUT"]
    fig, axes = plt.subplots(2, 3, figsize=(10.5, 6.2), sharey=True, facecolor="white")
    years = list(range(2015, 2025))
    for ax, iso in zip(axes.ravel(), order):
        conc = "flujo BdP (ECP)" if iso == "VUT" else "ingreso fiscal"
        pts = {r["anio"]: r["pct_pib_datamapper"] for r in rev if r["iso3"] == iso and r["concepto"] == conc
               and r["pct_pib_datamapper"] != ""}
        est = {r["anio"] for r in rev if r["iso3"] == iso and r["concepto"] == conc and r["estimacion_fmi"] == "sí"}
        xs = [y for y in years if y in pts]
        ax.bar(xs, [pts[y] for y in xs], color=[NEUTRAL if y in est else BLUE for y in xs], width=0.72,
               edgecolor="white", linewidth=1.5)
        if xs:
            ymax = max(xs, key=lambda y: pts[y])
            ax.text(ymax, pts[ymax] + 0.8, f"{ar(pts[ymax], 1)}%", ha="center", fontsize=8.5, color=INK)
            ax.text(xs[-1], pts[xs[-1]] + 0.8, f"{ar(pts[xs[-1]], 1)}%", ha="center", fontsize=8.5, color=INK2) if xs[-1] != ymax else None
        ax.set_title(NOMBRE[iso] + (" (ECP, BdP)" if iso == "VUT" else ""), fontsize=10, color=INK, loc="left")
        ax.set_xticks([2015, 2018, 2021, 2024])
        ax.set_xlim(2014.4, 2024.6)
        ax.yaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        _style(ax)
    for ax in axes[:, 0]:
        ax.set_ylabel("% del PBI", fontsize=9, color=INK2)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=BLUE, label="Dato del FMI (convertido a USD / PBI DataMapper)"),
                        Patch(color=NEUTRAL, label="Último año: estimación del FMI")],
               loc="upper right", bbox_to_anchor=(0.99, 0.93), fontsize=8, frameon=False, ncol=2)
    fig.suptitle("Dominica y St Kitts llegaron a financiar 25–37% del PBI con CBI; tras la presión de la UE,\n"
                 "St Kitts cayó a 8% en 2024 y Vanuatu de 14% a 5%",
                 x=0.02, ha="left", fontsize=12.5, color=INK, fontweight="bold")
    fig.text(0.02, 0.012, "Fuente: FMI, Article IV (Dominica CR 22/40 y 25/130; St Kitts CR 22/351 y 25/107; Antigua CR 25/96; Granada CR 25/39; "
             "Santa Lucía CR 25/65; Vanuatu CR 24/278); PBI: FMI DataMapper (NGDPD).\nIngreso fiscal CBI (Vanuatu: ingresos ECP en balanza de pagos). "
             "Dominica y Santa Lucía: año fiscal. Granada: la donación al NTF se registraba como 'grants' hasta 2022. Elaboración: Colossus Lab.",
             fontsize=7, color=MUTED, ha="left")
    fig.tight_layout(rect=(0, 0.06, 1, 0.88))
    for ext in ("png", "svg"):
        fig.savefig(CHARTS / f"C_recaudacion_pbi.{ext}", dpi=150, facecolor="white")
    plt.close(fig)


# --------------------------------------------------------------------------------------------------
def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    files, texts = {}, {}
    for sid in SOURCES:
        files[sid] = fetch(sid)
        if sid != "imf_dm":
            texts[sid] = local_text(files[sid])
    print(f"{len(files)} fuentes en data/raw")

    # 1. Montos
    tabla, led_montos = montos(files, texts)
    # Argentina (Módulo A): verificación de las citas en la copia local
    for nd in ("realizar un aporte directo y no reembolsable al Tesoro Nacional por USD 350.000",
               "suscribir un título público de USD 800.000 creado específicamente para este Programa",
               "podrá solicitar la ciudadanía argentina por un total de USD 500.000"):
        quote(texts["anuncio"], nd)
    tabla = [dict(pais="Argentina", via="Aporte no reembolsable al Tesoro", tipo_aporte="Donación (aporte al Tesoro)",
                  monto_min_principal_usd=350000, monto_familia_tipo_usd=500000, vigencia="Anuncio 02/10/2026 (sin norma publicada, ver A17)",
                  estado="verificado (anuncio)", claim_id="A01; A05", fuente=SOURCES["anuncio"][3], url=SOURCES["anuncio"][0]),
             dict(pais="Argentina", via="Título público específico", tipo_aporte="Bono", monto_min_principal_usd=800000,
                  monto_familia_tipo_usd="", vigencia="Anuncio 02/10/2026", estado="verificado (anuncio)", claim_id="A02",
                  fuente=SOURCES["anuncio"][3], url=SOURCES["anuncio"][0])] + tabla
    PROCESSED.mkdir(parents=True, exist_ok=True)
    write_csv(PROCESSED / "C_montos_minimos.csv", tabla)

    # 2. Recaudación
    data, led_rev = recaudacion(files)
    dm = json.loads(files["imf_dm"].read_text(encoding="utf-8"))["values"]["NGDPD"]
    gdp_dm = {iso: dm[iso] for iso in NOMBRE}
    rev = build_revenue(data, gdp_dm)
    write_csv(PROCESSED / "C_recaudacion_cbi.csv", rev)
    led_dm = []
    for i, iso in enumerate(NOMBRE):
        yrs = [str(y) for y in range(2015, 2025) if str(y) in gdp_dm[iso]]
        led_dm.append(dict(claim_id=f"C{70 + i}", etiqueta="DATO",
                           afirmacion=f"{NOMBRE[iso]}: PBI nominal en USD (FMI DataMapper, NGDPD), 2015–2024",
                           valor="; ".join(f"{y}={gdp_dm[iso][y]}" for y in yrs), fuente=SOURCES["imf_dm"][3], tipo_fuente="P",
                           url=SOURCES["imf_dm"][0], archivo_local=rel(files["imf_dm"]), sha256=sha256(files["imf_dm"]),
                           cita_textual=f"serie=NGDPD; país={iso}; año=2024; unidad=miles de millones de USD; valor={gdp_dm[iso]['2024']}"))

    # 3. Casos
    casos_rows, led_casos = casos(files, texts)
    write_csv(PROCESSED / "C_casos_regulatorios.csv", casos_rows)
    led_txt = textos(files, texts)

    # 4. Posicionamiento (monto y pasaporte)
    pas = {}
    pfile = PROCESSED / "B_pasaportes_destinos.csv"
    if pfile.exists():
        with pfile.open(encoding="utf-8") as f:
            pas = {r["iso3"]: int(r["destinos_sin_visa"]) for r in csv.DictReader(f)}
    ISO = {"Argentina": "ARG", "St Kitts y Nevis": "KNA", "Antigua y Barbuda": "ATG", "Granada": "GRD", "Santa Lucía": "LCA",
           "Turquía": "TUR", "Nauru": "NRU", "Dominica": "DMA", "Vanuatu": "VUT", "Egipto": "EGY", "Jordania": "JOR", "Malta": "MLT"}
    don = {}
    for r in tabla:
        if r["monto_min_principal_usd"] != "" and ("Donación" in r["tipo_aporte"]):
            don[r["pais"]] = min(don.get(r["pais"], 10**9), int(r["monto_min_principal_usd"]))
    inv = {}
    for r in tabla:
        if r["monto_min_principal_usd"] != "" and "Donación" not in r["tipo_aporte"]:
            inv[r["pais"]] = min(inv.get(r["pais"], 10**9), int(r["monto_min_principal_usd"]))
    fam = {r["pais"]: int(r["monto_familia_tipo_usd"]) for r in tabla if r["monto_familia_tipo_usd"] != ""}
    pos = []
    for pais, iso in ISO.items():
        d = don.get(pais)
        pos.append(dict(pais=pais, iso3=iso, donacion_min_usd=d or "", inversion_min_usd=inv.get(pais, ""),
                        familia_tipo_usd=fam.get(pais, ""), destinos_sin_visa=pas.get(iso, ""),
                        ratio_aporte_AR_vs_donacion=round(350000 / d, 2) if d else "",
                        usd_por_destino_sin_visa=round(d / pas[iso]) if (d and iso in pas) else ""))
    write_csv(PROCESSED / "C_posicionamiento.csv", pos)

    # Estimaciones derivadas
    car_don = {p: v for p, v in don.items() if p in ("St Kitts y Nevis", "Antigua y Barbuda", "Granada", "Santa Lucía")}
    cmin, cmax = min(car_don.values()), max(car_don.values())
    fam_car = {p: fam[p] for p in car_don if p in fam}
    led_est = [
        dict(claim_id="C80", etiqueta="ESTIMACIÓN",
             afirmacion="El aporte argentino (USD 350.000) es entre 1,40 y 1,52 veces la donación mínima de los cuatro programas caribeños verificados",
             valor=f"{350000 / cmax:.2f}–{350000 / cmin:.2f}×", fuente="Cálculo propio", tipo_fuente="", url="", archivo_local="", sha256="",
             cita_textual=f"350.000 / [{cmin}, {cmax}]; insumos A01, C01, C04, C07, C10"),
        dict(claim_id="C81", etiqueta="ESTIMACIÓN",
             afirmacion="Para una familia tipo (principal + cónyuge + 2 menores), Argentina pide USD 500.000, el doble o más que St Kitts, Antigua, Granada o Santa Lucía (USD 230.000–250.000, que cubren hasta 4 personas)",
             valor=f"{500000 / max(fam_car.values()):.1f}–{500000 / min(fam_car.values()):.1f}×", fuente="Cálculo propio", tipo_fuente="",
             url="", archivo_local="", sha256="", cita_textual="500.000 / familia tipo; insumos A05, C01, C04, C07, C10"),
        dict(claim_id="C82", etiqueta="ESTIMACIÓN",
             afirmacion="El pasaporte argentino da acceso sin visa previa a más destinos que todos los programas del benchmark salvo Malta (148 vs 123–136 en el Caribe, 111 Turquía, 80 Vanuatu, 73 Nauru, 49 Jordania, 48 Egipto)",
             valor="; ".join(f"{iso}={pas.get(iso, 'NA')}" for iso in ISO.values()), fuente="Módulo B (Passport Index Data, R)",
             tipo_fuente="R", url="", archivo_local="data/processed/B_pasaportes_destinos.csv", sha256="",
             cita_textual="Conteo de destinos sin visa por pasaporte del Módulo B (B36); data/processed/B_pasaportes_destinos.csv"),
        dict(claim_id="C83", etiqueta="ESTIMACIÓN",
             afirmacion="Costo de la donación mínima por destino sin visa: Argentina ~USD 2.365; Caribe ~USD 1.700–1.920; Nauru ~USD 1.230 (oferta 2026)",
             valor="; ".join(f"{r['iso3']}={r['usd_por_destino_sin_visa']}" for r in pos if r["usd_por_destino_sin_visa"] != ""),
             fuente="Cálculo propio", tipo_fuente="", url="", archivo_local="", sha256="",
             cita_textual="donación mínima / destinos sin visa; insumos A01, C01, C04, C07, C10, C16, C82, B36"),
    ]
    # Picos de recaudación (ESTIMACIÓN sobre DataMapper)
    fis = [r for r in rev if r["concepto"] in ("ingreso fiscal", "flujo BdP (ECP)") and r["pct_pib_datamapper"] != ""]
    for k, iso in enumerate(NOMBRE):
        rr = [r for r in fis if r["iso3"] == iso]
        top = max(rr, key=lambda r: r["pct_pib_datamapper"])
        last = max(rr, key=lambda r: r["anio"])
        tot = sum(r["recaudacion_usd_m"] for r in rr if 2020 <= r["anio"] <= 2024)
        led_est.append(dict(
            claim_id=f"C{84 + k}", etiqueta="ESTIMACIÓN",
            afirmacion=f"{NOMBRE[iso]}: máximo de recaudación CBI {top['pct_pib_datamapper']}% del PBI ({top['anio']}); "
                       f"{last['anio']}: {last['pct_pib_datamapper']}%; acumulado 2020–2024 ≈ USD {tot:,.0f} M",
            valor=f"max={top['pct_pib_datamapper']}% ({top['anio']}); ultimo={last['pct_pib_datamapper']}%; acum2020-24={tot:.0f} M USD",
            fuente="Cálculo propio sobre FMI Article IV + DataMapper", tipo_fuente="", url="",
            archivo_local="data/processed/C_recaudacion_cbi.csv", sha256="",
            cita_textual=f"recaudación USD / NGDPD; insumos {top['claim_ids']}; C{70 + k}"))
    write_csv(PROCESSED / "C_fuentes_fallidas.csv",
              [dict(fecha="2026-10-03", fuente=a, url=b, error=c, causa=d, accion=e) for a, b, c, d, e in FAILED])

    # 5. Gráficos
    plot_rows = [("Argentina", "aporte al Tesoro", 350000, "ar"), ("Argentina", "título público", 800000, "ar")]
    for r in tabla:
        if r["pais"] != "Argentina" and r["monto_min_principal_usd"] != "":
            short = {"Sustainable Island State Contribution (SISC)": "donación SISC",
                     "Inversión inmobiliaria en desarrollo aprobado": "inmueble aprobado",
                     "National Development Fund (NDF)": "donación NDF", "Inmueble aprobado": "inmueble aprobado",
                     "National Transformation Fund (NTF)": "donación NTF",
                     "Unidad en proyecto aprobado (cuota) / proyecto aprobado": "inmueble (cuota)",
                     "National Economic Fund (NEF)": "donación NEF", "Compra de inmueble (3 años sin vender)": "inmueble",
                     "Capital fijo, depósito bancario o bonos del Estado (3 años)": "depósito / bono / capital",
                     "ECRCP — oferta por tiempo limitado": "donación (oferta 2026)", "ECRCP — monto regular": "donación (regular)"}[r["via"]]
            plot_rows.append((r["pais"], short, int(r["monto_min_principal_usd"]), "don" if "Donación" in r["tipo_aporte"] else "inv"))
    chart_montos(plot_rows)
    chart_recaudacion(rev)

    ledger = led_montos + led_txt + led_rev + led_dm + led_casos + led_est
    ledger.sort(key=lambda r: r["claim_id"])
    write_ledger(MODULO, ledger)
    print(f"{len(ledger)} afirmaciones -> docs/claims/claims_C.csv")
    for r in led_est:
        print(" ", r["claim_id"], r["valor"])


if __name__ == "__main__":
    main()
