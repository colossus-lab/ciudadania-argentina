# Fuentes fallidas

Fuentes que no pudieron descargarse o verificarse, con causa y acción. Generado por `src/08_informe.py`.

## General (probe de fuentes)

| Fecha | Fuente | Error | Causa | Acción |
|---|---|---|---|---|
| 2026-10-03 | 52 URLs de 39 dominios (primer probe) | ProxyError 403 al CONNECT | Política de red del primer entorno | Resuelto: red habilitada; probe 48/55 OK |
| 2026-10-03 | web.archive.org | Conexión reseteada por el proxy de egreso (ws_closed_mid_exchange) durante toda la primera sesión | Red del primer entorno | **Resuelto:** el mismo día se re-corrieron los módulos desde otra red; la Wayback respondió y se completaron la serie de rechazo de visas (D) y los respaldos de los demás módulos |
| 2026-10-03 | api.census.gov | El probe lo marcó OK pero redirige a missing_key.html | La API exige key con registro | E usó el ACS Summary File oficial |

## Módulo A — Marco normativo

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | HCDN, Comisión Bicameral Permanente | https://www.hcdn.gob.ar/comisiones/especiales/cbtramite/ | HTTP 404 (también /comisiones/bicameral/tramite-legislativo/) | Sitio | Se usó la ficha del Senado (Expte. 46/25 PE) y el buscador de proyectos de la HCDN (A21–A27) |
| 2026-10-03 | InfoLEG, buscador de normas | https://www.argentina.gob.ar/normativa/buscar | La búsqueda por texto no devuelve resultados al pedido automatizado | Sitio | Se usó la ficha "normas que modifican" del DNU 366/2025 |
| 2026-10-03 | PJN, consulta pública de expedientes (incluye CSJ y CNE) | https://scw.pjn.gov.ar/scw/home.seam | El formulario exige captcha (captcha.pjn.gov.ar) | Protección anti-bots | No se elude; queda "no verificado" si "Yang" llegó a la CSJN |
| 2026-10-03 | CSJN, base de jurisprudencia y novedades | https://sjconsulta.csjn.gov.ar/sjconsulta/ | El formulario exige reCAPTCHA (también /novedades/consulta.html) | Protección anti-bots | No se elude |
| 2026-10-03 | CSJN, registro de procesos colectivos | https://servicios.csjn.gov.ar/ConsultaCausasColectivas/ | El formulario exige reCAPTCHA | Protección anti-bots | No se elude |
| 2026-10-03 | CIJ, buscador de sentencias (tribunales federales y nacionales) | https://www.csjn.gov.ar/tribunales-federales-nacionales/sentencias.html | El formulario exige captcha (captchav3.csjn.gov.ar) | Protección anti-bots | No se elude; las sentencias siguen con la copia de Palabras del Derecho |
| 2026-10-03 | CIJ, buscador de fallos (versión anterior) | https://www.csjn.gov.ar/tribunales-federales-nacionales/buscador-de-fallos.html | Sin resultados para "Yang" ni para el Expte. 8843/2023; la base de la CNE termina en 2009 | Cobertura | — |
| 2026-10-03 | CIJ, portada "sentencias del día" (Wayback, capturas 20260812203222 y 20260815224603) | https://web.archive.org/web/20260812203222id_/https://www.csjn.gov.ar/tribunales-federales-nacionales/inicio.html | Las 20 sentencias listadas en cada captura no incluyen la del Juzgado Federal de Esquel | Cobertura | — |
| 2026-10-03 | CNE, buscador de fallos, acordadas y resoluciones | https://www.electoral.gob.ar/nuevo/paginas/jurisprudencia/consulta.php | El formulario exige captcha (securimage y reCAPTCHA); la base tiene fallos del 2026-06-30 | Protección anti-bots | No se elude; no se enumeraron identificadores de recuperar.php |
| 2026-10-03 | CNE, documentos de fallos en Wayback (CDX) | https://web.archive.org/cdx/search/cdx?url=electoral.gob.ar/nuevo/paginas/jurisprudencia/recuperar.php&matchType=prefix | Solo hay 3 identificadores archivados (6958, 11724, 13454), ninguno de 2026 | Cobertura | — |
| 2026-10-03 | Boletín Oficial, primera sección 03/10/2026 | https://www.boletinoficial.gob.ar/seccion/primera/20261003 | Redirige a la portada; no hay edición (sábado) | Sin publicación | Se registró la edición vigente (A29) |

