"""Módulo G — Escenarios fiscales del Programa de Ciudadanía por Inversión.

Todo resultado de este módulo es ESCENARIO: depende de supuestos de demanda que no tienen dato observado
(el programa no recibió solicitudes al 03/10/2026). Los parámetros de precio salen del Módulo A (claims A01–A04);
las bases de comparación, del BCRA y la Secretaría de Finanzas.

Salidas: data/processed/G_escenarios.csv, data/processed/G_bases.csv, outputs/charts/G_escenarios.{png,svg},
docs/claims/claims_G.csv
"""
from __future__ import annotations

import csv
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import openpyxl

from common import CHARTS, PROCESSED, download, sha256, write_ledger

# --- Parámetros de precio (DATO, Módulo A) --------------------------------------------------------
APORTE_PRINCIPAL = 350_000      # A01
BONO_PRINCIPAL = 800_000        # A02
APORTE_CONYUGE_18_25 = 100_000  # A03
APORTE_MENOR = 25_000           # A04

# --- Supuestos de ESCENARIO (no son datos) ---------------------------------------------------------
SOLICITANTES = [100, 500, 1_000, 3_000]   # solicitantes principales aprobados por año
CANALES = {"Solo aporte": 0.0, "70% aporte / 30% bono": 0.3, "50% aporte / 50% bono": 0.5}
# Dependientes promedio por solicitante principal (supuesto): 0,6 cónyuges, 0,2 hijos 18–25, 0,8 menores.
DEP = {"conyuge": 0.6, "hijo_18_25": 0.2, "menor": 0.8}
APORTE_DEPENDIENTES = (DEP["conyuge"] + DEP["hijo_18_25"]) * APORTE_CONYUGE_18_25 + DEP["menor"] * APORTE_MENOR

URL_BCRA = "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias/1?desde=2016-01-01&hasta=2026-10-03&limit=3000"
URL_DEUDA = "https://www.argentina.gob.ar/sites/default/files/deuda_publica_30-06-2026_0.xlsx"


def bases() -> tuple[dict, list[dict]]:
    p_bcra = download(URL_BCRA, "G_bcra_reservas_v4", "json")
    serie = json.loads(p_bcra.read_text())["results"][0]["detalle"]
    ult = max(serie, key=lambda d: d["fecha"])

    p_deuda = download(URL_DEUDA, "G_finanzas_deuda_publica_trimestral_2026-06-30", "xlsx")
    wb = openpyxl.load_workbook(p_deuda, read_only=True, data_only=True)
    def find(sheet, pred):
        return next(r for r in wb[sheet].iter_rows(values_only=True) if any(pred(str(c).strip()) for c in r if c is not None))
    hdr46 = find("A.4.6", lambda c: c.startswith("Stock"))
    tot46 = find("A.4.6", lambda c: c == "TOTAL")
    cols46 = [str(c).strip() for c in hdr46 if c is not None]
    vals46 = [v for v in tot46 if isinstance(v, (int, float))]
    ext = dict(zip(cols46, vals46))
    tot31 = find("A.3.1", lambda c: c == "TOTAL")
    servicios_12m = [v for v in tot31 if isinstance(v, (int, float))][-1] / 1000  # miles -> millones

    b = {
        "reservas_brutas_musd": ult["valor"], "reservas_fecha": ult["fecha"],
        "venc_capital_externo_2027_musd": ext["2027"],
        "servicios_deuda_jul26_jun27_musd": servicios_12m,
    }
    rel = lambda p: p.relative_to(p.parents[2]).as_posix()
    ledger = [
        dict(claim_id="G01", etiqueta="DATO", afirmacion="Reservas internacionales brutas del BCRA (último dato)",
             valor=f"USD {ult['valor']:,.0f} M", fuente="BCRA, API Estadísticas v4.0, variable 1", tipo_fuente="P",
             url=URL_BCRA, archivo_local=rel(p_bcra), sha256=sha256(p_bcra),
             cita_textual=f"idVariable=1; fecha={ult['fecha']}; valor={ult['valor']}"),
        dict(claim_id="G02", etiqueta="DATO", afirmacion="Vencimientos de capital de la deuda bruta externa de la Administración Central en 2027",
             valor=f"USD {ext['2027']:,.0f} M", fuente="Secretaría de Finanzas, Deuda pública al 30/06/2026, hoja A.4.6", tipo_fuente="P",
             url=URL_DEUDA, archivo_local=rel(p_deuda), sha256=sha256(p_deuda),
             cita_textual=f"hoja=A.4.6; fila=TOTAL; columna=2027; valor={ext['2027']}"),
        dict(claim_id="G03", etiqueta="DATO", afirmacion="Servicios de capital e interés de la deuda bruta (todas las monedas) jul-2026 a jun-2027",
             valor=f"USD {servicios_12m:,.0f} M", fuente="Secretaría de Finanzas, Deuda pública al 30/06/2026, hoja A.3.1", tipo_fuente="P",
             url=URL_DEUDA, archivo_local=rel(p_deuda), sha256=sha256(p_deuda),
             cita_textual=f"hoja=A.3.1; fila=TOTAL; columna=Total; valor_miles={servicios_12m*1000:.1f}"),
    ]
    return b, ledger


