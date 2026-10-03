# Módulo E: ¿Argentina es más "popular" desde Qatar 2022?

Script: `src/05_popularidad.py` (corre de punta a punta desde `data/raw`). Fecha de corte: 03/10/2026.
Los claim_id remiten a `docs/claims/claims_E.csv`.

## Resumen (5 líneas)

1. **ESTIMACIÓN:** tras la final de Qatar hubo un escalón real de atención. Frente a Chile, Uruguay, Brasil y Colombia, el artículo "Argentina" de Wikipedia en inglés subió +22% (IC95 +10% a +36%). El mismo escalón aparece en alemán (+28%) y en español (+10%). Pero se erosiona a razón de unos 8 puntos log por año y el efecto neto se anula hacia 05/2025 (E07–E09).
2. **ESTIMACIÓN (contrapeso):** en 2025–26 la atención volvió a la base. La atención relativa en inglés pasó de +19% en 2023 a −2% en ago–sep 2026. En valores absolutos, las vistas de ago–sep 2026 están 25% por debajo de ene–oct 2022. En español, la atención relativa cae 12% (E03, E05, E06). Messi-Miami y el balotaje no dejan escalón positivo, y el período posterior a la salida del cepo (14/04/2025) muestra −10% (E08, E28).
3. **ESTIMACIÓN (a favor):** en Google EE.UU. el interés relativo por "Argentina" siguió por encima de la base: +27% en 2025 y +15% en ago–sep 2026, fuera de los meses de torneo. Los picos son de torneo: dic-2022 = 49 y jul-2026 = 100 en el índice 0–100 (E11, E12).
4. **ESTIMACIÓN (contrapeso):** las llegadas de residentes de EE.UU. y Canadá superaron a 2019 en sólo +5% en 2025, contra +41% de los viajes aéreos de ciudadanos de EE.UU. a Sudamérica. Cayeron −9,9% en 2025, y CABA registró 284.609 estadounidenses (−11% i.a.). En 2026 rebotan: +17% en ene–ago y +34% en el 2T en Ezeiza+Aeroparque. La elasticidad al tipo de cambio real bilateral es 0,38, pero la apreciación explica sólo −3,5 de los −9,9 puntos de 2025 (E13–E15, E20, E21, E23, E31).
5. **HIPÓTESIS (veredicto):** la tesis **se sostiene parcialmente**. Qatar dejó un pico enorme y un escalón de atención de 1 a 2 años, que en Wikipedia ya se disipó y en Google persiste moderado. El turismo norteamericano crece menos que su mercado regional y es sensible al precio. Ningún indicador muestra un salto sostenido atribuible a Messi-Miami o a Milei sobre "Argentina" como país (E32).

## Veredicto: "Argentina es más popular desde Qatar 2022"

**Se sostiene parcialmente** (**HIPÓTESIS**, apoyada en las estimaciones que siguen).

