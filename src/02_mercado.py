"""Módulo B — Mercado potencial del Programa de Ciudadanía por Inversión.

Preguntas:
  1. Hogares de EE.UU. por umbral de patrimonio neto (Fed SCF 2022, summary extract, pesos muestrales).
  2. Cola superior de EE.UU.: top 0,1 % y top 1 % (Fed Distributional Financial Accounts).
  3. Millonarios por país (UBS Global Wealth Report 2026; Altrata WUWR 2026 como contraste).
  4. Índice heurístico del comprador no estadounidense: millonarios × brecha de destinos sin visa × visa Schengen.
  5. Gráficos.

Salidas:
  data/processed/B_scf_umbrales.csv, B_scf_capacidad_pago.csv, B_dfa_top.csv, B_ubs_millonarios.csv,
  B_pasaportes_destinos.csv, B_indice_mercados.csv
  outputs/charts/B_*.{png,svg}
  docs/claims/claims_B.csv (vía write_ledger)

Todo corre desde las copias de data/raw (descarga solo si faltan).
"""
from __future__ import annotations

import io
import math
import re
import zipfile

import numpy as np
import pandas as pd

from common import (CHARTS, PROCESSED, RAW, download, html_to_text, local_text, norm_ws, quote, sha256,
                    write_ledger)

MODULO = "B"
APORTE = 350_000          # A01 (Módulo A): aporte del solicitante principal
APORTE_FAMILIA = 500_000  # A05 (Módulo A): familia tipo
EU_HEADERS = {"Accept": "application/xhtml+xml", "Accept-Language": "eng"}
UBS_PDF = ("https://www.ubs.com/global/en/wealthmanagement/insights/global-wealth-report/_jcr_content/root/contentarea/"
           "mainpar/gridcontrol_copy/col_1/inner/col_2/actionbutton.1527090767.file/"
           "PS9jb250ZW50L2RhbS9hc3NldHMvd20vc3RhdGljL25vaW5kZXgvZ3dyLTIwMjYtZGlnaXRhbC5wZGY=/gwr-2026-digital.pdf")
PI_BASE = "https://raw.githubusercontent.com/imorte/passport-index-data/main/"

SOURCES = {
    # id: (url, nombre local, ext, descripción, tipo, kwargs de descarga)
    "scf_index": ("https://www.federalreserve.gov/econres/scfindex.htm", "B_scf_index", "htm",
                  "Federal Reserve, Survey of Consumer Finances (página índice)", "P", {}),
    "scf2022": ("https://www.federalreserve.gov/econres/files/scfp2022s.zip", "B_scf_scfp2022s", "zip",
                "Federal Reserve, SCF 2022 summary extract (Stata, rscfp2022.dta)", "P", {}),
    "dfa": ("https://www.federalreserve.gov/releases/z1/dataviz/download/zips/dfa.zip", "B_fed_dfa", "zip",
            "Federal Reserve, Distributional Financial Accounts (dfa.zip, archivos del 15/09/2026)", "P", {}),
    "ubs": (UBS_PDF, "B_ubs_gwr2026", "pdf", "UBS, Global Wealth Report 2026 (PDF)", "R", {}),
    "altrata": ("https://altrata.com/wp-content/uploads/2026/06/Altrata_World-Ultra-Wealth-Report-2026_FINAL.pdf",
                "B_altrata_wuwr2026", "pdf", "Altrata, World Ultra Wealth Report 2026 (PDF de descarga directa, sin registro)",
                "R", {}),
    "kf": ("https://www.knightfrank.com/wealthreport", "B_knightfrank_wealthreport_page", "html",
           "Knight Frank, página de The Wealth Report 2026 (solo para documentar el formulario de registro)", "R", {}),
    "henley_terms": ("https://www.henleyglobal.com/terms-of-use", "B_henley_terms_of_use", "html",
                     "Henley & Partners, Terms of Use", "R", {}),
    "henley_disc": ("https://www.henleyglobal.com/disclaimer", "B_henley_disclaimer", "html",
                    "Henley & Partners, Disclaimer", "R", {}),
    "pi_tidy": (PI_BASE + "passport-index-tidy-iso3.csv", "B_passportindex_tidy_iso3", "csv",
                "Passport Index Data (imorte/passport-index-data, MIT, actualizado 17/02/2026; datos de passportindex.org)",
                "R", {}),
    "pi_readme": (PI_BASE + "README.md", "B_passportindex_readme", "md",
                  "Passport Index Data, README (definiciones y licencia)", "R", {}),
    "pi_license": (PI_BASE + "LICENSE", "B_passportindex_license", "txt", "Passport Index Data, LICENSE (MIT)", "R", {}),
    "eurlex_all": ("https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32018R1806", "B_eurlex_2018_1806_all", "html",
                   "EUR-Lex, ficha del Reglamento (UE) 2018/1806 (versiones consolidadas)", "P", {}),
    "eurlex_cons": ("https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02018R1806-20251230",
                    "B_eurlex_2018_1806_consol_20251230", "html",
                    "EUR-Lex, Reglamento (UE) 2018/1806, versión consolidada al 30/12/2025", "P", {}),
    "eu_vanuatu": ("https://publications.europa.eu/resource/celex/32025R0011", "B_eu_reg2025_11_vanuatu", "html",
                   "Reglamento (UE) 2025/11 (Vanuatu pasa al Anexo I), vía Oficina de Publicaciones (Cellar)", "P",
                   {"headers": EU_HEADERS}),
}