## Módulo B: mercado potencial

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | Fed SCF 2025 | https://www.federalreserve.gov/econres/files/scfp2025s.zip | HTTP 404 | Todavía no publicado (la página índice dice que 2022 es el último) | Se usa el SCF 2022; re-correr cuando salga el 2025 |
| 2026-10-03 | Henley Passport Index API | https://api.henleypassportindex.com/api/v3/countries | — (responde 200) | Los términos prohíben el acceso automatizado y la reproducción (B28, B29) | No se usa; alternativa Passport Index Data (MIT). **Afecta también al Módulo D**, que planeaba usar Henley |
| 2026-10-03 | passportindex.org (términos de la fuente original del dataset) | https://www.passportindex.org/ | HTTP 403 ("Just a moment…") | Protección anti-bots (Cloudflare) | **Resuelto vía Wayback (2026-10-03):** no hay página de términos entre ~66 mil URLs archivadas; la nota legal de About no da licencia ni prohíbe reutilizar, y el sitio es de Arton Capital (B52). Se mantiene el dataset MIT como R con advertencia |
| 2026-10-03 | Knight Frank, The Wealth Report 2026 | https://www.knightfrank.com/wealthreport | Formulario de registro | El informe se entrega tras completar un formulario (B27) | No se usa (regla de no scrapear detrás de un registro) |
| 2026-10-03 | UBS, databook por país | página GWR 2026 | No hay databook enlazado | UBS solo publica 34 de 56 mercados en el PDF | Se usa la tabla de la p. 22; los otros 22 mercados quedan fuera del índice |
| 2026-10-03 | EUR-Lex, Reg. (UE) 2025/11 | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32025R0011 | HTTP 202 con cuerpo vacío | Desafío anti-bots (AWS WAF, `x-amzn-waf-action: challenge`) | Mismo texto oficial vía la Oficina de Publicaciones (Cellar) |
| 2026-10-03 | Ley de Nacionalidad de China (NPC) | http://www.npc.gov.cn/zgrdw/englishnpc/Law/2007-12/12/content_1383852.htm | Redirige a la portada | URL obsoleta (sin captura Wayback de esa URL) | **Resuelto (2026-10-03):** captura Wayback de la URL correcta, `.../2007-12/13/content_1384056.htm`, más la ficha de vigencia de flk.npc.gov.cn (B44–B46) |
| 2026-10-03 | Citizenship Act 1955 (India) | indiacode.nic.in / mha.gov.in | HTTP 403 | Protección anti-bots | **Resuelto (2026-10-03):** captura Wayback del PDF oficial del MHA, `CitizenshipAct1955_02012025.pdf` (B47, B48). legislative.gov.in también da 403 |
| 2026-10-03 | flk.npc.gov.cn, descarga del PDF/DOCX de la ley china | https://flk.npc.gov.cn/law-search/download/pc | Requiere captcha (`/law-search/index/captchaImage`) | El sitio protege la descarga con captcha | No se descargó (regla de no eludir captchas). El texto viene de la versión inglesa del NPC (Wayback) y la vigencia, de la ficha JSON pública (B46) |
| 2026-10-03 | pravo.gov.ru, PDF oficial de la Ley 138-FZ (Rusia) | http://publication.pravo.gov.ru/file/pdf?eoNumber=0001202304280013 | PDF sin capa de texto (escaneo) | Publicación en imagen | Se usó el texto de kremlin.ru (B49). Es el texto publicado en 2023 y no se verificaron reformas posteriores del art. 10 |
| 2026-10-03 | Al Meezan (Qatar) | https://www.almeezan.qa/LawArticles.aspx?LawArticleID=39318&LawId=2591&language=en | `SSLCertVerificationError` en Python (requests) | El servidor no envía la cadena TLS intermedia | Copia bajada con curl, con verificación TLS del sistema operativo (`ssl_verify_result=0`), y reutilizada desde `data/raw` (B50) |
| 2026-10-03 | Ley de nacionalidad de Arabia Saudita (Bureau of Experts) | https://laws.boe.gov.sa/ | Timeout de conexión | Sitio inaccesible desde esta máquina; Wayback tiene ~2.700 fichas `LawDetails` sin título identificable | **No verificado:** queda "no verificado" en la tabla del índice |
| 2026-10-03 | Sudáfrica y Turquía (leyes de ciudadanía) | — | No se intentó | Fuera del alcance de esta pasada (pesan el 1,4 % y el 0,9 % de I1) | **No verificado** |
| 2026-10-03 | Fed SCF 2025 (re-chequeo) | https://www.federalreserve.gov/econres/scfindex.htm | Sigue apareciendo 2022 como "the most recent survey conducted"; `scfp2025s.zip` da 404 | No publicado | Sin cambios: se mantiene el SCF 2022 (B01–B11 no cambian) |
| 2026-10-03 | UBS, databook (re-chequeo) | https://www.ubs.com/global/en/wealthmanagement/insights/global-wealth-report.html | La página solo enlaza los PDF del GWR 2026 y 2025 | No hay databook 2026 | Sin cambios |

