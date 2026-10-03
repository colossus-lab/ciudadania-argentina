"""Módulo E (extensión) — Búsquedas en Google sobre el pasaporte / la ciudadanía argentina y el programa CBI.

Google Trends (vía pytrends) devuelve índices relativos 0–100 dentro de cada consulta (no volúmenes absolutos),
sobre una muestra que puede variar entre pedidos. Por eso cada consulta se guarda cruda con fecha en data/raw y
todo número derivado se rotula ESTIMACIÓN.

Consultas (cada una con pausa larga y como mucho 2 intentos, para no gatillar el bloqueo 429):
  Q1  EE.UU., 5 años, semanal: términos de pasaporte/ciudadanía argentina
  Q2  EE.UU., últimos 7 días, horario: reacción al anuncio del 02/10/2026
  Q3  Mundo, últimos 7 días, horario: idem
  Q4  Mundo, 12 meses: interés por país para "argentina citizenship" y "argentina passport"
  Q5  Mundo, 12 meses: interés por país para "ciudadania argentina" y "pasaporte argentino" (español)
  Q6  Mundo, 12 meses: interés por país para "cidadania argentina" (portugués)
  Q7  EE.UU., 5 años: "argentina citizenship" frente a programas CBI conocidos
  Q8  Mundo, 7 días: consultas relacionadas en ascenso de "argentina citizenship"

Salidas: data/raw/E2_gt_*.csv, data/processed/E2_*.csv, outputs/charts/E2_*.{png,svg}, docs/claims/claims_E2.csv
"""
from __future__ import annotations

import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from common import CHARTS, PROCESSED, RAW, TODAY, UA, raw_path, sha256, write_ledger

PAUSA = 75          # segundos entre consultas
ANUNCIO = pd.Timestamp("2026-10-02")
GT_URL = "https://trends.google.com/trends/explore"

QUERIES = {
    "Q1": dict(kind="time", kw=["argentina passport", "argentina citizenship", "argentine citizenship",
                                 "pasaporte argentino", "ciudadania argentina"], tf="today 5-y", geo="US"),
    "Q2": dict(kind="time", kw=["argentina citizenship", "argentina passport", "argentina citizenship by investment",
                                 "argentina golden passport"], tf="now 7-d", geo="US"),
    "Q3": dict(kind="time", kw=["argentina citizenship", "argentina passport", "ciudadania argentina",
                                 "pasaporte argentino"], tf="now 7-d", geo=""),
    "Q4": dict(kind="region", kw=["argentina citizenship", "argentina passport"], tf="today 12-m", geo=""),
    "Q5": dict(kind="region", kw=["ciudadania argentina", "pasaporte argentino"], tf="today 12-m", geo=""),
    "Q6": dict(kind="region", kw=["cidadania argentina"], tf="today 12-m", geo=""),
    "Q7": dict(kind="time", kw=["argentina citizenship", "portugal golden visa", "dominica citizenship",
                                 "st kitts citizenship", "turkey citizenship by investment"], tf="today 5-y", geo="US"),
    "Q8": dict(kind="related", kw=["argentina citizenship"], tf="now 7-d", geo=""),
}


def fetch(qid: str, q: dict) -> tuple[pd.DataFrame | None, str]:
    """Devuelve (DataFrame, estado). Reutiliza la copia cruda del día si existe."""
    existing = sorted(RAW.glob(f"E2_gt_{qid}_*.csv"))
    if existing:
        return pd.read_csv(existing[-1], index_col=0), "cache"
    from pytrends.request import TrendReq
    err = ""
    for intento in range(2):
        try:
            tr = TrendReq(hl="en-US", tz=0, timeout=(10, 30), requests_args={"headers": {"User-Agent": UA}})
            tr.build_payload(q["kw"], timeframe=q["tf"], geo=q["geo"])
            if q["kind"] == "time":
                df = tr.interest_over_time()
            elif q["kind"] == "region":
                df = tr.interest_by_region(resolution="COUNTRY", inc_low_vol=True, inc_geo_code=True)
            else:
                rel = tr.related_queries()[q["kw"][0]]
                parts = [d.assign(tipo=t) for t, d in rel.items() if d is not None and not d.empty]
                df = pd.concat(parts) if parts else pd.DataFrame()
            if df is None or df.empty:
                return None, "vacía (volumen insuficiente)"
            df.to_csv(raw_path(f"E2_gt_{qid}", "csv"))
            return df, "ok"
        except Exception as e:  # noqa: BLE001
            err = f"{type(e).__name__}: {str(e)[:120]}"
            time.sleep(PAUSA * 2)
    return None, f"falla tras 2 intentos ({err})"


def main() -> None:
    results, estados = {}, {}
    for i, (qid, q) in enumerate(QUERIES.items()):
        if i and not sorted(RAW.glob(f"E2_gt_{qid}_*.csv")):
            time.sleep(PAUSA)
        df, st = fetch(qid, q)
        results[qid], estados[qid] = df, st
        print(f"{qid}: {st}", flush=True)
    pd.DataFrame([dict(consulta=k, terminos=" | ".join(QUERIES[k]["kw"]), periodo=QUERIES[k]["tf"],
                       geo=QUERIES[k]["geo"] or "mundo", estado=v) for k, v in estados.items()]
                 ).to_csv(PROCESSED / "E2_consultas_estado.csv", index=False)
    analyze(results)