# UBS GWR 2026, p. 22 "The UBS Millionaire Index": nombre UBS -> (ISO3, nombre en el Reglamento 2018/1806 si es tercer país)
UBS_MARKETS = {
    "United States": ("USA", "United States"), "Mainland China": ("CHN", "China"), "Japan": ("JPN", "Japan"),
    "Germany": ("DEU", None), "United Kingdom": ("GBR", "United Kingdom"), "France": ("FRA", None),
    "Australia": ("AUS", "Australia"), "South Korea": ("KOR", "South Korea"), "Netherlands": ("NLD", None),
    "Italy": ("ITA", None), "Spain": ("ESP", None), "Switzerland": ("CHE", None), "India": ("IND", "India"),
    "Taiwan": ("TWN", "Taiwan"), "Hong Kong SAR": ("HKG", "Hong Kong SAR"), "Belgium": ("BEL", None),
    "Sweden": ("SWE", None), "Russia": ("RUS", "Russia"), "Brazil": ("BRA", "Brazil"),
    "Saudi Arabia": ("SAU", "Saudi Arabia"), "Mexico": ("MEX", "Mexico"), "Singapore": ("SGP", "Singapore"),
    "Israel": ("ISR", "Israel"), "Ireland": ("IRL", None), "United Arab Emirates": ("ARE", "United Arab Emirates"),
    "Portugal": ("PRT", None), "Poland": ("POL", None), "South Africa": ("ZAF", "South Africa"),
    "Türkiye": ("TUR", "Turkey"), "Luxembourg": ("LUX", None), "Greece": ("GRC", None), "Qatar": ("QAT", "Qatar"),
    "Hungary": ("HUN", None), "Cyprus": ("CYP", None),
}
NOMBRES_ES = {
    "USA": "EE.UU.", "CHN": "China (cont.)", "JPN": "Japón", "DEU": "Alemania", "GBR": "Reino Unido", "FRA": "Francia",
    "AUS": "Australia", "KOR": "Corea del Sur", "NLD": "Países Bajos", "ITA": "Italia", "ESP": "España", "CHE": "Suiza",
    "IND": "India", "TWN": "Taiwán", "HKG": "Hong Kong", "BEL": "Bélgica", "SWE": "Suecia", "RUS": "Rusia",
    "BRA": "Brasil", "SAU": "Arabia Saudita", "MEX": "México", "SGP": "Singapur", "ISR": "Israel", "IRL": "Irlanda",
    "ARE": "Emiratos Árabes", "PRT": "Portugal", "POL": "Polonia", "ZAF": "Sudáfrica", "TUR": "Turquía",
    "LUX": "Luxemburgo", "GRC": "Grecia", "QAT": "Qatar", "HUN": "Hungría", "CYP": "Chipre",
}
# UBS GWR 2026, p. 32: adultos con patrimonio de USD 5–100 M (15 mercados)
UBS_5_100M = {"United States": "4,122,000", "Mainland China": "516,000", "Germany": "244,000", "France": "182,000",
              "United Kingdom": "172,000", "Japan": "164,000", "Australia": "121,000", "Switzerland": "114,000",
              "Italy": "95,000", "Spain": "83,000", "Hong Kong SAR": "69,000", "Brazil": "43,000",
              "Mexico": "29,000", "Singapore": "27,000", "United Arab Emirates": "21,000"}

SIN_VISA = {"visa free", "visa on arrival", "eta"}  # + cualquier número de días (estadía sin visa)


# ------------------------------------------------------------------------------------------------- utilidades
def fetch(sid: str):
    url, name, ext, _d, _t, kw = SOURCES[sid]
    p = download(url, name, ext, **kw)
    if p.stat().st_size == 0:  # EUR-Lex devuelve 202 vacío cuando activa su desafío anti-bots (AWS WAF)
        p.unlink()
        raise RuntimeError(f"{sid}: respuesta vacía (desafío anti-bots); reintentar más tarde")
    return p


def rel(p) -> str:
    return str(p.relative_to(RAW.parents[1]))


def fmt(x: float, nd: int = 0) -> str:
    s = f"{x:,.{nd}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def wquantile(x: np.ndarray, w: np.ndarray, q: float) -> float:
    o = np.argsort(x)
    c = np.cumsum(w[o]) / w.sum()
    return float(x[o][np.searchsorted(c, q)])


# ------------------------------------------------------------------------------------------------- 1. SCF
def scf(files):
    z = zipfile.ZipFile(files["scf2022"])
    d = pd.read_stata(io.BytesIO(z.read("rscfp2022.dta")), columns=["yy1", "y1", "wgt", "networth", "fin"])
    d["implicate"] = d["y1"] % 10
    # El extract trae 5 réplicas (implicates) por hogar. La suma de wgt por réplica es 26,26 M y la suma total
    # 131,3 M (= hogares de EE.UU.): el peso ya viene dividido por 5. Método: por réplica se usa wgt×5 (cada réplica
    # representa a toda la población), se estima, y se promedian las 5 estimaciones (reglas de Rubin para el punto).
    # Equivale a sumar wgt sobre las 22.975 filas. Se reporta además el rango entre réplicas.
    tot_by_imp = d.groupby("implicate")["wgt"].sum() * 5
    rows = []
    for thr in (1e6, 5e6, 10e6, 30e6):
        est = []
        for _i, g in d.groupby("implicate"):
            m = g["networth"] > thr
            n = (g.loc[m, "wgt"] * 5).sum()
            est.append(dict(n=n, share=n / (g["wgt"] * 5).sum(),
                            med=wquantile(g.loc[m, "networth"].to_numpy(), g.loc[m, "wgt"].to_numpy(), 0.5),
                            obs=int(m.sum())))
        e = pd.DataFrame(est)
        med = e["med"].mean()
        rows.append(dict(umbral_usd=int(thr), hogares=e["n"].mean(), hogares_min_replica=e["n"].min(),
                         hogares_max_replica=e["n"].max(), participacion_pct=100 * e["share"].mean(),
                         obs_por_replica=round(e["obs"].mean(), 1), mediana_patrimonio_usd=med,
                         aporte_350k_sobre_umbral_pct=100 * APORTE / thr,
                         aporte_350k_sobre_mediana_pct=100 * APORTE / med,
                         aporte_500k_sobre_umbral_pct=100 * APORTE_FAMILIA / thr,
                         aporte_500k_sobre_mediana_pct=100 * APORTE_FAMILIA / med))
    umb = pd.DataFrame(rows)
    umb.to_csv(PROCESSED / "B_scf_umbrales.csv", index=False, float_format="%.4f")

    # "Sin esfuerzo" (HIPÓTESIS de definición): el aporte no supera el 10 %, 5 % o 1 % del patrimonio neto;
    # variante de liquidez: aporte <= 10 % de los activos financieros (fin).
    cap = []
    for monto in (APORTE, APORTE_FAMILIA):
        for var, ratio in (("networth", 0.10), ("networth", 0.05), ("networth", 0.01), ("fin", 0.10)):
            thr = monto / ratio
            n = np.mean([(g.loc[g[var] >= thr, "wgt"] * 5).sum() for _i, g in d.groupby("implicate")])
            cap.append(dict(aporte_usd=monto, variable=var, aporte_max_pct=100 * ratio, umbral_usd=thr, hogares=n,
                            participacion_pct=100 * n / tot_by_imp.mean()))
    cap = pd.DataFrame(cap)
    cap.to_csv(PROCESSED / "B_scf_capacidad_pago.csv", index=False, float_format="%.4f")
    return umb, cap, tot_by_imp.mean()