| Efecto | Evidencia a favor | Evidencia en contra |
|---|---|---|
| **Mundial Qatar** | Pico absoluto de la serie: 564.280 vistas el 18/12/2022 (E01). Escalón post-final de +22% (en), +28% (de) y +10% (es) relativo a controles, con IC que excluyen 0 (E07–E09). Binseg detecta sin fecha a priori un quiebre al alza el 20/11/2022 en inglés (+24%) y el 16/10/2022 en alemán (+24%) (E10). | El escalón decae unos 8 pp log por año y se anula hacia 05/2025 (E07). Binseg detecta quiebres a la baja el 07/01/2024 (−11%) y el 12/01/2025 (−7%) (E10). |
| **Messi-Miami (07/2023)** | El artículo "Lionel Messi" (en) se duplicó en 2023 (media geométrica 43.503 vs 22.867 vistas diarias en la base; `E_atencion_ventanas.csv`). | Sin escalón en "Argentina": −10% (p=0,23) en inglés, −9% (p=0,03) en español (E08). La atención va a Messi, no al país. |
| **Milei (balotaje y asunción)** | El artículo "Javier Milei" (en) pasó de ~200 a ~4.300 vistas diarias en 2025. En alemán el escalón del balotaje es +8%, no significativo (p=0,15). | Escalón en "Argentina" (en) de −3% (p=0,46); en español, −9% (p=0,01) (E08). Binseg ubica un quiebre a la baja 4 semanas después de la asunción: 07/01/2024, −11% en inglés y −16% en español (E10). En turismo, `post_milei` da −4% (p=0,15) (E23). |
| **Tipo de cambio / cepo** | Elasticidad de las llegadas EE.UU.+Canadá al ITCR bilateral (t−1) de 0,38 (IC95 0,17–0,59) (E23). EE.UU.+Canadá ganó participación en el total de turistas no residentes: del 7,2% en 2019 al 9,9% en 2025 (E33). | La salida (parcial) del cepo (14/04/2025, E28) llegó con un peso real más apreciado: ITCRB EE.UU. de 146,6 en ene-2024 a 95,4 en abr-2025 y 93,2 en sep-2026 (E22). La atención relativa cae −10% después de esa fecha (E08). La apreciación explica sólo un tercio de la caída del turismo en 2025 (E31). |
| **Mundial 2026** | 2.º mayor día de la serie: 218.272 vistas el 19/07/2026 (E02). En Google EE.UU., jul-2026 = 100, máximo histórico desde 2004 (E11). | Un mes después las vistas vuelven a su piso: ago–sep 2026 está 25% por debajo de 2022 (E03). El torneo se jugó en EE.UU., lo que infla la búsqueda local. **El resultado de Argentina en el Mundial 2026 no está verificado en fuente primaria descargable** (ver Fuentes fallidas). |

**Lo que va en contra de la tesis, con el mismo énfasis:**
- **ESTIMACIÓN:** en valores absolutos, el artículo "Argentina" (en) tuvo en 2025 un 11% menos de vistas diarias que en ene–oct 2022, y en ago–sep 2026 un 25% menos (E03). Parte de la caída es general: los controles también caen −15% (E04), una tendencia de toda Wikipedia en inglés.
- **ESTIMACIÓN:** en español, la atención relativa a Argentina está −12% bajo la base en 2025 y −15% en ago–sep 2026 (E06, `E_atencion_ventanas.csv`).
- **DATO / ESTIMACIÓN:** el turismo de EE.UU.+Canadá cayó −9,9% en 2025 (E13). CABA confirma 284.609 llegadas de estadounidenses (−11% i.a.; dato del plan re-verificado en la fuente oficial, E21). En Ezeiza+Aeroparque, el 1T-2025 cayó −11,6% (E17) y el 3T-2025 −3,9% (E18).
- **ESTIMACIÓN:** contra la "popularidad", Argentina recuperó mucho menos que el resto del destino Sudamérica: +5% vs 2019, frente a +41% de los viajes de EE.UU. a Sudamérica (E15).
- **ESTIMACIÓN:** con un control de demanda (viajes de EE.UU. a Sudamérica), el escalón post-Qatar en turismo baja a +9% y deja de ser significativo (p=0,35) (E23).
- **ESTIMACIÓN:** la diáspora argentina en EE.UU. (ACS) es estable: 210.767 en 2019 y 210.909 en 2024. El cambio 2022→2024 (+7%) no es estadísticamente significativo (E24–E25).

**Lo que va a favor y no hay que esconder:**
- **ESTIMACIÓN:** en Google EE.UU., el cociente Argentina/pares sigue +15% a +27% sobre la base pre-Qatar (E12).
- **DATO:** el 2026 muestra un rebote fuerte del turismo norteamericano. En el 1T-2026 llegaron 159,8 mil turistas (+28,9%) y en el 2T-2026 77,0 mil (+33,8%). El gasto total del 1T-2026 fue de USD 233,7 M (+52,4%) (E19–E20). Las llegadas de ene–ago 2026 crecen +17% contra ene–ago 2025, con datos provisorios (E14).
- **DATO:** las residencias permanentes (green cards) otorgadas a nacidos en Argentina pasaron de 4.130 (FY2022) a 5.710 (FY2024), el máximo de la serie 2015–2024 (E26). Esto mide emigración argentina hacia EE.UU., no atracción de estadounidenses hacia Argentina.

