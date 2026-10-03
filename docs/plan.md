# Plan de trabajo — Ciudadanía por Inversión y el "momento Argentina"

**Fecha:** 2026-10-03 · **Estado:** plan para revisión (paso 1 de la "Forma de trabajo") · **Autor:** Colossus Lab

---

## 0. Bloqueo actual: el contenedor no tiene salida a internet hacia las fuentes

Se corrió `src/00_probe_fuentes.py` contra 53 URLs de 40 dominios (resultado crudo en `docs/probe_fuentes.csv`).

| Resultado | Cantidad |
|---|---|
| Responden 2xx | **0 / 53** |
| Rechazo del proxy de salida del entorno (HTTP 403 al `CONNECT`) | 52 |
| 403 del propio proxy (datos.energia.gob.ar, por HTTP plano) | 1 |

**No es una caída de las fuentes:** el proxy de salida del entorno de ejecución solo deja pasar registros de paquetes
(pypi, npm) y GitHub. La herramienta de lectura web alternativa (WebFetch) también está bloqueada por la misma
política (`EGRESS_BLOCKED` en argentina.gob.ar y boletinoficial.gob.ar). Solo funciona un buscador web que devuelve
fragmentos de prensa, **que según las reglas del proyecto no puede ser fuente de cifras**.

Por lo tanto, **ningún dato del informe puede descargarse ni verificarse hasta habilitar la red.** No se completó
nada "a ojo". Todo queda documentado en `docs/fuentes_fallidas.md`.

### Qué hay que cambiar

En la configuración del entorno cloud (menú del entorno en la barra de título de la sesión → *Edit* → *Network access*):

- **Opción simple:** nivel de acceso *Full*.
- **Opción restringida:** *Custom*, conservando la lista por defecto de gestores de paquetes y agregando estos dominios:

```
# Normativa argentina
www.boletinoficial.gob.ar  www.argentina.gob.ar  servicios.infoleg.gob.ar  www.saij.gob.ar
www.hcdn.gob.ar  www.senado.gob.ar  www.cancilleria.gob.ar  www.csjn.gov.ar  www.cij.gov.ar
# Estadística y economía argentina
www.indec.gob.ar  www.bcra.gob.ar  api.bcra.gob.ar  apis.datos.gob.ar  datos.gob.ar
datos.yvera.gob.ar  www.yvera.tur.ar  datos.energia.gob.ar  www.economia.gob.ar
turismo.buenosaires.gob.ar  www.estadisticaciudad.gob.ar  sib.gob.ar  www.parquesnacionales.gob.ar
# EE.UU.
www.federalreserve.gov  travel.state.gov  www.state.gov  www.dhs.gov  ohss.dhs.gov  www.cbp.gov
uscode.house.gov  www.law.cornell.edu  www.govinfo.gov  www.federalregister.gov
api.census.gov  www.trade.gov  pubs.usgs.gov  www.usgs.gov
# Multilaterales e índices
api.worldbank.org  www.imf.org  faostatservices.fao.org  bulks-faostat.fao.org  whc.unesco.org
worldjusticeproject.org  www.visionofhumanity.org  www.economicsandpeace.org
wikimedia.org  trends.google.com
# Riqueza y pasaportes
www.ubs.com  www.knightfrank.com  altrata.com  www.henleyglobal.com  api.henleypassportindex.com
# UE y programas CBI (fuentes gubernamentales)
eur-lex.europa.eu  curia.europa.eu  home-affairs.ec.europa.eu  www.consilium.europa.eu  ec.europa.eu
cbiu.gov.dm  ciu.gov.kn  cip.gov.ag  www.imm.gov.gd  www.cipsaintlucia.com  citizenship.gov.vu
komunita.gov.mt  aima.gov.pt  www.boe.es  www.gov.uk  www.irishimmigration.ie
```

Si el entorno se cambia, re-correr `python src/00_probe_fuentes.py` y este plan se actualiza con el resultado real.