def _file(qid: str):
    hits = sorted(RAW.glob(f"E2_gt_{qid}_*.csv"))
    return hits[-1] if hits else None


def analyze(res: dict) -> None:
    ledger = []
    rel = lambda p: str(p.relative_to(p.parents[2]))

    def add(cid, etiqueta, afirm, valor, qid, cita):
        p = _file(qid)
        ledger.append(dict(claim_id=cid, etiqueta=etiqueta, afirmacion=afirm, valor=valor,
                           fuente=f"Google Trends vía pytrends, consulta {qid} ({QUERIES[qid]['tf']}, "
                                  f"geo={QUERIES[qid]['geo'] or 'mundo'}), descargada {TODAY}",
                           tipo_fuente="R", url=GT_URL, archivo_local=rel(p) if p else "",
                           sha256=sha256(p) if p else "", cita_textual=cita))

    # --- Q1: tendencia de 5 años en EE.UU.
    if res.get("Q1") is not None:
        d = res["Q1"].copy(); d.index = pd.to_datetime(d.index)
        d = d.drop(columns=[c for c in d.columns if c == "isPartial"])
        y = d.groupby(d.index.year).mean().round(1)
        y.to_csv(PROCESSED / "E2_us_5y_anual.csv")
        pk = d["argentina passport"].idxmax()
        add("E50", "DATO", "EE.UU., 5 años: semana de máximo interés relativo por 'argentina passport'",
            f"{pk.date()} (=100)", "Q1", f"date={pk.date()}; argentina passport={int(d.loc[pk, 'argentina passport'])}")
        for cid, term in (("E51", "argentina passport"), ("E52", "argentina citizenship")):
            first, last = y.index.min(), y.index.max()
            add(cid, "ESTIMACIÓN", f"EE.UU.: promedio anual del índice de '{term}' (primer año completo vs. 2026)",
                f"{y.loc[first + 1, term]} ({first + 1}) → {y.loc[last, term]} ({last})", "Q1",
                f"promedio por año calendario de la serie semanal '{term}' en Q1; ver data/processed/E2_us_5y_anual.csv")
        chart_5y(d)

    # --- Q2/Q3: reacción al anuncio (horario, últimos 7 días)
    for qid, geo_lbl, cid in (("Q2", "EE.UU.", "E53"), ("Q3", "mundo", "E54")):
        if res.get(qid) is None:
            continue
        d = res[qid].copy(); d.index = pd.to_datetime(d.index)
        d = d.drop(columns=[c for c in d.columns if c == "isPartial"])
        term = "argentina citizenship"
        antes = d.loc[d.index < ANUNCIO, term].mean()
        despues = d.loc[d.index >= ANUNCIO, term].mean()
        pk = d[term].idxmax()
        d.to_csv(PROCESSED / f"E2_{qid}_7dias_horario.csv")
        add(cid, "ESTIMACIÓN", f"{geo_lbl}: interés horario por '{term}' antes vs. desde el anuncio (02/10/2026, UTC)",
            f"{antes:.1f} → {despues:.1f} (máximo {pk:%d/%m %H:%M} UTC)", qid,
            f"media de la serie horaria '{term}' con fecha < 2026-10-02 vs. ≥ 2026-10-02 en {qid}")
        add(f"E{int(cid[1:]) + 10}", "DATO", f"{geo_lbl}: hora de máximo interés por '{term}' en los últimos 7 días",
            f"{pk:%Y-%m-%d %H:%M} UTC", qid, f"date={pk:%Y-%m-%d %H:%M:%S}; {term}={int(d.loc[pk, term])}")
        if qid == "Q2":
            for t in ("argentina citizenship by investment", "argentina golden passport"):
                if t in d and d[t].sum() == 0:
                    add("E55" if "investment" in t else "E56", "DATO",
                        f"EE.UU.: '{t}' no registra volumen suficiente en Google Trends en los últimos 7 días", "0 en todas las horas",
                        qid, f"suma de la columna '{t}' = 0 en {qid}")
        chart_7d(d, qid, geo_lbl)

    # --- Q4–Q6: países
    rankings = []
    for qid in ("Q4", "Q5", "Q6"):
        df = res.get(qid)
        if df is None:
            continue
        for term in QUERIES[qid]["kw"]:
            top = df[term].sort_values(ascending=False)
            top = top[top > 0].head(15)
            for pais, v in top.items():
                rankings.append(dict(consulta=qid, termino=term, pais=pais, indice=int(v)))
    if rankings:
        rk = pd.DataFrame(rankings)
        rk.to_csv(PROCESSED / "E2_paises_ranking.csv", index=False)
        for i, (term, g) in enumerate(rk.groupby("termino", sort=False)):
            top3 = ", ".join(f"{r.pais} ({r.indice})" for r in g.head(3).itertuples())
            qid = g["consulta"].iloc[0]
            first = g.iloc[0]
            add(f"E{57 + i}", "DATO", f"Mundo, 12 meses: países con mayor interés relativo por '{term}' (índice 0–100, normalizado por población de internautas)",
                top3, qid, f"geoName={first.pais}; {term}={first.indice}")
        chart_paises(rk)

    # --- Q8: consultas relacionadas
    if res.get("Q8") is not None:
        d = res["Q8"]
        d.to_csv(PROCESSED / "E2_relacionadas.csv")
        rising = d[d["tipo"] == "rising"] if "tipo" in d else d
        if not rising.empty:
            r0 = rising.iloc[0]
            add("E62", "DATO", "Mundo, 7 días: consulta relacionada en mayor ascenso con 'argentina citizenship'",
                f"{r0['query']} ({r0['value']})", "Q8", f"query={r0['query']}; value={r0['value']}")

    # --- Q7: comparación con programas CBI conocidos
    if res.get("Q7") is not None:
        d = res["Q7"].copy(); d.index = pd.to_datetime(d.index)
        d = d.drop(columns=[c for c in d.columns if c == "isPartial"])
        last52 = d.tail(52).mean().round(1)
        last52.to_csv(PROCESSED / "E2_us_vs_cbi_52sem.csv")
        add("E63", "ESTIMACIÓN", "EE.UU., últimas 52 semanas: interés medio relativo 'argentina citizenship' vs. programas CBI/golden visa",
            "; ".join(f"{k}: {v}" for k, v in last52.items()), "Q7", "media de las últimas 52 filas semanales de Q7 por término")

    write_ledger("E2", ledger)
    print(f"{len(ledger)} afirmaciones -> docs/claims/claims_E2.csv")