## Hallazgos y método

### 1. Atención (Wikimedia Pageviews)
- **Datos:** API REST de Wikimedia, `agent=user`, `all-access`, diaria del 01/07/2015 al 02/10/2026. Se usaron 7 artículos foco: Argentina (en, es) y Argentinien (de), Buenos Aires, Lionel Messi, Javier Milei y Patagonia (en). Los controles en inglés son Chile, Uruguay, Brazil y Colombia. Como robustez se agregaron controles en el mismo idioma para es (Chile, Uruguay, Brasil, Colombia) y de (Chile, Uruguay, Brasilien, Kolumbien). Archivos: `data/raw/E_wikimedia_pv_*`; series en `data/processed/E_pageviews_{diarias,mensuales}.csv`.
- **Serie relativa:** `D = log(vistas Argentina) − media(log vistas controles)`, guardada en `E_atencion_relativa_diaria.csv`. Neutraliza la caída general de Wikipedia (E04) y el cambio de clasificación de tráfico automatizado de 2020, que afecta a todos los artículos por igual.
- **Ventanas descriptivas** (`E_atencion_ventanas.csv`): media geométrica sin los días de torneo (Mundiales 2018/22/26 y Copas América 2019/21/24), contra la base ene–oct 2022.
- **ITS** (`E_its_resultados.csv`): OLS sobre D (en/es/de) y sobre log(vistas en), con dummies de mes y de día de la semana, pulsos por cada torneo, un pulso por el anuncio CBI y errores HAC Newey-West (30 rezagos). M1 es la regresión segmentada clásica (nivel y pendiente post-18/12/2022). M2 agrega escalones acumulativos en Qatar (18/12/2022), Messi-Miami (15/07/2023, fecha de corte dentro de 07/2023), balotaje (19/11/2023) y cepo (14/04/2025). El balotaje y la asunción (10/12/2023) están a 21 días: no se separan, y el escalón del balotaje captura ambos.
- **Quiebres** (`E_quiebres.csv`): `ruptures.Binseg` con costo l2 sobre la media semanal de D, sin las semanas de torneo y sin fechas a priori. El número de quiebres sale del BIC: n·ln(RSS/n) + (2K+1)·ln(n). En inglés, el quiebre más fuerte es el de 23/05/2021, antes de Qatar, y el de 20/11/2022 es el tercero en orden de detección. Esto muestra que la serie ya era volátil antes del Mundial.
- **Temas:** el artículo "Messi" se duplica en 2023 y vuelve a la base en 2025. "Milei" pasa de ~200 a miles de vistas diarias. "Buenos Aires" y "Patagonia" no muestran un aumento sostenido: Patagonia está −30% bajo la base en 2025. Ver `E_pageviews_temas.png`.

### 2. Google Trends EE.UU.
- **Datos:** pytrends funcionó al primer intento: `date=all`, `geo=US`, keywords Argentina, Buenos Aires, Chile, Uruguay y Colombia, guardado en `data/raw/E_gtrends_us_2026-10-03.csv`. Se analiza desde 2016 el cociente Argentina / promedio(Chile, Uruguay, Colombia), sin meses de torneo (`E_google_trends_*.csv`).
- **Si una re-ejecución falla (429 o bloqueo):** el script no insiste. Registra los dos intentos en `data/raw/E_gtrends_intentos_<fecha>.json` y sigue. Para reponer el dato a mano:
  1. En el navegador, abrir `https://trends.google.com/trends/explore?date=all&geo=US&q=Argentina,Buenos%20Aires,Chile,Uruguay,Colombia`.
  2. En "Interest over time", usar el botón de descarga (CSV).
  3. Quitar las 2 líneas de encabezado y renombrar las columnas a `date,Argentina,Buenos Aires,Chile,Uruguay,Colombia`. Las fechas van en formato AAAA-MM-01.
  4. Guardarlo como `data/raw/E_gtrends_us_<AAAA-MM-DD>.csv`. El script lo toma automáticamente.

