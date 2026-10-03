# Fuentes fallidas

Fuentes que no pudieron descargarse o verificarse, con causa y acción. Generado por `src/08_informe.py`.

## General (probe de fuentes)

| Fecha | Fuente | Error | Causa | Acción |
|---|---|---|---|---|
| 2026-10-03 | 52 URLs de 39 dominios (primer probe) | ProxyError 403 al CONNECT | Política de red del primer entorno | Resuelto: red habilitada; probe 48/55 OK |
| 2026-10-03 | web.archive.org | Conexión reseteada por el proxy de egreso (ws_closed_mid_exchange) durante toda la sesión | Red del entorno | Afecta a D (serie de tasas de rechazo) y a fallbacks de C y F; reintentar con `python src/04_pasaporte_vwp.py` |
| 2026-10-03 | api.census.gov | El probe lo marcó OK pero redirige a missing_key.html | La API exige key con registro | E usó el ACS Summary File oficial |

## Módulo A — Marco normativo

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | HCDN, Comisión Bicameral Permanente | https://www.hcdn.gob.ar/comisiones/especiales/ | La página no lista los dictámenes (contenido dinámico) | Sitio | Prensa (tipo S) solo para fechar; queda "no verificado" |
| 2026-10-03 | InfoLEG, buscador de normas | https://www.argentina.gob.ar/normativa/buscar | La búsqueda por texto no devuelve resultados al pedido automatizado | Sitio | Se usó la ficha "normas que modifican" del DNU 366/2025 |

## Módulo B: mercado potencial

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | Fed SCF 2025 | https://www.federalreserve.gov/econres/files/scfp2025s.zip | HTTP 404 | Todavía no publicado (la página índice dice que 2022 es el último) | Se usa el SCF 2022; re-correr cuando salga el 2025 |
| 2026-10-03 | Henley Passport Index API | https://api.henleypassportindex.com/api/v3/countries | — (responde 200) | Los términos prohíben el acceso automatizado y la reproducción (B28, B29) | No se usa; alternativa Passport Index Data (MIT). **Afecta también al Módulo D**, que planeaba usar Henley |
| 2026-10-03 | passportindex.org (términos de la fuente original del dataset) | https://www.passportindex.org/ | HTTP 403 ("Just a moment…") | Protección anti-bots (Cloudflare) | Se intentó Wayback (captura 21/09/2026 de la portada): la conexión a web.archive.org se cortó. Se usa el dataset MIT con advertencia (tipo R) |
| 2026-10-03 | Knight Frank, The Wealth Report 2026 | https://www.knightfrank.com/wealthreport | Formulario de registro | El informe se entrega tras completar un formulario (B27) | No se usa (regla de no scrapear detrás de un registro) |
| 2026-10-03 | UBS, databook por país | página GWR 2026 | No hay databook enlazado | UBS solo publica 34 de 56 mercados en el PDF | Se usa la tabla de la p. 22; los otros 22 mercados quedan fuera del índice |
| 2026-10-03 | EUR-Lex, Reg. (UE) 2025/11 | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32025R0011 | HTTP 202 con cuerpo vacío | Desafío anti-bots (AWS WAF, `x-amzn-waf-action: challenge`) | Mismo texto oficial vía la Oficina de Publicaciones (Cellar) |
| 2026-10-03 | Ley de Nacionalidad de China (NPC) | http://www.npc.gov.cn/zgrdw/englishnpc/Law/2007-12/12/content_1383852.htm | Redirige a la portada | URL obsoleta | Restricción de doble nacionalidad marcada "no verificada" |
| 2026-10-03 | Citizenship Act 1955 (India) | indiacode.nic.in / mha.gov.in | HTTP 403 | Protección anti-bots | Idem: "no verificado" |

## Módulo C — Benchmark de programas de ciudadanía por inversión