# ------------------------------------------------------------------------------------------------- 2. DFA
def dfa(files):
    z = zipfile.ZipFile(files["dfa"])
    lv = pd.read_csv(z.open("dfa-networth-levels-detail.csv"))
    sh = pd.read_csv(z.open("dfa-networth-shares.csv"))
    keep = ["TopPt1", "RemainingTop1"]
    lv = lv[lv["Category"].isin(keep)][["Date", "Category", "Net worth", "Household count", "Minimum Wealth Cutoff"]]
    sh = sh[sh["Category"].isin(keep)][["Date", "Category", "Net worth"]].rename(columns={"Net worth": "share_pct"})
    m = lv.merge(sh, on=["Date", "Category"])
    w = m.pivot(index="Date", columns="Category")
    out = pd.DataFrame({
        "trimestre": w.index,
        "top01_patrimonio_musd": w[("Net worth", "TopPt1")].values,
        "top01_hogares": w[("Household count", "TopPt1")].values,
        "top01_corte_usd": w[("Minimum Wealth Cutoff", "TopPt1")].values,
        "top01_participacion_pct": w[("share_pct", "TopPt1")].values,
        "resto_top1_patrimonio_musd": w[("Net worth", "RemainingTop1")].values,
        "resto_top1_hogares": w[("Household count", "RemainingTop1")].values,
        "top1_corte_usd": w[("Minimum Wealth Cutoff", "RemainingTop1")].values,
        "resto_top1_participacion_pct": w[("share_pct", "RemainingTop1")].values,
    })
    out["top1_patrimonio_musd"] = out["top01_patrimonio_musd"] + out["resto_top1_patrimonio_musd"]
    out["top1_hogares"] = out["top01_hogares"] + out["resto_top1_hogares"]
    out["top1_participacion_pct"] = out["top01_participacion_pct"] + out["resto_top1_participacion_pct"]
    out["top01_promedio_usd"] = out["top01_patrimonio_musd"] * 1e6 / out["top01_hogares"]
    out["resto_top1_promedio_usd"] = out["resto_top1_patrimonio_musd"] * 1e6 / out["resto_top1_hogares"]
    out["_ord"] = out["trimestre"].str.replace(":Q", ".").astype(float)
    out = out.sort_values("_ord").drop(columns="_ord").reset_index(drop=True)
    out.to_csv(PROCESSED / "B_dfa_top.csv", index=False, float_format="%.4f")
    return out


# ------------------------------------------------------------------------------------------------- 3. UBS
def ubs(files, texts):
    import pdfplumber
    with pdfplumber.open(files["ubs"]) as pdf:
        pg = pdf.pages[21]  # p. 22 impresa: "The UBS Millionaire Index"
        cols = [pg.crop((300, 140, 560, 365)).extract_text(), pg.crop((560, 140, pg.width, 365)).extract_text()]
    rows = []
    for col in cols:
        for line in col.splitlines():
            mm = re.match(r"^(.+?) ([\d,]+)$", line.strip())
            if mm and mm.group(1) in UBS_MARKETS:
                name, val = mm.group(1), mm.group(2)
                quote(texts["ubs"], f"{name} {val}")  # verificación contra el texto completo del PDF
                rows.append(dict(mercado_ubs=name, iso3=UBS_MARKETS[name][0], nombre=NOMBRES_ES[UBS_MARKETS[name][0]],
                                 millonarios_miles=int(val.replace(",", "")), cita=f"{name} {val}"))
    df = pd.DataFrame(rows)
    assert len(df) == len(UBS_MARKETS), f"UBS: se esperaban {len(UBS_MARKETS)} mercados, se leyeron {len(df)}"
    df["adultos_5_100M"] = df["mercado_ubs"].map(lambda n: int(UBS_5_100M[n].replace(",", "")) if n in UBS_5_100M else np.nan)
    for n, v in UBS_5_100M.items():
        quote(texts["ubs"], f"{n} {v}")
    df.to_csv(PROCESSED / "B_ubs_millonarios.csv", index=False)
    return df


# ------------------------------------------------------------------------------------------------- 4. pasaportes y Schengen
def schengen(texts):
    t = texts["eurlex_cons"]
    a1 = t[t.index("ANNEX I LIST OF THIRD COUNTRIES"):t.index("ANNEX II LIST OF THIRD COUNTRIES")]
    a2 = t[t.index("ANNEX II LIST OF THIRD COUNTRIES"):t.index("ANNEX III")]

    def status(name):
        if name is None:
            return "UE/AELC (no es tercer país)", 0
        in1, in2 = re.search(rf"\b{re.escape(name)}\b", a1), re.search(rf"\b{re.escape(name)}\b", a2)
        assert bool(in1) != bool(in2), f"{name}: no se pudo ubicar en un único anexo"
        return ("Anexo I (requiere visa)", 1) if in1 else ("Anexo II (exento)", 0)
    # Los países UE/AELC no figuran en ningún anexo: se verifica.
    for n in ("Germany", "France", "Ireland", "Switzerland", "Cyprus"):
        assert not re.search(rf"\b{n}\b", a1 + a2), n
    assert re.search(r"\bArgentina\b", a2) and not re.search(r"\bArgentina\b", a1)
    return status