# --- Gráficos ---------------------------------------------------------------------------------------
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e8e7e2"


def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#c3c2b7"); ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors=INK2, labelsize=8)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8); ax.set_axisbelow(True)


def _save(fig, name, nota):
    fig.text(0.01, 0.01, f"Fuente: Google Trends ({nota}), índice relativo 0–100, descargado {TODAY}. "
             "Elaboración: Colossus Lab.", fontsize=6.5, color=INK2, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    for ext in ("png", "svg"):
        fig.savefig(CHARTS / f"E2_{name}.{ext}", facecolor="white", dpi=150)
    plt.close(fig)


def chart_5y(d: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    for i, c in enumerate(["argentina passport", "argentina citizenship"]):
        ax.plot(d.index, d[c], color=COLORS[i], lw=1.6, label=c)
    ax.axvline(ANUNCIO, color="#9a9994", lw=0.8); ax.text(ANUNCIO, ax.get_ylim()[1] * 0.95, " anuncio CBI", fontsize=7, color=INK2)
    ax.set_title("EE.UU.: búsquedas sobre el pasaporte y la ciudadanía argentina (semanal, 5 años)", loc="left", fontsize=10.5, color=INK)
    ax.legend(frameon=False, fontsize=8, loc="upper left"); _style(ax)
    _save(fig, "us_pasaporte_5y", "geo=US, today 5-y")


def chart_7d(d: pd.DataFrame, qid: str, geo_lbl: str) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    for i, c in enumerate(d.columns):
        ax.plot(d.index, d[c], color=COLORS[i % len(COLORS)], lw=1.4, label=c)
    ax.axvline(ANUNCIO, color="#9a9994", lw=0.8)
    ax.text(ANUNCIO, ax.get_ylim()[1] * 0.95, " 02/10 (día del anuncio)", fontsize=7, color=INK2)
    ax.set_title(f"{geo_lbl}: búsquedas horarias, últimos 7 días", loc="left", fontsize=10.5, color=INK)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left"); _style(ax)
    _save(fig, f"{qid}_7dias", f"geo={'US' if qid == 'Q2' else 'mundo'}, now 7-d, horas UTC")


def chart_paises(rk: pd.DataFrame) -> None:
    terms = list(dict.fromkeys(rk["termino"]))
    fig, axes = plt.subplots(1, len(terms), figsize=(3.1 * len(terms), 4.6), squeeze=False)
    for ax, t in zip(axes[0], terms):
        g = rk[rk["termino"] == t].head(10).iloc[::-1]
        ax.barh(g["pais"], g["indice"], color="#2a78d6", height=0.6)
        for y, v in enumerate(g["indice"]):
            ax.text(v + 1, y, str(v), va="center", fontsize=7, color=INK)
        ax.set_title(f"'{t}'", fontsize=8.5, loc="left", color=INK); ax.set_xlim(0, 115)
        ax.tick_params(labelsize=7, colors=INK2)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.suptitle("Mundo, 12 meses: países con mayor interés relativo de búsqueda", x=0.01, ha="left", fontsize=10.5, color=INK)
    _save(fig, "paises", "mundo, today 12-m, por país; normalizado por volumen local")


if __name__ == "__main__":
    main()