## Módulo C — Benchmark de programas de ciudadanía por inversión

Detalle completo en `data/processed/C_fuentes_fallidas.csv`. Resueltas el 04/10/2026 y retiradas de la tabla: Dominica (cbiu.gov.dm ya no pide captcha: C91–C94), Vanuatu (el dominio oficial es vancitizenship.gov.vu: C95–C96), Jordania (copia Wayback del Ministerio de Inversión: C97–C99), FMI Article IV 2026 (PDF en imf.org/-/media/files/…/2026/english/: C63–C69, C76) y la Wayback Machine (ahora responde).

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | Dominica, leyes (dominica.gov.dm) | https://www.dominica.gov.dm/laws/2024/… | 502 / connection reset | Host caído | Misma S.R.O. 8/2024 desde cbiu.gov.dm (C92) |
| 2026-10-03 | Dominica, S.R.O. 46/2025 | https://www.cbiu.gov.dm/wp-content/uploads/2025/12/CBI-Amendment-Regulation-2025.pdf | PDF escaneado sin texto | Escaneo | Lectura visual (C94): no cambia montos |
| 2026-10-03 | Granada imm.gov.gd | https://www.imm.gov.gd/ | 502 | Host caído | Se usó laws.gov.gd |
| 2026-10-03 | Granada IMA (imagrenada.gd) | https://imagrenada.gd/wp-content/uploads/2024/07/S.R.O.-15-of-2024-… | 202 + sgcaptcha | Anti-bots | Se usó laws.gov.gd |
| 2026-10-03 | Vanuatu (PacLII / citizenship.gov.vu) | https://www.paclii.org/vu/legis/num_reg/ | 403 / 502; sin capturas Wayback | Anti-bots / dominio inexistente | Dominio oficial vancitizenship.gov.vu (C95–C96); la Order 33/2019 es un escaneo y no se usó |
| 2026-10-03 | Jordania (JIC / MOIN en vivo) | https://www.jic.gov.jo/en/ | Connection reset / timeout | Host inaccesible | Mecanismo 2025 vía Wayback (C97) |
| 2026-10-03 | Egipto (decreto 876/2023) | https://www.state.gov/reports/2024-investment-climate-statements/egypt/ | 403; decreto no publicado en abierto | Anti-bots / fuente no publicada | GAFI (Wayback 2026) no publica montos; el SIS solo reproduce prensa (S). Monto no verificado |
| 2026-10-03 | FMI eLibrary | https://www.elibrary.imf.org/view/journals/002/2026/093/002.2026.issue-093-en.xml | 403 (vista); 202 vacío (PDF) | Anti-bots | PDF oficiales en imf.org/-/media/files/…/2026/english/ |
| 2026-10-03 | FMI Vanuatu Article IV 2026 | https://www.imf.org/-/media/files/publications/cr/2026/english/1vutea2026001-source-pdf.pdf | 404 | No publicado (o con otro nombre) | Se usa CR 25/277 (C76) |
| 2026-10-03 | FMI Antigua CR 23/184 | https://www.imf.org/-/media/Files/Publications/CR/2023/English/1ATGEA2023001.ashx | Tablas como imagen | Sin capa de texto | Antigua desde 2020 (CR 25/96 y 26/97); sin OCR |
| 2026-10-03 | Comisión Europea, carta del 25/06/2026 | https://ec.europa.eu/commission/presscorner/api/search?language=en&text=citizenship%20by%20investment | Sin resultados en el press corner (9 búsquedas) | Carta no publicada | Queda como S; se agrega el octavo informe VSM (C28) |
| 2026-10-03 | EUR-Lex | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32025R2441 | 202 vacío (03/10); timeout (04/10) | WAF / conexión inestable | Mismo texto vía Oficina de Publicaciones |
| 2026-10-03 | Curia | https://curia.europa.eu/juris/liste.jsf?num=C-181/23&language=en | Redirige a infocuria (JS) | Contenido en JavaScript | Sentencia vía Oficina de Publicaciones |
| 2026-10-03 | Diário da República (PT) | https://diariodarepublica.pt/dr/detalhe/lei/56-2023-221792115 | 200, 2 KB (JS) | Contenido en JavaScript | Texto consolidado de la AT |
| 2026-10-03 | Resmî Gazete 13/05/2022 | https://www.resmigazete.gov.tr/eskiler/2022/05/20220513-20.pdf | PDF sin texto | Escaneo | Texto consolidado de mevzuat.gov.tr |