def pasaportes(files):
    d = pd.read_csv(files["pi_tidy"], dtype=str)
    d = d[d["Passport"] != d["Destination"]]
    d["sin_visa"] = d["Requirement"].str.fullmatch(r"\d+") | d["Requirement"].isin(SIN_VISA)
    acc = {p: set(g.loc[g["sin_visa"], "Destination"]) for p, g in d.groupby("Passport")}
    cnt = pd.DataFrame({"iso3": list(acc), "destinos_sin_visa": [len(v) for v in acc.values()]})
    arg = acc["ARG"]
    # Ganancia para un doble nacional: destinos que abre el pasaporte argentino y que el propio no abre
    # (se excluyen el propio país y la Argentina como destinos).
    cnt["ganancia_conjunto"] = [len(arg - acc[p] - {p, "ARG"}) for p in cnt["iso3"]]
    cnt["delta_vs_ARG"] = len(arg) - cnt["destinos_sin_visa"]
    cnt = cnt.sort_values("destinos_sin_visa", ascending=False)
    cnt.to_csv(PROCESSED / "B_pasaportes_destinos.csv", index=False)
    req = d.set_index(["Passport", "Destination"])["Requirement"]
    return cnt, acc, req


def indice(ubs_df, cnt, status):
    arg_n = int(cnt.loc[cnt["iso3"] == "ARG", "destinos_sin_visa"].iloc[0])
    df = ubs_df.merge(cnt, on="iso3", how="left")
    df[["schengen_estado", "necesita_visa_schengen"]] = df["mercado_ubs"].map(
        lambda n: status(UBS_MARKETS[n][1])).apply(pd.Series)
    df["delta_pos"] = df["delta_vs_ARG"].clip(lower=0)
    M = df["millonarios_miles"]
    df["I1_base"] = M * df["delta_pos"] * df["necesita_visa_schengen"]           # fórmula pedida
    df["I2_sin_schengen"] = M * df["delta_pos"]
    df["I3_log_schengen"] = np.log(M * 1000) * np.log1p(df["delta_pos"]) * df["necesita_visa_schengen"]
    df["I4_log"] = np.log(M * 1000) * np.log1p(df["delta_pos"])
    df["I5_ganancia_doble_nac"] = M * df["ganancia_conjunto"]
    df["I6_5a100M_schengen"] = (df["adultos_5_100M"] / 1000) * df["delta_pos"] * df["necesita_visa_schengen"]
    for c in [c for c in df.columns if c.startswith("I") and c[1].isdigit()]:
        mx = df[c].max()
        df[c + "_n100"] = 100 * df[c] / mx if mx and mx > 0 else 0.0
        df["rank_" + c] = df[c].rank(ascending=False, method="min").where(df[c] > 0)
    df["destinos_ARG"] = arg_n
    df = df.sort_values(["I1_base", "I2_sin_schengen"], ascending=False).reset_index(drop=True)
    df.to_csv(PROCESSED / "B_indice_mercados.csv", index=False, float_format="%.4f")
    return df, arg_n


# ------------------------------------------------------------------------------------------------- 5. gráficos
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
BLUE, ORANGE = "#2a78d6", "#eb6834"