### 3. Turismo receptivo
- **DNM total país** (yvera, `turistas-no-residentes-serie.csv`): llegadas mensuales de "EE.UU. y Canadá" por medio de transporte, de ene-2010 a ago-2026. 2025–26 son datos provisorios. Es la serie principal porque cubre todos los pasos.
- **ETI** (INDEC/SECTUR, yvera): turistas y estadía de "EE.UU. y Canadá" en Ezeiza+Aeroparque, de 2014 a dic-2025. El gasto por residencia sale de los informes técnicos trimestrales de INDEC (1T-2025, 3T-2025, 1T-2026 y 2T-2026), verificado con cita literal (E17–E20). Yvera publica el gasto sólo por paso, no por residencia.
- **Advertencias:** la ETI cubre sólo aeropuertos y pasos seleccionados (Ezeiza, Aeroparque, Córdoba, Mendoza, Puerto de Buenos Aires y Cristo Redentor), no el total del país. **EE.UU. viene agregado con Canadá** en todas las series oficiales argentinas. Desde ene-2026, INDEC reagrupa Bolivia, Paraguay y Uruguay en "Resto de América" en algunas tablas.
- **Modelo** (`E_turismo_modelo.csv`): `log(llegadas EE.UU.+Can) ~ log(ITCRB EE.UU. t−1) + tendencia + post_qatar(2023-01) + post_milei(2023-12) + post_cepo(2025-04) + mundial26 + dummies de mes`. Muestra de 2014-01 a 2026-08, sin 2020-03..2022-03 (cierre de fronteras y reapertura), con HAC de 12 rezagos. T2 usa el ITCRM multilateral (elasticidad 0,34). T3 agrega log(viajes de EE.UU. a Sudamérica, NTTO) como control de demanda. Los coeficientes son **ESTIMACIÓN**.
- **NTTO:** sólo publica gratis el agregado por regiones ("South America"). El detalle I-92/APIS por país es de pago (E29). Por eso no hay serie pública de viajes EE.UU.→Argentina.

### 4. Tipo de cambio real
BCRA `ITCRMSerie.xlsx`, hoja de promedios mensuales: ITCRM y bilateral EE.UU., base 17-12-15=100. Un valor más alto significa una Argentina más barata. El salto de dic-2023 a ene-2024 (146,6) se revirtió en 2024. En sep-2026 el bilateral está en 93,2; entre abr y sep de 2026 estuvo en los niveles más apreciados desde mediados de 2018 (mínimo 91,4 en may-2026) (E22).

### 5. Diáspora y migración
- **ACS 1 año, tabla B05006** (nacidos en Argentina, total de nacidos en el extranjero y Sudamérica), 2010–2019 y 2021–2024. **No existe el ACS 1 año 2020** (no se publicó por la pandemia). La API `api.census.gov` exige ahora una key, que requiere registro. Por eso se usó el **Summary File oficial** (www2.census.gov): sequence-based para 2010–2021 y table-based para 2022–2024. Las estimaciones son las mismas que publica la API, con su margen de error (MOE) al 90% (`E_diaspora_acs_b05006.csv`).
- **DHS OHSS Yearbook FY2024:** residencias permanentes (LPR) por país de nacimiento (Tabla 3) y naturalizaciones (Tabla 22), FY2015–2024 (`E_dhs_lpr_naturalizaciones.csv`). Los valores vienen redondeados a la decena en la fuente.