---

## 1. Fuentes por módulo

Columnas: **Tipo** = P (primaria) / R (referencia privada con metodología pública) / S (secundaria, solo para fechar).
**Riesgo** = problemas esperables *independientes* del bloqueo de red, a confirmar al probar.

### Módulo A — Marco normativo

| Fuente | URL | Tipo | Uso | Riesgo |
|---|---|---|---|---|
| Anuncio MECON (2/10/2026) | argentina.gob.ar/noticias/luis-caputo-anuncio-… | P | Montos, cronograma, organismos | — |
| DNU 366/2025 (BO 29/05/2025) | boletinoficial.gob.ar/detalleAviso/primera/326096/20250529 | P | Modifica Ley 346 (arts. 2 bis, 6 bis), crea la Agencia | Confirmar que es DNU (la ficha de InfoLEG lo titula "Decreto DNU 366/2025") |
| DNU 366/2025 ficha + texto actualizado | argentina.gob.ar/normativa/nacional/norma-413297 | P | Normas modificatorias, vigencia | — |
| Decreto 524/2025 (BO 31/07/2025) | boletinoficial.gob.ar/detalleAviso/primera/329061/20250731 | P | Reglamentación | Verificar qué reglamenta exactamente |
| Decreto 285/2026 (BO 28/04/2026) | boletinoficial.gob.ar/pdf/aviso/primera/341227/20260428 | P | Designación de la directora ejecutiva | — |
| Resolución que fija USD 350.000 / 800.000 | Búsqueda en BO, sección primera, oct-2026 | P | Fuente normativa de los montos | **Puede no estar publicada aún** → se deja explícito |
| Comisión Bicameral Ley 26.122 | hcdn.gob.ar/comisiones/especiales/cbtramite | P | Dictámenes sobre el DNU 366 | Información dispersa en órdenes del día |
| Proyectos de ley de derogación | hcdn.gob.ar / senado.gob.ar (buscador de proyectos) | P | Proyectos que rechazan el DNU | — |
| Causas judiciales | cij.gov.ar / csjn.gov.ar | P | Amparos contra el DNU | Sentencias de primera instancia no siempre publicadas → prensa solo para fechar |

**Alerta temprana a verificar:** fragmentos de prensa citan que el DNU 366/2025 hablaba de inversiones "de más de USD 500.000",
mientras el anuncio de 2026 fija USD 350.000 (aporte). Si se confirma, hay que explicar qué norma habilitó el cambio.

### Módulo B — Mercado potencial

| Fuente | URL | Tipo | Uso | Riesgo |
|---|---|---|---|---|
| Fed — Distributional Financial Accounts | federalreserve.gov/releases/z1/dataviz/download/zips/dfa.zip | P | Riqueza top 1% / 0,1%, trimestral | — |
| Fed — Survey of Consumer Finances | federalreserve.gov/econres/files/scfp2022s.zip (+ SCF 2025 si ya salió) | P | Hogares por tramo >1M, >5M, >10M con pesos muestrales | SCF 2025 se publica habitualmente en otoño boreal; verificar. SCF no cubre bien la cola extrema (excluye Forbes 400) |
| UBS Global Wealth Report 2026 | ubs.com/…/global-wealth-report | R | Millonarios por país (insumo del cruce con pasaportes) | PDF descargable; las tablas por país están en el anexo |
| Altrata World Ultra Wealth Report 2026 | altrata.com | R | UHNWI (>USD 30M) | **Probable formulario de registro** → si lo exige, no se scrapea; se documenta |
| Knight Frank Wealth Report 2026 | knightfrank.com/wealthreport | R | UHNWI | Idem: suele pedir registro |
| Henley Passport Index | henleyglobal.com / api.henleypassportindex.com | R | Destinos sin visa por pasaporte | La API no está documentada oficialmente: revisar términos antes de usarla |
| Schengen: lista de países con exigencia de visa | Reglamento (UE) 2018/1806, anexos I y II (EUR-Lex) | P | Variable "necesita visa Schengen" | — |