def _style(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _save(fig, name, fuente):
    import textwrap
    fig.text(0.01, 0.012, "\n".join(textwrap.wrap(fuente, 150)), fontsize=7, color=INK2, ha="left", va="bottom")
    CHARTS.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(CHARTS / f"{MODULO}_{name}.{ext}", dpi=150, facecolor="white")


def charts(umb, idx, top):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

    # (a) hogares de EE.UU. por umbral
    fig, ax = plt.subplots(figsize=(9, 4.4), facecolor="white")
    lab = ["> USD 1 M", "> USD 5 M", "> USD 10 M", "> USD 30 M"]
    y = np.arange(len(umb))[::-1]
    v = umb["hogares"] / 1e6
    ax.barh(y, v, height=0.5, color=BLUE)
    for yi, vi, s, a in zip(y, v, umb["participacion_pct"], umb["aporte_350k_sobre_mediana_pct"]):
        ax.text(vi + 0.3, yi, f"{fmt(vi, 1)} M ({fmt(s, 1)} % de los hogares) · aporte = {fmt(a, 1)} % de la mediana del tramo",
                va="center", fontsize=8.5, color=INK)
    ax.set_yticks(y, lab, color=INK)
    ax.set_xlim(0, v.max() * 2.3)
    ax.set_xlabel("Millones de hogares (USD de 2022)", color=INK2)
    _style(ax)
    fig.suptitle("EE.UU.: 4,8 M de hogares superan USD 5 M; para ellos USD 350.000 es <4 % del patrimonio",
                 x=0.01, ha="left", fontsize=10.5, color=INK, fontweight="bold")
    ax.set_title("ESTIMACIÓN. Hogares con patrimonio neto sobre cada umbral, SCF 2022 (promedio de 5 réplicas)",
                 loc="left", fontsize=8.5, color=INK2)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.84, bottom=0.22)
    _save(fig, "hogares_umbral", "Fuente: Federal Reserve, Survey of Consumer Finances 2022 (summary extract, pesos "
          "muestrales). Excluye a la lista Forbes 400. Elaboración: Colossus Lab")
    plt.close(fig)

    # (b) ranking del índice (top 15 por la variante sin indicador Schengen; color = necesita visa Schengen)
    r = idx[idx["I2_sin_schengen"] > 0].sort_values("I2_sin_schengen", ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(9, 5.4), facecolor="white")
    y = np.arange(len(r))[::-1]
    vals = r["I2_sin_schengen_n100"]
    cols = [ORANGE if s == 1 else BLUE for s in r["necesita_visa_schengen"]]
    ax.barh(y, vals, height=0.6, color=cols)
    for yi, vi, (_, row) in zip(y, vals, r.iterrows()):
        ax.text(vi + 1, yi, f"{fmt(vi, 0 if vi >= 1 else 1)}  ({fmt(row['millonarios_miles'] / 1000, 2)} M de millonarios · "
                f"+{int(row['delta_pos'])} destinos)", va="center", fontsize=8, color=INK)
    ax.set_yticks(y, r["nombre"], color=INK)
    ax.set_xlim(0, 175)
    ax.set_xlabel("Índice (máximo = 100)", color=INK2)
    _style(ax)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=ORANGE, label="Necesita visa Schengen (Reg. 2018/1806, Anexo I)"),
                       Patch(color=BLUE, label="No necesita visa Schengen")],
              loc="lower right", frameon=False, fontsize=8, labelcolor=INK2)
    npos = int((idx["I2_sin_schengen"] > 0).sum())
    fig.suptitle(f"Solo {npos} de {len(idx)} mercados de UBS ganan destinos sin visa con el pasaporte argentino",
                 x=0.01, ha="left", fontsize=10.5, color=INK, fontweight="bold")
    ax.set_title("HIPÓTESIS / ESTIMACIÓN. Millonarios × max(0, destinos sin visa ARG − país). Heurística, no demanda medida",
                 loc="left", fontsize=8.5, color=INK2)
    fig.subplots_adjust(left=0.15, right=0.98, top=0.87, bottom=0.16)
    _save(fig, "ranking_indice", "Fuente: UBS Global Wealth Report 2026 (millonarios); Passport Index Data, feb-2026 "
          "(destinos); EUR-Lex, Reg. (UE) 2018/1806 consol. 30/12/2025. Elaboración: Colossus Lab")
    plt.close(fig)

    # (c) participación del top 0,1 % y del resto del top 1 % en el patrimonio de EE.UU.
    fig, ax = plt.subplots(figsize=(9, 4.4), facecolor="white")
    x = top["trimestre"].str.replace(":Q", ".").astype(float)
    x = x.apply(lambda q: int(q) + (round((q % 1) * 10) - 1) / 4)
    ax.plot(x, top["top01_participacion_pct"], color=BLUE, lw=2)
    ax.plot(x, top["resto_top1_participacion_pct"], color=ORANGE, lw=2)
    last = top.iloc[-1]
    ax.text(x.iloc[-1] + 0.4, last["top01_participacion_pct"], f"Top 0,1 %: {fmt(last['top01_participacion_pct'], 1)} %",
            va="center", fontsize=8.5, color=INK)
    ax.text(x.iloc[-1] + 0.4, last["resto_top1_participacion_pct"],
            f"Resto del top 1 %: {fmt(last['resto_top1_participacion_pct'], 1)} %", va="center", fontsize=8.5, color=INK)
    ax.set_xlim(x.min(), x.max() + 10)
    ax.set_ylim(0, 22)
    ax.set_ylabel("% del patrimonio neto de los hogares", color=INK2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.legend(["Top 0,1 %", "Resto del top 1 % (0,9 %)"], loc="upper left", frameon=False, fontsize=8, labelcolor=INK2)
    fig.suptitle(f"El 1 % más rico de EE.UU. concentra {fmt(last['top1_participacion_pct'], 1)} % del patrimonio "
                 f"({last['trimestre'].replace(':Q', ' T')})", x=0.01, ha="left", fontsize=10.5, color=INK, fontweight="bold")
    ax.set_title("DATO. Participación en el patrimonio neto de los hogares, trimestral", loc="left", fontsize=8.5, color=INK2)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.85, bottom=0.17)
    _save(fig, "dfa_top", "Fuente: Federal Reserve, Distributional Financial Accounts (dfa.zip). Elaboración: Colossus Lab")
    plt.close(fig)