## Módulo D — Pasaporte argentino y Visa Waiver Program de EE.UU.

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | Henley Passport Index (API y web) | https://api.henleypassportindex.com/api/v3/countries | No usada | Los términos de uso lo prohíben (acceso automatizado; uso comercial sin licencia) | Sin datos de Henley; sustituto Passport Index Data (R) |
| 2026-10-03 | Henley — serie histórica del puesto argentino | https://www.henleyglobal.com/passport-index/ranking | No usada | Los términos de uso lo prohíben | Serie histórica sin fuente |
| 2026-10-03 | travel.state.gov (Refusal Rates y NIV Detail Tables) | https://travel.state.gov/content/dam/visas/Statistics/Non-Immigrant-Statistics/RefusalRates/FY25.pdf | HTTP 403 | Anti-bots para clientes automatizados | **Resuelto:** copias del mismo archivo oficial en la Wayback Machine (20/20 PDF de rechazo; 19 tablas NIV). En la primera corrida web.archive.org cortaba la conexión (`ws_closed_mid_exchange`); se re-corrió desde otra red |
| 2026-10-03 | DoS NIV Detail Table FY2025 | https://travel.state.gov/content/dam/visas/Statistics/Non-Immigrant-Statistics/NIVDetailTables/FY25NIVDetailTable.xlsx | Sin captura 200 (API de disponibilidad ni CDX) | No publicada todavía o no archivada | Serie de visas emitidas hasta FY2024 |
| 2026-10-03 | uscode.house.gov | https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title8-section1187 | HTTP 200 con "Under Maintenance" | Mantenimiento | Se usó Cornell LII |
| 2026-10-03 | FederalRegister.gov (HTML/TXT) | https://www.federalregister.gov/documents/full_text/html/2014/03/31/2014-07254.html | "Request Access" (CAPTCHA) | Anti-scraping (solo la API está abierta) | API + copia oficial de govinfo.gov |
| 2026-10-03 | EUR-Lex (Reglamento 2018/1806) | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02018R1806-20250101 | HTTP 202 vacío | Desafío anti-bots | No necesario para este módulo (el Módulo B lo obtuvo vía Cellar) |
| 2026-10-03 | UK Parliament, written statement HCWS979 | https://questions-statements.parliament.uk/written-statements/detail/2023-07-19/hcws979 | HTTP 403 | Anti-bots | Se usó el Explanatory Memorandum de gov.uk |