Detalle completo en `data/processed/C_fuentes_fallidas.csv`.

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | Dominica CBIU | https://www.cbiu.gov.dm/investment-options/ | 202 → /.well-known/sgcaptcha/ | Captcha anti-bots (también en los PDF) | Wayback falló (ver abajo); Dominica queda "no verificado" |
| 2026-10-03 | Dominica, leyes (S.R.O. 1 y 8/2024) | https://www.dominica.gov.dm/laws/2024/… | 502 / connection reset | Host caído | Solo el piso regional (C20) como contexto |
| 2026-10-03 | Wayback Machine | https://web.archive.org/web/20260916071416id_/https://www.cbiu.gov.dm/investment-options/ | Connection reset | El túnel a web.archive.org se corta (archive.org/wayback/available sí responde) | Captura identificada, no descargada |
| 2026-10-03 | Granada imm.gov.gd | https://www.imm.gov.gd/ | 502 | Host caído | Se usó laws.gov.gd |
| 2026-10-03 | Granada IMA (imagrenada.gd) | https://imagrenada.gd/wp-content/uploads/2024/07/S.R.O.-15-of-2024-… | 202 + sgcaptcha | Anti-bots | Se usó laws.gov.gd |
| 2026-10-03 | Vanuatu (PacLII / Citizenship Office) | https://www.paclii.org/vu/legis/num_reg/ ; https://citizenship.gov.vu/ | 403 / 502 | Anti-bots / host caído | Monto no verificado |
| 2026-10-03 | Jordania (JIC / MOIN) | https://www.jic.gov.jo/en/ | Connection reset; MOIN redirige a la portada árabe | Host inaccesible | Monto no verificado |
| 2026-10-03 | Egipto (decreto 876/2023) | https://www.state.gov/reports/2024-investment-climate-statements/egypt/ | 403; decreto no publicado en abierto | Anti-bots | Monto no verificado |
| 2026-10-03 | FMI Article IV 2026 (St Kitts CR 26/93, Dominica CR 26/117) | https://www.imf.org/en/publications/cr/issues/2026/05/07/st-575691 | 403; eLibrary 202 vacío | Anti-bots; el PDF no sigue el patrón -/media | Serie cortada en 2024 (estimación) |
| 2026-10-03 | FMI Antigua CR 23/184 | https://www.imf.org/-/media/Files/Publications/CR/2023/English/1ATGEA2023001.ashx | Tablas como imagen | Sin capa de texto | Antigua solo 2020–2024 |
| 2026-10-03 | EUR-Lex | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32025R2441 | 202, cuerpo vacío | WAF | Mismo texto vía Oficina de Publicaciones |
| 2026-10-03 | Curia | https://curia.europa.eu/juris/liste.jsf?num=C-181/23&language=en | Redirige a infocuria (JS) | Contenido en JavaScript | Sentencia vía Oficina de Publicaciones |
| 2026-10-03 | Diário da República (PT) | https://diariodarepublica.pt/dr/detalhe/lei/56-2023-221792115 | 200, 2 KB (JS) | Contenido en JavaScript | Texto consolidado de la AT |
| 2026-10-03 | Resmî Gazete 13/05/2022 | https://www.resmigazete.gov.tr/eskiler/2022/05/20220513-20.pdf | PDF sin texto | Escaneo | Texto consolidado de mevzuat.gov.tr |

## Módulo D — Pasaporte argentino y Visa Waiver Program de EE.UU.

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | Henley Passport Index (API y web) | https://api.henleypassportindex.com/api/v3/countries | No usada | Los términos de uso lo prohíben (acceso automatizado; uso comercial sin licencia) | Sin datos de Henley; sustituto Passport Index Data (R) |
| 2026-10-03 | Henley — serie histórica del puesto argentino | https://www.henleyglobal.com/passport-index/ranking | No usada | Los términos de uso lo prohíben | Serie histórica sin fuente |
| 2026-10-03 | DoS Adjusted Refusal Rates B, FY2006–FY2025 (20 PDF) | `web.archive.org/web/<ts>id_/https://travel.state.gov/.../RefusalRates/FY{yy}.pdf` (ver `D_wayback_capturas.csv`) | `ConnectionResetError`; proxy: `ws_closed_mid_exchange` | web.archive.org corta la conexión desde este entorno (archive.org sí responde); travel.state.gov da 403 | Capturas ubicadas y registradas; re-correr el script cuando web.archive.org responda. Sin relleno |
| 2026-10-03 | DoS NIV Detail Tables (B1/B2 por nacionalidad) | `web.archive.org/web/20260430115050id_/.../FY24NIVDetailTable.xlsx` y siguientes | `ConnectionResetError` | Ídem | Ídem |
| 2026-10-03 | Library of Congress Web Archive | https://webarchive.loc.gov/all/2014*/travel.state.gov/... | HTTP 403 (Cloudflare "Just a moment") | Anti-bots | Descartado |
| 2026-10-03 | arquivo.pt CDX | https://arquivo.pt/wayback/cdx | HTTP 403 | Acceso denegado | Descartado |
| 2026-10-03 | CRS (crsreports.congress.gov, RL32221) | https://crsreports.congress.gov/product/pdf/RL/RL32221 | HTTP 403 | Anti-bots | Descartado |
| 2026-10-03 | uscode.house.gov | https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title8-section1187 | HTTP 200 con "Under Maintenance" | Mantenimiento | Se usó Cornell LII |
| 2026-10-03 | FederalRegister.gov (HTML/TXT) | https://www.federalregister.gov/documents/full_text/html/2014/03/31/2014-07254.html | "Request Access" (CAPTCHA) | Anti-scraping (solo la API está abierta) | API + copia oficial de govinfo.gov |
| 2026-10-03 | EUR-Lex (Reglamento 2018/1806) | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02018R1806-20250101 | HTTP 202 vacío | Desafío anti-bots | No necesario para este módulo (el Módulo B lo obtuvo vía Cellar) |
| 2026-10-03 | UK Parliament, written statement HCWS979 | https://questions-statements.parliament.uk/written-statements/detail/2023-07-19/hcws979 | HTTP 403 | Anti-bots | Se usó el Explanatory Memorandum de gov.uk |

El detalle por año está en `data/processed/D_fuentes_fallidas.csv`.