**Método:** para el universo "realista" se estiman hogares >USD 5M y >USD 30M (SCF para >5M y >10M; DFA + informes privados para
la cola). Se calcula aporte / patrimonio por tramo. Para la hipótesis de comprador no estadounidense: índice
`millonarios(UBS) × (destinos_AR − destinos_país)⁺ × 1{necesita visa Schengen}` y variantes, ranking de mercados.

### Módulo C — Benchmark CBI

| Fuente | Uso | Riesgo |
|---|---|---|
| Sitios gubernamentales: Dominica (cbiu.gov.dm), St Kitts y Nevis (ciu.gov.kn), Antigua y Barbuda (cip.gov.ag), Granada, Santa Lucía, Vanuatu, Turquía, Egipto, Jordania, Nauru, Malta (komunita.gov.mt) | Montos mínimos y tipo de aporte | Algunos montos solo están en reglamentos (SROs) y no en las webs |
| FMI — Article IV de países del Caribe + DataMapper (PBI) | Recaudación CBI en USD y % del PBI | Las cifras CBI aparecen en tablas/recuadros de PDFs; extracción con pdfplumber |
| EUR-Lex: Reglamento de suspensión de la exención de visa a Vanuatu | Caso regulatorio | — |
| Curia: sentencia C-181/23 Comisión c. Malta (29/04/2025) | Caso regulatorio | — |
| Portugal (AIMA / Diário da República), España (BOE, Ley 1/2025), Reino Unido (gov.uk, cierre Tier 1 Investor 2022), Irlanda (IIP, cierre 2023) | Cierres/reformas golden visa | — |

### Módulo D — Pasaporte y Visa Waiver

| Fuente | Uso | Riesgo |
|---|---|---|
| Henley Passport Index, histórico | Puesto y destinos sin visa de Argentina | El histórico puede no estar en formato descargable; se arma año por año |
| 8 U.S.C. §1187 (uscode.house.gov) | Requisitos legales del VWP (umbral de rechazo <3%, ePassport, intercambio de información) | — |
| DoS — tasas ajustadas de rechazo B, FY2006–FY2025 (travel.state.gov/…/RefusalRates/FY25.pdf, etc.) | Serie Argentina y Chile pre-2014 | Un PDF por año; extracción con pdfplumber |
| DoS — Report of the Visa Office (tablas de NIV emitidas por nacionalidad y clase) | Visas B1/B2 emitidas a argentinos | Formato cambia entre años |
| DHS — página VWP y Federal Register (designación de Chile 2014) | Precedentes | — |

### Módulo E — ¿Argentina más "popular" desde Qatar 2022?

| Serie | Fuente | Frecuencia | Riesgo |
|---|---|---|---|
| Atención (principal) | Wikimedia Pageviews API, en/es/de, 7 artículos + 4 controles, desde 2015-07-01 | Diaria | Ninguno conocido (API abierta) |
| Búsqueda en EE.UU. | Google Trends vía `pytrends` | Mensual | **Alto:** suele devolver 429/bloqueo. Plan B: instrucciones para exportar CSV a mano desde trends.google.com y dejarlos en `data/raw/` |
| Turismo receptivo | INDEC ETI / datos.yvera.gob.ar (CKAN): llegadas "EE.UU. y Canadá", gasto, estadía | Mensual | ETI cubre aeropuertos seleccionados, no el total; "EE.UU. y Canadá" viene agregado |
| Turismo CABA | Observatorio Turístico CABA (dato del contexto: 284.609 en 2025, −11% i.a.) | Anual | Re-verificar |
| Salidas de residentes de EE.UU. | NTTO / trade.gov (APIS/I-92) | Mensual | **Probable:** el detalle por país de destino puede ser de pago; se documenta |
| Tipo de cambio real | BCRA ITCRM (xlsx diario) + bilateral EE.UU. | Diaria | — |
| Diáspora | Census ACS B05006 (api.census.gov), 2010–2024 | Anual | ACS 1-año 2020 no publicado (pandemia) |
| Residencias y naturalizaciones | DHS OHSS Yearbook | Anual | Tablas en xlsx por año |