### 6. Eventos (`E_eventos.csv`)
| Fecha | Evento | Fuente / estado |
|---|---|---|
| 18/12/2022 | Final de Qatar 2022 | S (solo para fechar) |
| 07/2023 (corte 15/07/2023) | Messi al Inter Miami | S (aproximado al mes) |
| 19/11/2023 | Balotaje | S |
| 10/12/2023 | Asunción de Milei | S |
| 20/06–14/07/2024 | Copa América 2024 | S |
| 14/04/2025 | Salida del cepo para personas humanas: Com. "A" 8226 del 11/04/2025, "con vigencia a partir del 14/04/25" | **P, confirmada** (E28). Es una apertura **parcial**: habilita a personas humanas; no es la liberación total del mercado de cambios |
| 11/06–19/07/2026 | Mundial 2026 | S (fechas). **Resultado de Argentina: no verificado** |
| 02/10/2026 | Anuncio del Programa CBI | P (Módulo A) |

## Fuentes

| Fuente | Tipo | URL |
|---|---|---|
| Wikimedia Pageviews API (per-article, daily, agent=user) | P | https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/ |
| Google Trends (pytrends), geo=US | R | https://trends.google.com/trends/explore?date=all&geo=US&q=Argentina,Buenos%20Aires,Chile,Uruguay,Colombia |
| Yvera / DNM — Turismo internacional total país (receptivo) | P | https://datos.yvera.gob.ar/dataset/4cbf7d4a-702a-4911-8c1e-717a45214902 |
| Yvera / INDEC ETI — no residentes mensual Ezeiza+Aeroparque y gasto trimestral por paso | P | https://datos.yvera.gob.ar/dataset/78b880c1-50d5-4a0c-9c87-7350e70548c2 |
| INDEC — Estadísticas de turismo internacional (1T-25, 3T-25, 1T-26, 2T-26) | P | https://www.indec.gob.ar/uploads/informesdeprensa/eti_04_257F79FE4B90.pdf · eti_10_250B9725FF40.pdf · eti_04_261D31E891A2.pdf · eti_07_2611F2D28020.pdf |
| Ente de Turismo CABA — Perfil mercado EE.UU. 2025 | P | https://turismo.buenosaires.gob.ar/sites/turismo/files/eeuu_perfiles_internacionales_2025.pdf |
| NTTO (trade.gov) — U.S. citizen travel to international regions | P | https://www.trade.gov/sites/default/files/2024-02/US-Outbound-to-World-Regions.xlsx |
| NTTO — página del programa I-92 (precios) | P | https://www.trade.gov/us-international-air-travel-statistics-i-92-data |
| BCRA — ITCRM y bilaterales | P | https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/ITCRMSerie.xlsx |
| BCRA — Comunicación "A" 8226 | P | https://www.bcra.gob.ar/archivos/Pdfs/comytexord/A8226.pdf |
| U.S. Census Bureau — ACS 1-year Summary File, B05006 (2010–2024) | P | https://www2.census.gov/programs-surveys/acs/summary_file/ |
| DHS OHSS — Yearbook FY2024, LPR (Tabla 3) | P | https://ohss.dhs.gov/system/files/2026-06/2026_0604_ohss_yearbook_lawful_permanent_residents_fy2024.xlsx |
| DHS OHSS — Yearbook FY2024, Naturalizations (Tabla 22) | P | https://ohss.dhs.gov/system/files/2026-06/2026_0604_ohss_yearbook_naturalizations_fy2024.xlsx |
| FIFA / prensa (solo para fechar eventos deportivos y políticos) | S | — |