El detalle por año está en `data/processed/D_fuentes_fallidas.csv`.

## Módulo E: ¿Argentina es más "popular" desde Qatar 2022?

Fuentes que siguen sin poder usarse (el script las vuelca en `data/processed/E_fuentes_fallidas.csv`):

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | Census API ACS B05006 | https://api.census.gov/data/2023/acs/acs1?get=NAME,B05006_001E&for=us:1 | HTTP 302 → `missing_key.html` | La API exige una key, y la key requiere un formulario de registro. **Ojo:** `docs/probe_fuentes.csv` marca esta fuente como OK, pero su URL final es `missing_key.html` (falso positivo del probe) | Se usó el ACS Summary File oficial (mismas estimaciones) |
| 2026-10-03 | NTTO I-92 / APIS por país de destino | https://www.trade.gov/us-international-air-travel-statistics-i-92-data | Producto de pago (USD 150 a USD 5.795) | Licencia comercial | Se usó el agregado gratuito "South America" como control de demanda (E29) |

**Resueltas (revisión del 2026-10-03, con la Wayback Machine ya accesible):**
- **FIFA, resultado del Mundial 2026** (https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/spain-argentina-final-report-highlights). El índice CDX tiene capturas desde el 19/07/2026 (p. ej. `20260720115443`), pero todas son el cascarón JS de fifa.com: unos 4,5 KB con `<div id="root"></div>` y sin contenido ni JSON embebido. No se usó `cxm-api.fifa.com` (API no documentada). **Se resolvió con las notas oficiales de CONMEBOL, AFA y RFEF**, archivadas en la Wayback Machine (E34–E36). La nota de AFA lleva fecha 17/07/2026 (anterior al partido; parece ser la fecha de alta de la nota). La fecha de la final sale de CONMEBOL ("julio 19, 2026").
- **INDEC, página de la ETI.** El registro anterior apuntaba a `Nivel4-Tema-3-13-56`, que es la Encuesta de Ocupación Hotelera. La página de la ETI es `Nivel4-Tema-3-13-55`. El propio sitio carga su contenido desde el fragmento HTML `/Nivel4/Tema/3/13/55`, que es el mismo HTML que ve el navegador (no es una API). Ese fragmento lista los cuadros por paso (p. ej. `eti26_ezeyaerop_cuadros.xls`), las series (`series_eti_via_aerea.xlsx`, `series_mensual_aeroparque_ezeiza_2026.xlsx`) y el último informe técnico. Está guardado en `data/raw/E_indec_eti_pagina_nivel4_2026-10-03.html`. Los cuatro informes trimestrales usados (E17–E20) son PDF de indec.gob.ar verificados con cita literal; el buscador sólo sirvió para ubicarlos.
- **Wikimedia Pageviews API:** daba HTTP 429 intermitente (rate limit por IP compartida del proxy). Se resolvió con reintentos espaciados (`download_retry`), y las 19 series se bajaron completas.
- **DHS OHSS con curl:** daba HTTP 403 (Akamai). Con `requests` (`src/common.py`) responde 200, y los xlsx se bajaron con `download()`.
- **Ente de Turismo CABA (E21)** y **Com. "A" 8226 / salida del cepo el 14/04/2025 (E28):** ya estaban verificadas con cita literal en la fuente oficial. No quedaban pendientes.