**Eventos marcados:** 18/12/2022 · 07/2023 · 19/11/2023 · 10/12/2023 · Copa América 2024 · salida del cepo (fecha a verificar en BCRA,
se espera 14/04/2025 por Com. "A" 8226 — **no confirmado**) · Mundial 2026 (resultado de Argentina **a verificar, no se supone**) · 02/10/2026.

**Método:** (1) gráficos con eventos; (2) ITS con regresión segmentada sobre log-pageviews, dummies de mes/día de semana y diferencia
contra el promedio de controles (Chile, Uruguay, Brasil, Colombia), errores HAC Newey-West; (3) quiebres con `ruptures` (PELT/Binseg,
penalidad BIC) sin fijar fecha; (4) turismo: `log(llegadas_EEUU) ~ log(ITCRM) + dummies eventos + estacionalidad`;
(5) veredicto: se sostiene / parcialmente / no se sostiene, separando Mundial, Messi-Miami, Milei y tipo de cambio.

### Módulo F — "Refugio austral" (AR vs NZ, UY, CL, PT, CA)

| Dimensión | Fuente |
|---|---|
| Paz y gobernanza | Global Peace Index (IEP); World Bank WGI vía api.worldbank.org/v2 |
| Autosuficiencia alimentaria | FAOSTAT Food Balance Sheets (producción vs. suministro interno) |
| Energía | Secretaría de Energía (datos.energia.gob.ar): producción Vaca Muerta, balanza energética |
| Litio | USGS Mineral Commodity Summaries 2026 |
| Atractivo natural | UNESCO World Heritage List (XML); APN / SIB |
| **Contrapesos (obligatorios)** | Defaults soberanos (FMI / fuentes académicas con metodología pública), inflación (INDEC IPC; WB para comparar), riesgo país (fuente pública a confirmar — el EMBI de JP Morgan no es abierto), controles de capital / corralito (BCRA, normativa), WJP Rule of Law Index |
| Geopolítica | Cancillería, Departamento de Estado, DHS (candidatura VWP) |

### Módulo G — Escenarios fiscales

| Fuente | Uso |
|---|---|
| Montos del anuncio / resolución (Módulo A) | Parámetros |
| BCRA — reservas internacionales brutas (API v3) | Comparación |
| Secretaría de Finanzas — perfil de vencimientos de deuda en moneda extranjera | Comparación |
| Recaudación CBI de otros países (Módulo C) | Comparación |

Escenarios de 100 / 500 / 1.000 / 3.000 solicitantes principales por año, con mezcla aporte/bono y tamaño familiar. Rotulados **ESCENARIO**.

---

## 2. Entregables y estructura

```
data/raw/          descargas originales con fecha (nombre_YYYY-MM-DD.ext)
data/processed/    series limpias
src/00_probe_fuentes.py   prueba de disponibilidad (hecho)
src/01_normativa.py … src/07_escenarios.py, src/08_informe.py, src/09_auditoria.py
outputs/charts/    PNG + SVG, fuente al pie
outputs/informe.{md,html,pdf}   fondo blanco
docs/claims_ledger.csv, fuentes.md, fuentes_fallidas.md, metodologia.md
run_all.py / Makefile
```

Etiquetas obligatorias en el texto: **DATO**, **ESTIMACIÓN**, **HIPÓTESIS**, **ESCENARIO**.

## 3. Orden de ejecución propuesto

1. Habilitar red → re-correr el probe → actualizar este plan.
2. Módulos A → G en orden, con resumen de 5 líneas al cierre de cada uno.
3. Informe → auditoría de `claims_ledger.csv` contra las copias locales → README con `make all`.
