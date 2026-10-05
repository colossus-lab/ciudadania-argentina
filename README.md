# Ciudadanía por Inversión y el "momento Argentina"

Investigación de **Colossus Lab** sobre el Programa de Ciudadanía por Inversión anunciado por el Ministerio de Economía el 02/10/2026: su base legal, su mercado potencial, cómo se compara con otros programas, qué vale el pasaporte argentino, si Argentina está "de moda" desde Qatar 2022, si es un "refugio austral" y cuánto podría recaudar.

- **Informe:** `outputs/informe.pdf` · `outputs/informe.html` · `outputs/informe.md`
- **Resumen ejecutivo:** `docs/resumen_ejecutivo.md`
- **Afirmaciones verificables:** `docs/claims_ledger.csv` (cada una con su fuente, archivo local, hash y cita literal) y `docs/auditoria.csv` (verificación automática contra las copias locales)
- **Fuentes:** `docs/fuentes.md` · **Fuentes fallidas:** `docs/fuentes_fallidas.md` · **Plan:** `docs/plan.md`

## Etiquetas
**DATO** sale directo de una fuente · **ESTIMACIÓN** es un cálculo propio con método explícito · **HIPÓTESIS** es una interpretación · **ESCENARIO** es una proyección condicional.
Prensa y buscadores (tipo S) se usan solo para fechar eventos, nunca como fuente de cifras.

## Módulos
| Módulo | Script | Documento |
|---|---|---|
| A — Marco normativo | `src/01_normativa.py` | `docs/modulos/A_normativa.md` |
| B — Mercado potencial | `src/02_mercado.py` | `docs/modulos/B_mercado.md` |
| C — Benchmark CBI | `src/03_benchmark.py` | `docs/modulos/C_benchmark.md` |
| D — Pasaporte y Visa Waiver | `src/04_pasaporte_vwp.py` | `docs/modulos/D_pasaporte_vwp.md` |
| E — Popularidad post-Qatar | `src/05_popularidad.py` | `docs/modulos/E_popularidad.md` |
| E2 — Búsquedas sobre el pasaporte | `src/05b_busquedas_pasaporte.py` | `docs/modulos/E2_busquedas_pasaporte.md` |
| F — "Refugio austral" | `src/06_refugio.py` | `docs/modulos/F_refugio.md` |
| G — Escenarios fiscales | `src/07_escenarios.py` | `docs/modulos/G_escenarios.md` |

## Reproducir
```bash
python3 -m pip install -r requirements.txt   # Python 3.11 o 3.12 (ruptures 1.1.10 no tiene wheel para 3.13+)
make all            # corre los módulos, la auditoría y genera el informe
# sin make:
python3 run_all.py
```
- Los scripts trabajan sobre las copias de `data/raw/` (`nombre_AAAA-MM-DD.ext`) y solo descargan lo que falta.
- Las descargas de más de 20 MB no están versionadas por el límite de GitHub; se re-descargan solas (lista y hashes en `docs/raw_grandes.csv`).
- `make probe` vuelve a probar la disponibilidad de todas las fuentes (`docs/probe_fuentes.csv`).
- Google Trends (E y E2) puede responder 429: los scripts reintentan una vez, espaciado, y si falla lo registran. Los CSV crudos ya descargados se reutilizan.

## Pendientes conocidos
- **Módulo A:** las sentencias "Yang" (CNE) y del Juzgado Federal de Esquel vienen de copias publicadas por *Palabras del Derecho* (con firma digital del PJN). Los buscadores oficiales (PJN, CSJN, CNE, CIJ) exigen captcha y no se eludió; tampoco se pudo saber si "Yang" llegó a la Corte.
- **Módulo B:** la SCF 2025 de la Fed no se publicó; al salir, re-correr `src/02_mercado.py`. Falta verificar la doble nacionalidad en Arabia Saudita, Sudáfrica y Turquía.
- **Módulo C:** el monto de Egipto y la carta de la Comisión Europea del 25/06/2026 siguen sin fuente primaria.
- **Módulo D:** la tasa de rechazo FY2026 y la tabla NIV FY2025 todavía no están publicadas o archivadas; `python src/04_pasaporte_vwp.py` las suma cuando aparezcan.
- **Entorno:** en Windows, WeasyPrint necesita GTK; si falta, `src/08_informe.py` imprime el PDF con Edge o Chrome headless. El archivo `.gitattributes` evita que git cambie los fines de línea de `data/` (los hashes del ledger dependen de los bytes exactos).

Contacto: Colossus Lab.
