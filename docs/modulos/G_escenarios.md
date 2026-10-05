# Módulo G — Escenarios fiscales

**Resumen (5 líneas)**
1. **ESCENARIO:** con 1.000 solicitantes principales por año (70% aporte / 30% bono), los aportes al Tesoro suman ≈ USD 345 M/año. Eso es el 2,9% de los vencimientos de capital de deuda externa de 2027 y el 0,75% de las reservas brutas (G04).
2. **ESCENARIO:** el techo del rango analizado (3.000 solicitantes por año, todos por aporte) daría USD 1.350 M al año, el 11% de los vencimientos de capital externo de 2027 (G05). Como referencia, los cinco programas del Caribe juntos recaudaron unos USD 492 M al año en 2020–2024 (C90). Igualar esa cifra exigiría unos 1.430 solicitantes argentinos por año (G06). El escenario de 3.000 equivale a más del doble de todo el Caribe. Con los Article IV 2026 del FMI, el Caribe recaudó ≈ USD 419 M en 2025 (C77) y promedia ≈ USD 543 M por año en 2021–2025 con la serie revisada (C78); la referencia de 2020–2024 queda en el medio de ese rango.
3. **DATO:** reservas brutas del BCRA de USD 46.092 M al 30/09/2026 (G01); vencimientos de capital de la deuda externa de la Administración Central en 2027: USD 12.125 M (G02). Servicios totales de la deuda (todas las monedas) entre jul-2026 y jun-2027: USD 147.930 M (G03).
4. **HIPÓTESIS:** el bono de USD 800.000 no es ingreso, es financiamiento. Su valor fiscal neto depende de la tasa y el plazo, que no se publicaron. Solo los aportes (y los de los dependientes) son recursos no reembolsables.
5. **HIPÓTESIS:** el programa puede ser relevante como señal o como fuente de divisas marginal, pero no cambia por sí solo la ecuación de deuda. Además, su flujo está expuesto al riesgo judicial del DNU 366/2025 (Módulo A).

## Supuestos (todos de ESCENARIO, editables en `src/07_escenarios.py`)
- Solicitantes principales aprobados por año: 100 / 500 / 1.000 / 3.000.
- Canal: 100% aporte; 70/30; 50/50 entre aporte (USD 350.000) y bono (USD 800.000).
- Dependientes promedio por solicitante: 0,6 cónyuges, 0,2 hijos de 18 a 25 y 0,8 menores, lo que da USD 100.000 de aportes de dependientes por solicitante. Se asume que los dependientes aportan en efectivo aunque el principal elija el bono: el anuncio dice que deben realizar "los aportes previstos para cada categoría".
- No se incluyen tasas administrativas ni de debida diligencia (no fueron anunciadas).

## Tabla completa
`data/processed/G_escenarios.csv` (ingreso al Tesoro, financiamiento vía bono y % sobre cada base).

## Fuentes
| Fuente | Tipo | URL |
|---|---|---|
| BCRA, API Estadísticas v4.0, variable 1 (reservas internacionales) | P | https://api.bcra.gob.ar/estadisticas/v4.0/monetarias/1 |
| Secretaría de Finanzas, Deuda pública al 30/06/2026 (hojas A.3.1 y A.4.6) | P | https://www.argentina.gob.ar/sites/default/files/deuda_publica_30-06-2026_0.xlsx |

## Fuentes fallidas
| Fecha | Fuente | Error | Acción |
|---|---|---|---|
| 2026-10-03 | api.bcra.gob.ar v3.0 | 410 Gone | Se usó la v4.0 |

## Limitaciones
- No hay ningún dato de demanda: el programa no estaba operativo. Los escenarios no son pronósticos.
- Los servicios totales de la deuda (G03) incluyen deuda en pesos convertida a USD. Para medir presión cambiaria, la base relevante es G02.