## Fuentes fallidas

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | Census API ACS B05006 | https://api.census.gov/data/2023/acs/acs1?get=NAME,B05006_001E&for=us:1 | HTTP 302 → `missing_key.html` | La API exige una key, y la key requiere un formulario de registro. **Ojo:** `docs/probe_fuentes.csv` marca esta fuente como OK, pero su URL final es `missing_key.html` (falso positivo del probe) | Se usó el ACS Summary File oficial (mismas estimaciones) |
| 2026-10-03 | Wikimedia Pageviews API | https://wikimedia.org/api/rest_v1/metrics/pageviews/… | HTTP 429 intermitente (envoy rate limit, `retry-after: 1`) | Límite por IP compartida del proxy | Reintentos espaciados (`download_retry`); las 19 series se bajaron completas |
| 2026-10-03 | DHS OHSS (ohss.dhs.gov) con curl | https://ohss.dhs.gov/topics/immigration/yearbook | HTTP 403 (Akamai) | Anti-bots que bloquea a curl; con `requests` (src/common.py) responde 200 | Se descargaron los xlsx con `download()`. La Wayback Machine (web.archive.org) cortaba la conexión vía el proxy (`ws_closed_mid_exchange`) y no hizo falta |
| 2026-10-03 | FIFA (resultado del Mundial 2026) | https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/spain-argentina-final-report-highlights | El HTML no trae contenido (se renderiza con JavaScript); la captura Wayback no se pudo bajar | Sitio JS; el endpoint `cxm-api.fifa.com` es una API no documentada y no se usó | **Resultado de Argentina: no verificado.** Los buscadores (S) indican que Argentina fue finalista, pero no se usa como dato |
| 2026-10-03 | NTTO I-92 / APIS por país de destino | https://www.trade.gov/us-international-air-travel-statistics-i-92-data | Producto de pago (USD 150 a USD 5.795) | Licencia comercial | Se usó el agregado gratuito "South America" como control de demanda (E29) |
| 2026-10-03 | INDEC, página de la ETI | https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-13-56 | La página no lista cuadros xls (se carga por JavaScript) | Sitio dinámico | Se usaron yvera (CKAN) y los PDF de informes técnicos ubicados por buscador |

## Limitaciones
- **Pageviews ≠ intención de inversión ni de residencia.** Wikipedia mide curiosidad, mayormente deportiva y noticiosa. Los picos son torneos, y los escalones son modestos y transitorios. Ninguna de estas series mide demanda de ciudadanía por inversión.
- Wikipedia en inglés pierde tráfico en forma general (los controles caen −15% entre 2022 y 2025; E04). Por eso la medida relevante es la relativa (D). Los controles (Chile, Uruguay, Brasil y Colombia) también tienen shocks propios: estallido en Chile, Copa América 2024 en EE.UU. con Colombia y Uruguay, entre otros.
- La ITS supone que, sin eventos, D sigue una tendencia lineal con estacionalidad. Los escalones son acumulativos y los eventos cercanos (balotaje y asunción, a 21 días) no se pueden separar. Los coeficientes son **ESTIMACIÓN** con HAC; la autocorrelación diaria es alta.
- **Google Trends:** el índice es relativo (0–100) y redondeado a enteros. Con valores bajos (Uruguay = 1), el cociente es ruidoso y está dominado por Colombia. Google cambió su recolección el 01/01/2016 y el 01/01/2022; la base pre-Qatar (ene–oct 2022) queda después del último cambio. El Mundial 2026 se jugó en EE.UU., lo que infla las búsquedas locales de jun–jul 2026.
- **Turismo:** EE.UU. viene agregado con Canadá. La ETI cubre sólo pasos seleccionados. Los datos de 2025–26 de la DNM son provisorios. NTTO mide salidas aéreas de ciudadanos de EE.UU. (incluye escalas y otro universo), por lo que la comparación con la DNM es de tendencias (índice 2019 = 100), no de niveles. El modelo omite variables como conectividad aérea, precios relativos de pasajes y seguridad percibida.
- **ACS:** es una muestra, con MOE de ±10–13 mil personas. Las variaciones interanuales en general no son significativas (E25). Las LPR y naturalizaciones miden emigración argentina, no "popularidad" entre estadounidenses.
- **Mundial 2026:** el resultado de Argentina no está verificado en fuente primaria. El análisis usa sólo la ventana del torneo (11/06–19/07/2026), que también es S.