# ------------------------------------------------------------------------------------------------- main
def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    files = {sid: fetch(sid) for sid in SOURCES}
    texts = {sid: local_text(files[sid]) for sid in ("scf_index", "ubs", "altrata", "kf", "henley_terms",
                                                     "henley_disc", "eurlex_all", "eurlex_cons", "eu_vanuatu")}
    texts["pi_readme"] = norm_ws(files["pi_readme"].read_text(encoding="utf-8"))

    # ¿Salió el SCF 2025? (la página índice enlaza los archivos del último relevamiento)
    idx_html = files["scf_index"].read_text(encoding="utf-8", errors="ignore")
    scf2025 = "scfp2025" in idx_html
    print(f"SCF 2025 publicado según scfindex.htm: {'sí' if scf2025 else 'no'} (último extract enlazado: "
          f"{'scfp2022s.zip' if 'scfp2022s.zip' in idx_html else '?'})")

    umb, cap, tot_hh = scf(files)
    top = dfa(files)
    ubs_df = ubs(files, texts)
    status = schengen(texts)
    cnt, acc, req = pasaportes(files)
    idx, arg_n = indice(ubs_df, cnt, status)
    charts(umb, idx, top)

    # ---------------------------------------------------------------- afirmaciones
    rows = []

    def add(cid, label, claim, value, sid, cita, fuente=None, tipo=None):
        url, _n, _e, desc, t, _kw = SOURCES[sid] if sid else ("", "", "", "", "", {})
        p = files.get(sid) if sid else None
        rows.append(dict(claim_id=cid, etiqueta=label, afirmacion=claim, valor=value, fuente=fuente or desc,
                         tipo_fuente=tipo or t, url=url, archivo_local=rel(p) if p else "",
                         sha256=sha256(p) if p else "", cita_textual=cita))

    q = lambda sid, s: quote(texts[sid], s)  # noqa: E731

    # SCF
    add("B01", "DATO", "El SCF 2022 es el último relevamiento publicado; el SCF 2025 aún no está en la página del SCF "
        "(consulta 03/10/2026; scfp2025s.zip devuelve 404)", "SCF 2022", "scf_index",
        q("scf_index", "The 2022 Survey of Consumer Finances (SCF) is the most recent survey conducted"))
    labels = {1e6: "B02", 5e6: "B03", 10e6: "B04", 30e6: "B05"}
    for _, r in umb.iterrows():
        cid = labels[r["umbral_usd"]]
        add(cid, "ESTIMACIÓN", f"Hogares de EE.UU. con patrimonio neto > USD {fmt(r['umbral_usd'] / 1e6, 0)} M "
            f"(USD de 2022) y su participación en el total de hogares",
            f"{fmt(r['hogares'] / 1e6, 2)} M hogares ({fmt(r['participacion_pct'], 2)} %); rango entre réplicas "
            f"{fmt(r['hogares_min_replica'] / 1e6, 2)}–{fmt(r['hogares_max_replica'] / 1e6, 2)} M", "scf2022",
            f"rscfp2022.dta: por réplica (y1 % 10) suma de wgt×5 con networth > {int(r['umbral_usd'])}; promedio de las "
            f"5 réplicas; total de hogares = suma de wgt = {fmt(tot_hh, 0)}")
    for cid, thr in (("B06", 1e6), ("B07", 5e6), ("B08", 10e6)):
        r = umb[umb["umbral_usd"] == thr].iloc[0]
        add(cid, "ESTIMACIÓN", f"Aporte como % del patrimonio en el tramo > USD {fmt(thr / 1e6, 0)} M: sobre el umbral "
            f"y sobre la mediana ponderada del tramo", f"USD 350k = {fmt(r['aporte_350k_sobre_umbral_pct'], 1)} % del umbral "
            f"y {fmt(r['aporte_350k_sobre_mediana_pct'], 1)} % de la mediana (USD {fmt(r['mediana_patrimonio_usd'] / 1e6, 2)} M); "
            f"USD 500k = {fmt(r['aporte_500k_sobre_umbral_pct'], 1)} % / {fmt(r['aporte_500k_sobre_mediana_pct'], 1)} %",
            "scf2022", f"aporte (A01=350.000; A05=500.000) / umbral y / mediana ponderada de networth del tramo "
            f"(promedio de 5 réplicas); insumos {labels[thr]}")
    c = cap.set_index(["aporte_usd", "variable", "aporte_max_pct"])["hogares"]
    add("B09", "ESTIMACIÓN", "Hogares de EE.UU. para los que el aporte es ≤ 5 % del patrimonio neto (HIPÓTESIS de "
        "'sin esfuerzo'): principal USD 350k (patrimonio ≥ USD 7 M) y familia tipo USD 500k (≥ USD 10 M)",
        f"{fmt(c[(APORTE, 'networth', 5.0)] / 1e6, 2)} M y {fmt(c[(APORTE_FAMILIA, 'networth', 5.0)] / 1e6, 2)} M hogares",
        "scf2022", "suma ponderada (wgt×5, promedio de réplicas) de hogares con networth ≥ aporte/0,05; aporte de A01 y A05")
    add("B10", "ESTIMACIÓN", "Hogares de EE.UU. para los que el aporte es ≤ 1 % del patrimonio neto: ≥ USD 35 M (350k) "
        "y ≥ USD 50 M (500k)", f"{fmt(c[(APORTE, 'networth', 1.0)] / 1e3, 0)} mil y "
        f"{fmt(c[(APORTE_FAMILIA, 'networth', 1.0)] / 1e3, 0)} mil hogares", "scf2022",
        "suma ponderada de hogares con networth ≥ aporte/0,01; aporte de A01 y A05")
    add("B11", "ESTIMACIÓN", "Variante de liquidez: hogares con activos financieros (fin) ≥ 10 × aporte",
        f"{fmt(c[(APORTE, 'fin', 10.0)] / 1e6, 2)} M (fin ≥ USD 3,5 M) y {fmt(c[(APORTE_FAMILIA, 'fin', 10.0)] / 1e6, 2)} M "
        f"(fin ≥ USD 5 M)", "scf2022", "suma ponderada de hogares con fin ≥ aporte/0,10; aporte de A01 y A05")

    # DFA
    L = top.iloc[-1]
    q_last = L["trimestre"]
    add("B12", "DATO", f"Patrimonio neto del top 0,1 % de los hogares de EE.UU. ({q_last})",
        f"USD {fmt(L['top01_patrimonio_musd'] / 1e6, 2)} billones (millones de millones)", "dfa",
        f"dfa-networth-levels-detail.csv; Date={q_last}; Category=TopPt1; Net worth={int(L['top01_patrimonio_musd'])} (MUSD)")
    add("B13", "DATO", f"Hogares en el top 0,1 % ({q_last})", fmt(L["top01_hogares"], 0), "dfa",
        f"dfa-networth-levels-detail.csv; Date={q_last}; Category=TopPt1; Household count={int(L['top01_hogares'])}")
    add("B14", "DATO", f"Patrimonio neto del resto del top 1 % (percentiles 99–99,9) ({q_last})",
        f"USD {fmt(L['resto_top1_patrimonio_musd'] / 1e6, 2)} billones; {fmt(L['resto_top1_hogares'], 0)} hogares", "dfa",
        f"dfa-networth-levels-detail.csv; Date={q_last}; Category=RemainingTop1; Net worth="
        f"{int(L['resto_top1_patrimonio_musd'])}; Household count={int(L['resto_top1_hogares'])}")
    add("B15", "ESTIMACIÓN", f"Patrimonio y participación del top 1 % ({q_last}) = TopPt1 + RemainingTop1",
        f"USD {fmt(L['top1_patrimonio_musd'] / 1e6, 2)} billones; {fmt(L['top1_participacion_pct'], 1)} % del total",
        "dfa", f"B12 + B14; participación = {L['top01_participacion_pct']} + {L['resto_top1_participacion_pct']} "
        f"(dfa-networth-shares.csv, Date={q_last})")
    add("B16", "DATO", f"Participación del top 0,1 % en el patrimonio neto ({q_last})",
        f"{fmt(L['top01_participacion_pct'], 1)} %", "dfa",
        f"dfa-networth-shares.csv; Date={q_last}; Category=TopPt1; Net worth={L['top01_participacion_pct']}")
    cut = top.dropna(subset=["top1_corte_usd"]).iloc[-1]
    add("B17", "DATO", f"Patrimonio mínimo para entrar al top 0,1 % y al top 1 % (último dato con corte: {cut['trimestre']})",
        f"USD {fmt(cut['top01_corte_usd'] / 1e6, 1)} M y USD {fmt(cut['top1_corte_usd'] / 1e6, 1)} M", "dfa",
        f"dfa-networth-levels-detail.csv; Date={cut['trimestre']}; Minimum Wealth Cutoff: TopPt1="
        f"{int(cut['top01_corte_usd'])}; RemainingTop1={int(cut['top1_corte_usd'])}")
    add("B18", "ESTIMACIÓN", f"Patrimonio promedio por hogar y peso del aporte de USD 350k ({q_last})",
        f"Top 0,1 %: USD {fmt(L['top01_promedio_usd'] / 1e6, 0)} M (aporte {fmt(100 * APORTE / L['top01_promedio_usd'], 2)} %); "
        f"resto top 1 %: USD {fmt(L['resto_top1_promedio_usd'] / 1e6, 1)} M (aporte "
        f"{fmt(100 * APORTE / L['resto_top1_promedio_usd'], 2)} %)", "dfa", "B12/B13 y B14 (patrimonio/hogares); A01/promedio")
    first = top.iloc[0]
    add("B19", "DATO", f"Participación del top 0,1 % al inicio de la serie ({first['trimestre']})",
        f"{fmt(first['top01_participacion_pct'], 1)} %", "dfa",
        f"dfa-networth-shares.csv; Date={first['trimestre']}; Category=TopPt1; Net worth={first['top01_participacion_pct']}")

    # UBS
    us = ubs_df.set_index("iso3")
    add("B20", "DATO", "Millonarios en USD (adultos) en EE.UU., fin de 2025", "23.627 mil", "ubs", q("ubs", "United States 23,627"))
    add("B21", "DATO", "Millonarios en USD en la muestra de UBS (56 mercados)", "≈ 57,5 millones", "ubs",
        q("ubs", "people out of the roughly 57.5 million millionaires in our sample"))
    add("B22", "DATO", "UBS publica el número de millonarios de solo 34 de sus 56 mercados (tabla 'The UBS Millionaire "
        "Index'); Argentina no está en la muestra de 56", f"34 mercados; 'Argentina' aparece "
        f"{texts['ubs'].count('Argentina')} veces en el PDF", "ubs", q("ubs", "Overview of the markets covered in this year’s report"))
    add("B23", "DATO", "Adultos con patrimonio de USD 5–100 M en EE.UU. (UBS)", "4.122.000", "ubs",
        q("ubs", "United States 4,122,000"))
    add("B24", "DATO", "Millonarios en USD en China continental e India (UBS)",
        f"{fmt(us.loc['CHN', 'millonarios_miles'], 0)} mil y {fmt(us.loc['IND', 'millonarios_miles'], 0)} mil", "ubs",
        q("ubs", "Mainland China 5,305") + " | " + q("ubs", "India 944"))
    # Altrata (contraste para la cola: > USD 30 M)
    add("B25", "DATO", "Individuos UHNW (patrimonio ≥ USD 30 M) en EE.UU., 2025, con patrimonio conjunto de USD 23,8 billones (Altrata)",
        "206.880", "altrata", q("altrata", "1 US 206,880 15.0%") + " | " +
        q("altrata", "This cohort of some 207,000 ultra wealthy individuals held a cumulative net worth of $23.8tn in 2025"))
    add("B26", "DATO", "Población UHNW mundial 2025 (Altrata)", "556.850", "altrata",
        q("altrata", "The global UHNW population increased by 14.4% to an all-time high of 556,850 individuals"))
    # Knight Frank: falla documentada
    add("B27", "DATO", "Knight Frank The Wealth Report 2026 exige formulario para descargar el informe: no se usa",
        "Formulario de registro", "kf", q("kf", "To download the report, please complete the form below and a download link will be provided"))
    # Henley: términos
    add("B28", "DATO", "Los términos de henleyglobal.com prohíben el acceso automatizado: no se usa la API del Henley Passport Index",
        "Prohibido", "henley_terms", q("henley_terms", "Use any robot, spider, scraper, or other automated means to access the website for any purpose"))
    add("B29", "DATO", "El aviso legal de Henley prohíbe reproducir contenido sin permiso escrito", "Prohibido", "henley_disc",
        q("henley_disc", "No part of this site may be reproduced in any form or by any means without prior written permission"))

    # Schengen
    add("B30", "DATO", "Versión consolidada vigente del Reglamento (UE) 2018/1806 usada", "30/12/2025", "eurlex_all",
        q("eurlex_all", "Current consolidated version: 30/12/2025"))
    schen = idx[idx["necesita_visa_schengen"] == 1]["nombre"].tolist()
    add("B31", "DATO", "Mercados con datos UBS cuyos nacionales necesitan visa Schengen (Anexo I)", ", ".join(schen),
        "eurlex_cons", q("eurlex_cons", "ANNEX I LIST OF THIRD COUNTRIES WHOSE NATIONALS ARE REQUIRED TO BE IN POSSESSION "
                         "OF A VISA WHEN CROSSING THE EXTERNAL BORDERS OF THE MEMBER STATES") +
        " [pertenencia de cada nombre verificada en el segmento Anexo I–Anexo II del texto consolidado]")
    add("B32", "DATO", "Argentina está en el Anexo II (exenta de visa Schengen para estadías ≤ 90 días en 180)", "Anexo II",
        "eurlex_cons", q("eurlex_cons", "Albania (6) Argentina Australia"))
    add("B33", "DATO", "Desde el Reg. (UE) 2025/2441, operar un programa de ciudadanía por inversión es causal para suspender "
        "la exención de visa de un país del Anexo II (Argentina incluida)", "Art. 8 (causal e)", "eurlex_cons",
        q("eurlex_cons", "the operation, by a third country listed in Annex II, of an investor citizenship scheme under which "
          "citizenship is granted to a person, in exchange for pre-determined payments or investments, without that person "
          "having any genuine link to that third country"))
    add("B34", "DATO", "Caso Vanuatu: la UE constató que su CBI permitía a nacionales de países con visa obtener acceso sin visa a la Unión",
        "Reg. (UE) 2025/11, cons. 3", "eu_vanuatu",
        q("eu_vanuatu", "third-country nationals who would otherwise be subject to the visa requirement are able to obtain "
          "Vanuatu citizenship in exchange for an investment, therefore obtaining visa-free access to the Union"))
    add("B35", "DATO", "Caso Vanuatu: la mayoría de los solicitantes exitosos 2022–2023 venía de países con visa; en 2023, China 519 y Rusia 237",
        "China 519; Rusia 237", "eu_vanuatu",
        q("eu_vanuatu", "The countries of origin of successful applicants in 2022 and 2023 include mostly countries whose "
          "nationals are subject to the visa requirement. In 2023, most applications were from nationals of China (519) and Russia (237)"))

    # Pasaportes
    pi_def = q("pi_readme", "Visa issued upon arrival - effectively visa-free")
    add("B36", "ESTIMACIÓN", "Destinos sin visa previa del pasaporte argentino (estadía sin visa, visa a la llegada o ETA; "
        "definición análoga a Henley)", f"{arg_n} de 198", "pi_tidy",
        f"passport-index-tidy-iso3.csv; Passport=ARG; Requirement ∈ {{número de días, 'visa free', 'visa on arrival', 'eta'}}; "
        f"n={arg_n}. Definición del README: '{pi_def}'")
    add("B37", "DATO", "El pasaporte argentino requiere visa para EE.UU. y Canadá; ETA para el Reino Unido",
        f"USA={req[('ARG', 'USA')]}; CAN={req[('ARG', 'CAN')]}; GBR={req[('ARG', 'GBR')]}", "pi_tidy",
        f"passport-index-tidy-iso3.csv; Passport=ARG; Destination=USA/CAN/GBR; Requirement="
        f"{req[('ARG', 'USA')]}/{req[('ARG', 'CAN')]}/{req[('ARG', 'GBR')]}")
    n_better = int((cnt["iso3"].ne("ARG") & (cnt["destinos_sin_visa"] >= arg_n)).sum())
    add("B38", "ESTIMACIÓN", "Pasaportes (de 199) con igual o más destinos sin visa que el argentino: para ellos la brecha es ≤ 0",
        f"{n_better} de 198", "pi_tidy", f"conteo de pasaportes con destinos_sin_visa ≥ {arg_n} (B36); data/processed/B_pasaportes_destinos.csv")
    nonpos = idx[idx["delta_pos"] == 0]
    add("B39", "ESTIMACIÓN", "Mercados con datos UBS para los que el pasaporte argentino no agrega destinos (brecha ≤ 0)",
        f"{len(nonpos)} de {len(idx)}; suman {fmt(nonpos['millonarios_miles'].sum() / 1e3, 1)} M de los "
        f"{fmt(idx['millonarios_miles'].sum() / 1e3, 1)} M de millonarios de la tabla", "pi_tidy",
        "B36 vs destinos_sin_visa de cada país (B_pasaportes_destinos.csv) cruzado con B_ubs_millonarios.csv")

    # Índice
    r1 = idx[idx["I1_base"] > 0].sort_values("I1_base", ascending=False)
    add("B40", "ESTIMACIÓN", "HIPÓTESIS de comprador no estadounidense — índice base millonarios × max(0, destinos_ARG − "
        "destinos_país) × 1{visa Schengen}: mercados con valor positivo, en orden",
        "; ".join(f"{n} ({fmt(v, 1)})" for n, v in zip(r1["nombre"], r1["I1_base_n100"])), "pi_tidy",
        "I1 = millonarios_miles(UBS, B20–B24) × delta_pos(B36) × necesita_visa_schengen(B31); normalizado a máx = 100; "
        "data/processed/B_indice_mercados.csv", fuente="Cálculo propio sobre UBS GWR 2026, Passport Index Data y Reg. (UE) 2018/1806",
        tipo="R")
    r2 = idx[idx["I2_sin_schengen"] > 0].sort_values("I2_sin_schengen", ascending=False)
    add("B41", "ESTIMACIÓN", "Variante sin indicador Schengen: mercados con valor positivo (máx. 15), en orden",
        "; ".join(f"{n} ({fmt(v, 1)})" for n, v in zip(r2["nombre"].head(15), r2["I2_sin_schengen_n100"].head(15))),
        "pi_tidy", "I2 = millonarios_miles × delta_pos; normalizado a máx = 100", fuente="Cálculo propio", tipo="R")
    r5 = idx.sort_values("I5_ganancia_doble_nac", ascending=False).head(5)
    add("B42", "ESTIMACIÓN", "Variante 'doble nacionalidad' (destinos que abre ARG y no el pasaporte propio): top 5",
        "; ".join(f"{n} (+{int(g)} destinos)" for n, g in zip(r5["nombre"], r5["ganancia_conjunto"])), "pi_tidy",
        "I5 = millonarios_miles × |destinos_ARG \\ destinos_país|", fuente="Cálculo propio", tipo="R")

    gan_us = sorted(acc["ARG"] - acc["USA"] - {"USA", "ARG"})
    add("B43", "ESTIMACIÓN", "Para un ciudadano estadounidense, destinos que abre el pasaporte argentino y no el propio "
        "(ganancia de movilidad de la doble nacionalidad)", f"{len(gan_us)}: {', '.join(gan_us)}", "pi_tidy",
        "passport-index-tidy-iso3.csv: destinos sin visa (definición B36) de ARG menos los de USA, sin USA ni ARG")

    write_ledger(MODULO, rows)

    # resumen por consola
    print(umb[["umbral_usd", "hogares", "participacion_pct", "mediana_patrimonio_usd", "aporte_350k_sobre_mediana_pct"]])
    print(cap)
    print(top.tail(1).T)
    print(idx[["nombre", "millonarios_miles", "destinos_sin_visa", "delta_vs_ARG", "ganancia_conjunto", "schengen_estado",
               "I1_base_n100", "I2_sin_schengen_n100", "I4_log_n100", "I5_ganancia_doble_nac_n100"]].to_string())
    print(f"ARG destinos sin visa: {arg_n}; pasaportes con ≥: {n_better}")
    print(f"{len(rows)} afirmaciones -> docs/claims/claims_{MODULO}.csv")


if __name__ == "__main__":
    main()