## Módulo E: ¿Argentina es más "popular" desde Qatar 2022?

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | Census API ACS B05006 | https://api.census.gov/data/2023/acs/acs1?get=NAME,B05006_001E&for=us:1 | HTTP 302 → `missing_key.html` | La API exige una key, y la key requiere un formulario de registro. **Ojo:** `docs/probe_fuentes.csv` marca esta fuente como OK, pero su URL final es `missing_key.html` (falso positivo del probe) | Se usó el ACS Summary File oficial (mismas estimaciones) |
| 2026-10-03 | Wikimedia Pageviews API | https://wikimedia.org/api/rest_v1/metrics/pageviews/… | HTTP 429 intermitente (envoy rate limit, `retry-after: 1`) | Límite por IP compartida del proxy | Reintentos espaciados (`download_retry`); las 19 series se bajaron completas |
| 2026-10-03 | DHS OHSS (ohss.dhs.gov) con curl | https://ohss.dhs.gov/topics/immigration/yearbook | HTTP 403 (Akamai) | Anti-bots que bloquea a curl; con `requests` (src/common.py) responde 200 | Se descargaron los xlsx con `download()`. La Wayback Machine (web.archive.org) cortaba la conexión vía el proxy (`ws_closed_mid_exchange`) y no hizo falta |
| 2026-10-03 | FIFA (resultado del Mundial 2026) | https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/spain-argentina-final-report-highlights | El HTML no trae contenido (se renderiza con JavaScript); la captura Wayback no se pudo bajar | Sitio JS; el endpoint `cxm-api.fifa.com` es una API no documentada y no se usó | **Resultado de Argentina: no verificado.** Los buscadores (S) indican que Argentina fue finalista, pero no se usa como dato |
| 2026-10-03 | NTTO I-92 / APIS por país de destino | https://www.trade.gov/us-international-air-travel-statistics-i-92-data | Producto de pago (USD 150 a USD 5.795) | Licencia comercial | Se usó el agregado gratuito "South America" como control de demanda (E29) |
| 2026-10-03 | INDEC, página de la ETI | https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-13-56 | La página no lista cuadros xls (se carga por JavaScript) | Sitio dinámico | Se usaron yvera (CKAN) y los PDF de informes técnicos ubicados por buscador |

## Módulo E (extensión) — Búsquedas en Google sobre el pasaporte y la ciudadanía argentina

| Fecha | Fuente | Error | Acción |
|---|---|---|---|
| 2026-10-03 | Google Trends | 429 en el primer intento | Segundo intento espaciado con User-Agent identificable: OK |

## Módulo F — "Refugio austral": Argentina frente a Nueva Zelanda, Uruguay, Chile, Portugal y Canadá

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | Banco Mundial API v2 | https://api.worldbank.org/v2/country/…/indicator/… | Primero, timeouts sin respuesta; después, HTTP 502 con página `waf-block` | Bloqueo anti-bots (WAF) del Banco Mundial tras pocas consultas | Se usó la **API Data360** del Banco Mundial (mismas bases WGI y WDI). El valor de prueba ARG RL 2025 = −0,1024 coincide en ambas APIs |
| 2026-10-03 | Wayback Machine (UNESCO XML, captura 20250716131746) | https://web.archive.org/web/20250716131746id_/https://whc.unesco.org/en/list/xml | `Connection reset by peer` (5 intentos) | El túnel del proxy de egreso se cierra (`ws_closed_mid_exchange`) | Se usó **UNESCO Open Data, dataset whc001** (fuente primaria, modificado el 2026-10-02, incluye las inscripciones de 2026) |
| 2026-10-03 | whc.unesco.org | /en/list/xml/ | HTTP 403 | Anti-bots (ya registrado en el probe) | Ídem |
| 2026-10-03 | www.energia.gob.ar (https) | balance_2025_v0_h.xlsx | `CERTIFICATE_VERIFY_FAILED` (unable to get local issuer certificate) | Cadena de certificados incompleta en el servidor | Se descargó por http (los enlaces del CKAN apuntan a http); el sha256 queda en el ledger. No se desactivó TLS |
| 2026-10-03 | Riesgo país (EMBI) | apis.datos.gob.ar/series/api/search; api.bcra.gob.ar/estadisticas/v4.0/monetarias | Sin resultados | El EMBI de JP Morgan es propietario; no hay serie pública oficial vigente | Celda "s/d"; no se rellenó con datos de prensa |
| 2026-10-03 | U.S. State Department | https://www.state.gov/u-s-relations-with-argentina/ ; https://2021-2025.state.gov/major-non-nato-ally-status/ | HTTP 403 / página "Technical Difficulties" | Anti-bots | Se usó U.S. Treasury (ESF) como fuente primaria del gobierno de EE.UU. |
| 2026-10-03 | Reinhart-Rogoff (Varieties of Crises) | carmenreinhart.com | No se encontró un enlace directo a datos descargables | — | Se usó la base BoC–BoE 2025 (pública y con metodología documentada) |

## Módulo G — Escenarios fiscales

| Fecha | Fuente | Error | Acción |
|---|---|---|---|
| 2026-10-03 | api.bcra.gob.ar v3.0 | 410 Gone | Se usó la v4.0 |