def escenarios(b: dict) -> list[dict]:
    out = []
    for canal, share_bono in CANALES.items():
        for n in SOLICITANTES:
            aportes = n * (1 - share_bono) * APORTE_PRINCIPAL + n * APORTE_DEPENDIENTES
            bonos = n * share_bono * BONO_PRINCIPAL
            out.append(dict(
                canal=canal, solicitantes_principales=n,
                ingreso_tesoro_musd=round(aportes / 1e6, 1),
                financiamiento_bono_musd=round(bonos / 1e6, 1),
                pct_reservas=round(100 * aportes / 1e6 / b["reservas_brutas_musd"], 2),
                pct_venc_capital_externo_2027=round(100 * aportes / 1e6 / b["venc_capital_externo_2027_musd"], 2),
                pct_servicios_12m=round(100 * aportes / 1e6 / b["servicios_deuda_jul26_jun27_musd"], 2),
            ))
    return out


def ar(x: float, dec: int = 0) -> str:
    """Formato numérico argentino: punto de miles, coma decimal."""
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


CARIBE_MUSD_ANIO = 492  # C90: ingreso fiscal CBI de los 5 programas caribeños, promedio 2020–2024 (ESTIMACIÓN del Módulo C)


def chart(rows: list[dict], b: dict) -> None:
    base = [r for r in rows if r["canal"] == "70% aporte / 30% bono"]
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    fig.patch.set_facecolor("white")
    xs = [ar(r["solicitantes_principales"]) for r in base]
    ys = [r["ingreso_tesoro_musd"] for r in base]
    bars = ax.bar(xs, ys, color="#2a78d6", width=0.55, zorder=2)
    for rect, r in zip(bars, base):
        ax.annotate(f"USD {ar(r['ingreso_tesoro_musd'])} M\n{ar(r['pct_venc_capital_externo_2027'], 1)}% de venc. ext. 2027",
                    (rect.get_x() + rect.get_width() / 2, rect.get_height()), xytext=(0, 4),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8, color="#0b0b0b")
    ax.axhline(CARIBE_MUSD_ANIO, color="#eb6834", lw=1.4, ls="--", zorder=3)
    ax.text(-0.4, CARIBE_MUSD_ANIO + 18, f"5 programas del Caribe juntos: ≈ USD {CARIBE_MUSD_ANIO} M/año (2020–24)",
            fontsize=7.5, color="#0b0b0b", ha="left")
    ax.set_ylim(0, max(ys) * 1.35)
    ax.set_xlabel("Solicitantes principales aprobados por año (supuesto)", fontsize=9, color="#52514e")
    ax.set_ylabel("Ingreso al Tesoro por aportes (USD M)", fontsize=9, color="#52514e")
    ax.set_title("ESCENARIO: aun con 3.000 solicitantes por año, los aportes\ncubren una fracción chica de los vencimientos externos de 2027",
                 fontsize=11, loc="left", color="#0b0b0b")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#c3c2b7"); ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors="#52514e", labelsize=8)
    ax.yaxis.grid(True, color="#e8e7e2", linewidth=0.8, zorder=0)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: ar(v)))
    fig.text(0.01, 0.01,
             f"Supuestos: 70% aporte USD 350.000 / 30% bono USD 800.000 (el bono es financiamiento, no ingreso);\n"
             f"dependientes promedio por solicitante: 0,6 cónyuge, 0,2 hijo de 18–25, 0,8 menor.\n"
             f"Fuente: MECON (anuncio 02/10/2026); Secretaría de Finanzas (deuda al 30/06/2026; venc. de capital externo 2027: "
             f"USD {ar(b['venc_capital_externo_2027_musd'])} M). Elaboración: Colossus Lab.",
             fontsize=6.5, color="#52514e", ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    CHARTS.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(CHARTS / f"G_escenarios.{ext}", facecolor="white")
    plt.close(fig)


def main() -> None:
    b, ledger = bases()
    rows = escenarios(b)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    with (PROCESSED / "G_escenarios.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    with (PROCESSED / "G_bases.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["variable", "valor"]); w.writerows(b.items())

    top = next(r for r in rows if r["canal"] == "Solo aporte" and r["solicitantes_principales"] == 3000)
    base1000 = next(r for r in rows if r["canal"] == "70% aporte / 30% bono" and r["solicitantes_principales"] == 1000)
    ledger += [
        dict(claim_id="G04", etiqueta="ESCENARIO",
             afirmacion="Con 1.000 solicitantes/año (70% aporte, 30% bono) los aportes suman", valor=f"USD {base1000['ingreso_tesoro_musd']:,.0f} M "
             f"({base1000['pct_venc_capital_externo_2027']}% de venc. capital externo 2027; {base1000['pct_reservas']}% de reservas)",
             fuente="Cálculo propio", tipo_fuente="", url="", archivo_local="data/processed/G_escenarios.csv", sha256="",
             cita_textual="ingreso = N·(1−b)·350k + N·(0,8·100k + 0,8·25k); N=1000, b=0,3; insumos A01–A04, G01, G02"),
        dict(claim_id="G05", etiqueta="ESCENARIO",
             afirmacion="Techo del rango: 3.000 solicitantes/año, todos por aporte", valor=f"USD {top['ingreso_tesoro_musd']:,.0f} M "
             f"({top['pct_venc_capital_externo_2027']}% de venc. capital externo 2027)",
             fuente="Cálculo propio", tipo_fuente="", url="", archivo_local="data/processed/G_escenarios.csv", sha256="",
             cita_textual="ingreso = 3000·350k + 3000·100k; insumos A01–A04, G02"),
    ]
    eq = round(CARIBE_MUSD_ANIO * 1e6 / (0.7 * APORTE_PRINCIPAL + APORTE_DEPENDIENTES))
    ledger.append(dict(claim_id="G06", etiqueta="ESCENARIO",
                       afirmacion="Solicitantes argentinos/año (mezcla 70/30) necesarios para igualar lo que recaudan juntos los 5 programas del Caribe",
                       valor=f"≈ {eq:,}".replace(",", "."), fuente="Cálculo propio", tipo_fuente="", url="",
                       archivo_local="data/processed/G_escenarios.csv", sha256="",
                       cita_textual="N = 492 M / (0,7·350k + 100k); insumos C90, A01, A03, A04"))
    write_ledger("G", ledger)
    chart(rows, b)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
