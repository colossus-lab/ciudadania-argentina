# Módulo E (extensión) — Búsquedas en Google sobre el pasaporte y la ciudadanía argentina

Google Trends da índices **relativos** de 0 a 100 dentro de cada consulta, no volúmenes. Los índices salen de una muestra que puede variar entre pedidos, y los rankings por país están normalizados por el total de búsquedas de cada país. Por eso todo número derivado es **ESTIMACIÓN**, y la fuente es tipo **R**. Las consultas crudas están en `data/raw/E2_gt_Q*_2026-10-03.csv`.

**Resumen (5 líneas)**
1. **DATO / ESTIMACIÓN:** en EE.UU., el interés por "argentina passport" fue plano entre 2021 y mediados de 2025, con un promedio anual de 2 a 4. En 2026 promedia 32,5, y "argentina citizenship" pasó de 0,3 a 19,7 en el mismo período (E51, E52). El máximo de 5 años es la semana del 28/06/2026 (E50).
2. **HIPÓTESIS:** el primer salto (semana del 27/07/2025, índice 57) coincide con la declaración de intención del 28/07/2025 para el reingreso de Argentina al Visa Waiver Program (D28). El pico de junio y julio de 2026 coincide con el Mundial en EE.UU. La suba sostenida desde noviembre de 2025 no tiene una causa identificada en fuente primaria. Que coincidan en fecha no prueba la causa.
3. **ESTIMACIÓN:** el anuncio del 02/10/2026 tuvo reacción inmediata. En EE.UU., el índice horario de "argentina citizenship" pasó de 0,1 a 13,2 de promedio, y en el mundo de 0,7 a 30,5. El máximo fue a las 19:00 UTC del 02/10 en los dos casos (E53, E54, E63, E64). Las consultas relacionadas en mayor ascenso de la semana son "argentina citizenship by investment program" (+1.300%) y "argentina citizenship by investment" (+450%) (E62).
4. **ESTIMACIÓN:** en las últimas 52 semanas, en EE.UU., "argentina citizenship" (26,1) superó a "portugal golden visa" (21,2) y quintuplicó a "dominica citizenship" (5,2), "st kitts citizenship" (3,2) y "turkey citizenship by investment" (3,4) (E70). **Contrapeso:** "argentina citizenship" también captura la ciudadanía por descendencia, por matrimonio y por residencia, que no tienen nada que ver con el programa CBI.
5. **DATO (con cautela):** fuera de EE.UU., el interés relativo por "argentina citizenship" más alto en 12 meses está en Suiza (44), Rusia (43), Finlandia (42), Suecia, Hungría y Portugal (E57). En español, "pasaporte argentino" pesa más en España (92), México (88) y Chile (87) (E60). **HIPÓTESIS:** que Rusia aparezca coincide con el índice de movilidad del Módulo B (B31). Los rankings de términos de bajo volumen son ruidosos: la primera corrida, que incluía países de bajo volumen, ponía a Guinea Ecuatorial y St. Kitts en 100, y en portugués aparece Sri Lanka.

## Gráficos
- `outputs/charts/E2_us_pasaporte_5y.{png,svg}`: EE.UU., serie semanal de 5 años.
- `outputs/charts/E2_Q2_7dias`, `E2_Q3_7dias`: reacción horaria al anuncio, en EE.UU. y en el mundo.
- `outputs/charts/E2_paises`: países con mayor interés relativo, por término.

## Método
`src/05b_busquedas_pasaporte.py`: 8 consultas vía pytrends, con 75 s de pausa entre una y otra y como máximo 2 intentos por consulta. Cada respuesta cruda se guarda con fecha y se reutiliza si ya existe. Los rankings por país usan `inc_low_vol=False`, que excluye a los países con volumen insuficiente.

## Fuentes
| Fuente | Tipo | URL |
|---|---|---|
| Google Trends (vía pytrends 4.9.2) | R | https://trends.google.com/trends/explore |

## Fuentes fallidas
| Fecha | Fuente | Error | Acción |
|---|---|---|---|
| 2026-10-03 | Google Trends | 429 en el primer intento | Segundo intento espaciado con User-Agent identificable: OK |

## Limitaciones
- No son volúmenes: un índice de 30 en un término de bajo volumen puede representar pocas búsquedas.
- Términos en inglés y español: el interés en otros idiomas (chino, ruso, árabe) no está medido.
- La semana del anuncio está incompleta (`isPartial`) en la serie semanal.