## Módulo E (extensión) — Búsquedas en Google sobre el pasaporte y la ciudadanía argentina

| Fecha | Fuente | Error | Acción |
|---|---|---|---|
| 2026-10-03 | Google Trends | 429 en el primer intento | Segundo intento espaciado con User-Agent identificable: OK |

## Módulo F — "Refugio austral": Argentina frente a Nueva Zelanda, Uruguay, Chile, Portugal y Canadá

| Fecha | Fuente | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | whc.unesco.org | /en/list/xml/ | HTTP 403 (en el reintento, HTTP 503) | Anti-bots / servicio no disponible | Se usó **UNESCO Open Data, dataset whc001** (fuente primaria, modificado el 2026-10-02, incluye las inscripciones de 2026). La captura de Wayback 20250716131746, que antes fallaba, ahora responde, pero es más vieja que whc001 |
| 2026-10-03 | www.energia.gob.ar (https) | balance_2025_v0_h.xlsx | `CERTIFICATE_VERIFY_FAILED` (unable to get local issuer certificate) | Cadena de certificados incompleta en el servidor | Se descargó por http (los enlaces del CKAN apuntan a http); el sha256 queda en el ledger. No se desactivó TLS |
| 2026-10-03 | Riesgo país (EMBI) por país: NZL, URY, CHL, PRT, CAN | apis.datos.gob.ar/series/api/search; api.bcra.gob.ar/estadisticas/v4.0/monetarias; OCDE DF_FINMARK | Sin resultados | El EMBI de JP Morgan es propietario; ninguna fuente oficial publica el spread por país de los cinco comparables | Celdas "s/d". Argentina: dato del BCRA (IPOM, F123). Comparable para los seis: calificación soberana (F127–F138). No se rellenó con datos de prensa |
| 2026-10-03 | OCDE, tasa de largo plazo de ARG y URY | sdmx.oecd.org (DF_FINMARK, IRLT) | La consulta no devuelve series para ARG ni URY | No son miembros de la OCDE | Celdas "s/d" en esa fila |
| 2026-10-03 | U.S. State Department, relación bilateral | https://www.state.gov/u-s-relations-with-argentina/ (en vivo y captura Wayback 20260218075946) | HTTP 403; la captura de Wayback guardó la página "Technical Difficulties / Exception: forbidden" | Anti-bots (también al archivar) | La lista de aliados extra-OTAN se obtuvo vía Wayback (F149); el resto, con U.S. Treasury (ESF) |
| 2026-10-03 | NZ Treasury / NZ Debt Management | https://debtmanagement.treasury.govt.nz/investor-resources/credit-ratings | HTTP 403 | Anti-bots | Se usó la captura de Wayback del 09/04/2026 (F129); un cambio de calificación posterior no quedaría reflejado |
| 2026-10-03 | BCRA, buscador de WordPress | https://www.bcra.gob.ar/wp-json/wp/v2/search | HTTP 403 | WAF del sitio | No se eludió; el texto ordenado y el IPOM se ubicaron por la navegación pública del sitio |
| 2026-10-03 | Reinhart-Rogoff (Varieties of Crises) | carmenreinhart.com | No se encontró un enlace directo a datos descargables | — | Se usó la base BoC–BoE 2025 (pública y con metodología documentada) |

## Módulo G — Escenarios fiscales

| Fecha | Fuente | Error | Acción |
|---|---|---|---|
| 2026-10-03 | api.bcra.gob.ar v3.0 | 410 Gone | Se usó la v4.0 |
