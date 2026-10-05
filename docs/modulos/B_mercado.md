# Módulo B: mercado potencial

**Fecha:** 2026-10-03 · **Script:** `src/02_mercado.py` · **Afirmaciones:** `docs/claims/claims_B.csv` (B01–B54)

## Resumen (5 líneas)

1. **ESTIMACIÓN:** en EE.UU. hay unos 4,8 M de hogares con patrimonio neto > USD 5 M y 2,1 M > USD 10 M (SCF 2022, en dólares de 2022). Para el tramo > USD 5 M, el aporte de USD 350.000 equivale al 3,8 % del patrimonio mediano (B03, B04, B07).
2. **DATO:** el top 0,1 % de EE.UU. (136.779 hogares) tiene USD 27,9 billones, el 15,0 % del patrimonio de los hogares al 2T-2026. Con el resto del top 1 %, el grupo suma el 32,5 % (B12, B13, B15, B16). **ESTIMACIÓN:** para un hogar promedio del top 0,1 %, el aporte es el 0,17 % de su patrimonio (B18).
3. **ESTIMACIÓN / HIPÓTESIS:** el índice millonarios × brecha de destinos sin visa × visa Schengen solo da positivo en 7 de los 34 mercados con datos de UBS. China lidera con holgura (100), seguida por India (23), Arabia Saudita (6) y Rusia (4) (B31, B40). Sin el indicador Schengen, son 10 mercados (B41). **DATO:** China no reconoce la doble nacionalidad e India retira la ciudadanía a quien adquiere otra (B44, B45, B47). Esos dos mercados suman el 90,9 % del índice (B51), así que su comprador cambiaría de pasaporte en lugar de sumar uno.
4. **Contrapeso, ESTIMACIÓN:** en 24 de esos 34 mercados, que reúnen 44,7 M de los 53,3 M de millonarios de la tabla, el pasaporte argentino no agrega destinos (B39). A un estadounidense le abre solo 7 destinos: China, Brasil, Rusia, Irán, Venezuela, Bielorrusia y Uzbekistán (B43). Además, el pasaporte argentino necesita visa para entrar a EE.UU. (B37).
5. **Contrapeso, DATO:** desde el Reglamento (UE) 2025/2441, que un país del Anexo II tenga un programa de ciudadanía por inversión sin "vínculo genuino" es causal para suspenderle la exención de visa Schengen. Argentina está en ese anexo (B32, B33). Ese mismo argumento le costó a Vanuatu la exención (B34, B35).

---

## 1. EE.UU.: cuántos hogares pueden pagar (SCF)

**Fuente y versión.** **DATO:** la página del SCF dice que el relevamiento 2022 es "the most recent survey conducted" (B01). `scfp2025s.zip` devuelve 404: el **SCF 2025 todavía no salió** al 03/10/2026. Por eso se usa el summary extract `scfp2022s.zip` (`rscfp2022.dta`, 22.975 registros = 4.595 hogares × 5 réplicas).

**Tratamiento de las 5 réplicas (implicates).** En el extract, la suma de `wgt` por réplica da 26,26 M y la suma sobre las 22.975 filas da 131,3 M, que es el total de hogares de EE.UU. O sea, **el peso ya viene dividido por 5**. El método fue el siguiente: en cada réplica se usa `wgt × 5`, porque cada réplica representa a toda la población; se estima la cantidad (o la mediana) y se promedian las 5 estimaciones, que es el estimador puntual de Rubin. Para totales y proporciones, esto equivale a sumar `wgt` sobre todas las filas. Se informa el rango entre réplicas como medida de la incertidumbre de imputación. No se calcularon errores muestrales con los pesos replicados (`scf2022rw1s.zip`); queda como limitación.

| Umbral (USD de 2022) | Hogares (promedio de réplicas) | % de hogares | Rango entre réplicas | Mediana del tramo | Aporte 350k / mediana | Aporte 500k / mediana |
|---|---|---|---|---|---|---|
| > 1 M | 23,68 M | 18,0 % | 22,89–25,37 M | USD 2,16 M | 16,2 % | 23,2 % |
| > 5 M | 4,81 M | 3,7 % | 4,57–5,03 M | USD 9,33 M | 3,8 % | 5,4 % |
| > 10 M | 2,13 M | 1,6 % | 2,11–2,16 M | USD 15,17 M | 2,3 % | 3,3 % |
| > 30 M | 0,39 M | 0,3 % | 0,37–0,42 M | USD 48,5 M | 0,7 % | 1,0 % |

Todo lo de la tabla es **ESTIMACIÓN** (B02–B08; detalle en `data/processed/B_scf_umbrales.csv`). Sobre el umbral mismo, el aporte del principal es el 35 % (1 M), el 7 % (5 M) y el 3,5 % (10 M).

**Qué significa "sin esfuerzo".** Es una **HIPÓTESIS** de definición: que el aporte no supere un porcentaje dado del patrimonio (`B_scf_capacidad_pago.csv`):

| Criterio | Principal (USD 350k) | Familia tipo (USD 500k) |
|---|---|---|
| Aporte ≤ 10 % del patrimonio neto | 6,91 M hogares (≥ 3,5 M) | 4,81 M (≥ 5 M) |
| Aporte ≤ 5 % del patrimonio neto | 3,37 M (≥ 7 M) (B09) | 2,13 M (≥ 10 M) (B09) |
| Aporte ≤ 1 % del patrimonio neto | 329 mil (≥ 35 M) (B10) | 185 mil (≥ 50 M) (B10) |
| Liquidez: aporte ≤ 10 % de los activos financieros | 3,48 M (B11) | 2,35 M (B11) |

**Advertencias.** (i) El SCF **excluye por diseño a la lista Forbes 400** y cubre mal la cola extrema. Para esa cola se usa el DFA (sección 2). (ii) Las cifras están en dólares de 2022. Entre 2022 y 2026 la riqueza del top creció (el top 0,1 % pasó del 13,1 % al 15,0 % del total según el DFA), así que en 2026 los conteos probablemente sean mayores (**HIPÓTESIS**). (iii) La unidad es el hogar, mientras que UBS y Altrata cuentan individuos adultos. Aun así, el orden de magnitud coincide: UBS estima 4,12 M de adultos estadounidenses con USD 5–100 M (B23, **DATO**), contra 4,81 M de hogares > USD 5 M en el SCF 2022.

## 2. Cola superior: Distributional Financial Accounts

Los archivos de `dfa.zip` son del 15/09/2026 y el último trimestre es el 2T-2026. Serie completa 1989:T3–2026:T2 en `data/processed/B_dfa_top.csv`; gráfico `B_dfa_top`.

| 2T-2026 | Patrimonio neto | Hogares | Participación | Promedio por hogar | Aporte 350k / promedio |
|---|---|---|---|---|---|
| Top 0,1 % | USD 27,87 billones (B12) | 136.779 (B13) | 15,0 % (B16) | USD 204 M | 0,17 % (B18) |
| Resto del top 1 % (p99–p99,9) | USD 32,45 billones (B14) | 1.214.225 (B14) | 17,5 % | USD 26,7 M | 1,31 % (B18) |
| Top 1 % (suma) | USD 60,31 billones (B15) | 1.351.004 | 32,5 % (B15) | — | — |

**DATO:** el DFA solo publica el corte mínimo de patrimonio en los trimestres con SCF. El último es el 3T-2022: USD 45,8 M para entrar al top 0,1 % y USD 11,0 M para el top 1 % (B17). La participación del top 0,1 % subió del 8,6 % (1989:T3) al 15,0 % (B19, B16).

**DATO, contraste privado (Altrata, PDF de descarga directa sin registro):** 206.880 individuos estadounidenses con ≥ USD 30 M, con un patrimonio conjunto de USD 23,8 billones (B25), sobre 556.850 en el mundo (B26).

## 3. Millonarios por país (UBS Global Wealth Report 2026)

**DATO:** el PDF de la edición 2026 se descarga sin registro. En el HTML de la página **no hay enlace a un databook** con todos los mercados. La tabla "The UBS Millionaire Index" (p. 22) publica el número de millonarios en USD de **34 de los 56 mercados** de la muestra (B22). Quedan fuera, entre otros, Canadá, Dinamarca, Noruega, Austria, Nueva Zelanda, Chile, Colombia y Uruguay. **Argentina no forma parte de la muestra de UBS** (0 menciones en el PDF). EE.UU. tiene 23,627 M (B20) de los ≈ 57,5 M de la muestra (B21); China continental, 5,305 M, e India, 944 mil (B24). Los 34 valores, verificados uno por uno contra el texto del PDF, están en `data/processed/B_ubs_millonarios.csv`.

Altrata (WUWR 2026) sí se pudo usar porque el PDF tiene enlace de descarga directa. Knight Frank (The Wealth Report 2026) **exige un formulario** para dar el enlace de descarga (B27): no se usó.

## 4. Hipótesis del comprador no estadounidense

**Todo este apartado es HIPÓTESIS / ESTIMACIÓN. El índice es una heurística de dónde el pasaporte argentino agregaría movilidad; no mide demanda.**

**Destinos sin visa: por qué no Henley.** **DATO:** los términos de henleyglobal.com prohíben "any robot, spider, scraper, or other automated means to access the website for any purpose" (B28), y el aviso legal prohíbe reproducir contenido sin permiso escrito (B29). Por eso **no se usó la API `api.henleypassportindex.com`**, aunque el probe la había encontrado operativa. Como alternativa abierta se usó **Passport Index Data** (`imorte/passport-index-data`, licencia MIT, actualizado al 17/02/2026, compilado de passportindex.org). Es una matriz de 199 × 199 con el requisito de entrada para cada par. Se cuenta como "sin visa previa" un número de días, `visa free`, `visa on arrival` o `eta`, definición análoga a la de Henley. Con esta fuente, el pasaporte argentino llega a **148 de 198 destinos** (B36, **ESTIMACIÓN**). La cifra no es comparable con el puntaje de Henley, que usa otra metodología y otra fecha. **DATO, licencia de la fuente original:** passportindex.org sigue devolviendo 403 anti-bots, así que se revisó en la Wayback Machine. No publica términos de uso ni licencia de datos: no hay ninguna página de términos, legal o privacidad entre unas 66 mil URLs archivadas de `www.` y `discover.passportindex.org`. Su única nota legal (página About, captura del 03/07/2026) lo define como "a free tool, built with publicly available information" y aclara que "Analytics is based on proprietary research" (B52). No hay entonces una prohibición expresa de reutilización como la de Henley, pero tampoco una licencia: la licencia MIT cubre la compilación de GitHub, no necesariamente los datos de origen. La fuente sigue siendo R con esa advertencia. **Conflicto de interés a declarar:** el sitio pertenece a Arton Capital ("Invented and empowered by Arton Capital") y promociona la segunda ciudadanía (B52), igual que Henley. Los requisitos de visado son hechos públicos, pero la compilación viene de un actor de la industria.

**Visa Schengen.** **DATO:** se usa el Reglamento (UE) 2018/1806, versión consolidada al **30/12/2025**, que es la vigente según EUR-Lex al 03/10/2026 (B30). El indicador vale 1 si el país está en el Anexo I. La pertenencia se verifica en el texto consolidado y los países UE/AELC, que no figuran en ningún anexo, valen 0. De los 34 mercados de UBS, están en el Anexo I China, India, Arabia Saudita, Rusia, Sudáfrica, Turquía y Qatar (B31). Argentina está en el Anexo II (B32). **DATO, novedades de 2026:** la ficha EUR-Lex registra una sola modificación posterior al 30/12/2025. Es la suspensión del art. 4(1) por el Reglamento de Ejecución (UE) 2026/496, del 06/03/2026 al 06/03/2027 (B53). Ese reglamento suspende la exención de visa para los pasaportes diplomáticos, de servicio y oficiales de Georgia, con base en el art. 8e(1), que agregó el Reg. 2025/2441 (B54). Los anexos no cambiaron, así que el indicador S sigue igual. El dato importa por otro motivo: el paquete de suspensión de 2025 ya se está aplicando (en este caso, por leyes georgianas que el reglamento considera contrarias a los derechos fundamentales, no por un programa CBI).

**Variantes calculadas** (`data/processed/B_indice_mercados.csv`; M = millonarios en miles; Δ⁺ = max(0, destinos_ARG − destinos_país); S = 1{Anexo I}):

| Variante | Fórmula |
|---|---|
| I1 (base, la pedida) | M × Δ⁺ × S |
| I2 (sin Schengen) | M × Δ⁺ |
| I3 / I4 (log) | ln(millonarios) × ln(1 + Δ⁺), con y sin S |
| I5 (doble nacionalidad) | M × \|destinos_ARG \ destinos_país\|: lo que suma el pasaporte argentino a quien conserva el propio |
| I6 (cola alta) | adultos con USD 5–100 M (UBS p. 32, 15 mercados) × Δ⁺ × S |

**Ranking (máximo = 100).** Hay **10 mercados con Δ⁺ > 0**, no 15. El resto del ranking de 15 vale cero.

| # | Mercado | Millonarios (miles) | Destinos sin visa | Δ vs ARG (148) | Visa Schengen | I1 | I2 | I4 (log) | I5 | Nacionalidad de origen al adquirir otra |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | China (cont.) | 5.305 | 77 | +71 | sí | 100 | 100 | 100 | 100 | pierde o no reconocida (B44–B46) |
| 2 | India | 944 | 55 | +93 | sí | 23,3 | 23,3 | 94,4 | 21,8 | pierde; puede pedir OCI (B47, B48) |
| 3 | Arabia Saudita | 348 | 86 | +62 | sí | 5,7 | 5,7 | 79,8 | 5,8 | no verificado |
| 4 | Rusia | 447 | 114 | +34 | sí | 4,0 | 4,0 | 69,9 | 4,7 | conserva (B49) |
| 5 | Sudáfrica | 97 | 94 | +54 | sí | 1,4 | 1,4 | 69,5 | 1,4 | no verificado |
| 6 | Turquía | 93 | 111 | +37 | sí | 0,9 | 0,9 | 62,8 | 1,1 | no verificado |
| 7 | Qatar | 30 | 105 | +43 | sí | 0,3 | 0,3 | 58,9 | 0,4 | retiro discrecional (B50) |
| 8 | Taiwán | 772 | 113 | +35 | no | 0 | 7,2 | 73,4 | 7,6 | no verificado |
| 9 | México | 333 | 136 | +12 | no | 0 | 1,1 | 49,3 | 1,0 | no verificado |
| 10 | Israel | 195 | 140 | +8 | no | 0 | 0,4 | 40,4 | 0,8 | no verificado |
| — | EE.UU. | 23.627 | 153 | −5 | no | 0 | 0 | 0 | 39,5 | no verificado |

Lectura (**HIPÓTESIS**). El índice base lo domina China por escala. Con logaritmos, India, Arabia Saudita, Taiwán y Rusia quedan cerca de China. La variante de doble nacionalidad (I5) pone a EE.UU. en segundo lugar solo por la cantidad de millonarios, porque la ganancia real es de 7 destinos (B43). I6 solo da positivo para China, porque los otros 14 mercados con datos de 5–100 M no tienen Δ⁺ > 0 con visa Schengen.

**Qué cambia con la doble nacionalidad (DATO + ESTIMACIÓN).** China e India, los dos primeros del ranking, no admiten conservar la nacionalidad de origen:
- **China.** La Ley de Nacionalidad "does not recognize dual nationality for any Chinese national" (art. 3, B44). El nacional radicado en el exterior que adquiere otra nacionalidad "shall automatically lose Chinese nationality" (art. 9, B45). La ley, de 1980, figura vigente y sin reformas en la base oficial del NPC (B46). Matiz: la pérdida automática del art. 9 exige estar radicado en el exterior. Para un comprador que sigue viviendo en China, la ley no prevé esa pérdida, pero China tampoco reconoce la nacionalidad argentina (art. 3) y lo sigue tratando como chino.
- **India.** El ciudadano que adquiere voluntariamente otra ciudadanía deja de ser ciudadano indio "upon such acquisition" (Citizenship Act 1955, s. 9(1), B47). La pérdida se atenúa con la tarjeta Overseas Citizen of India, a la que puede acceder quien fue ciudadano indio (s. 7A, B48). La OCI no es ciudadanía.
- **Rusia** permite conservar la nacionalidad: adquirir otra no extingue la rusa, aunque Rusia trata al doble nacional solo como ruso (Ley 138-FZ, art. 10, B49). **Qatar** puede retirarla por decisión del Emir (art. 11.5; pérdida discrecional, no automática, B50). **Arabia Saudita, Sudáfrica y Turquía: no verificado** (ver Fuentes fallidas).

Consecuencias: (i) el índice base I1 **no se anula**. Su Δ⁺ compara los dos pasaportes como sustitutos, que es justamente la situación de quien pierde el suyo. (ii) En cambio, la variante I5, que supone que el comprador conserva su pasaporte, **no es válida para China ni para India**. (iii) China e India suman el **90,9 % del índice I1** (B51, ESTIMACIÓN). Para ese comprador, el costo real no es solo el aporte: también renuncia (India) o se expone a perder o a ver desconocida (China) la nacionalidad de origen, con sus derechos de residencia, trabajo y propiedad. **HIPÓTESIS:** eso reduce la demanda efectiva de los dos mercados que más pesan en el índice. Entre los mercados con I1 > 0 y doble nacionalidad verificada, solo Rusia conserva la nacionalidad de origen, y es justamente el mercado expuesto a sanciones y a los controles del Decreto 524/2025 (A15).

## 5. Contrapesos

**Para quién el pasaporte argentino no agrega nada** (**ESTIMACIÓN**):
- 45 de los otros 198 pasaportes tienen igual o más destinos sin visa que el argentino (B38).
- En 24 de los 34 mercados de UBS, que reúnen 44,7 M de 53,3 M de millonarios (84 %), la brecha es ≤ 0 (B39). Son EE.UU., toda la UE, Suiza, el Reino Unido, Japón, Corea, Australia, Singapur, Hong Kong, Emiratos y Brasil.
- Al estadounidense, que es el mercado más rico, el pasaporte argentino le suma 7 destinos: China (30 días), Brasil, Rusia, Irán, Venezuela, Bielorrusia y Uzbekistán (B43). No le da nada en Europa.
- **DATO:** el pasaporte argentino **requiere visa para EE.UU. y Canadá** (B37). Para un comprador chino o indio, el acceso a EE.UU. no cambia.

**Evidencia sobre el motivo de compra (movilidad u otros).**
- **DATO:** la evidencia oficial más directa es la del caso Vanuatu. La UE constató que su programa permitía a nacionales de países con visa "obtaining visa-free access to the Union" (B34). Constató también que la mayoría de los solicitantes exitosos de 2022–2023 venía de países con visa; en 2023, China 519 y Rusia 237 (B35). Ese patrón de origen es **compatible** con el motivo de movilidad, pero **no prueba** el motivo: nadie relevó las razones de los compradores.
- **HIPÓTESIS (sin dato):** no se encontró una fuente primaria ni privada con metodología pública que releve los motivos de los compradores de CBI, como movilidad, plan B político, impuestos, educación o residencia. Henley, que publica encuestas sobre esto, quedó excluido por sus términos. Por lo tanto, que los compradores elijan por movilidad sigue siendo una **HIPÓTESIS no verificada**. Para el comprador estadounidense, el motivo de movilidad prácticamente no aplica (B43). Si existe demanda estadounidense, tendría que explicarse por otros motivos (plan B, residencia, afinidad).
- **DATO, riesgo regulatorio que contradice la tesis:** desde el Reg. (UE) 2025/2441, el art. 8 del 2018/1806 incluye como causal de suspensión de la exención de visa "the operation, by a third country listed in Annex II, of an investor citizenship scheme … without that person having any genuine link to that third country" (B33). El DNU 366/2025 permite naturalizar "cualquiera sea el tiempo de su residencia" (A09). **HIPÓTESIS:** precisamente el activo que el índice pone en valor, el acceso Schengen para nacionales de países del Anexo I, es lo que podría poner en riesgo la exención de visa de **todos** los argentinos.
- **DATO (verificado el 03/10/2026):** China no reconoce la doble nacionalidad y la pierde automáticamente quien, radicado en el exterior, adquiere otra (B44, B45). India retira la ciudadanía a quien adquiere voluntariamente otra (B47). Los dos mercados que encabezan el índice, con el 90,9 % de I1 (B51), son entonces de comprador "sustituto", no "acumulador". Detalle en la sección 4.
- **HIPÓTESIS:** para compradores rusos, los controles de SIDE/UIF que prevé el Decreto 524/2025 (A15) y el entorno de sanciones pueden reducir la demanda efectiva.

## Fuentes

| Fuente | Tipo | URL |
|---|---|---|
| Federal Reserve, SCF (página índice) | P | https://www.federalreserve.gov/econres/scfindex.htm |
| Federal Reserve, SCF 2022 summary extract (Stata) | P | https://www.federalreserve.gov/econres/files/scfp2022s.zip |
| Federal Reserve, Distributional Financial Accounts | P | https://www.federalreserve.gov/releases/z1/dataviz/download/zips/dfa.zip |
| UBS, Global Wealth Report 2026 (PDF) | R | https://www.ubs.com/global/en/wealthmanagement/insights/global-wealth-report.html (enlace "gwr-2026-digital.pdf") |
| Altrata, World Ultra Wealth Report 2026 (PDF) | R | https://altrata.com/wp-content/uploads/2026/06/Altrata_World-Ultra-Wealth-Report-2026_FINAL.pdf |
| Knight Frank, página de The Wealth Report (solo para documentar el formulario) | R | https://www.knightfrank.com/wealthreport |
| Henley & Partners, Terms of Use y Disclaimer (solo para documentar la exclusión) | R | https://www.henleyglobal.com/terms-of-use · https://www.henleyglobal.com/disclaimer |
| Passport Index Data (MIT, 17/02/2026; datos de passportindex.org) | R | https://github.com/imorte/passport-index-data (`passport-index-tidy-iso3.csv`, README, LICENSE) |
| EUR-Lex, Reglamento (UE) 2018/1806, ficha y versión consolidada 30/12/2025 | P | https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32018R1806 · https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02018R1806-20251230 |
| Reglamento (UE) 2025/11 (Vanuatu), Oficina de Publicaciones (Cellar) | P | https://publications.europa.eu/resource/celex/32025R0011 |
| Reglamento de Ejecución (UE) 2026/496 (Georgia, pasaportes diplomáticos), Oficina de Publicaciones (Cellar) | P | https://publications.europa.eu/resource/celex/32026R0496 |
| NPC, Nationality Law of the People's Republic of China (inglés), captura Wayback del 07/08/2026 | P | https://web.archive.org/web/20260807035519id_/http://www.npc.gov.cn/zgrdw/englishnpc/Law/2007-12/13/content_1384056.htm |
| NPC, Base Nacional de Leyes y Reglamentos, ficha de 中华人民共和国国籍法 (JSON de la API pública del sitio) | P | https://flk.npc.gov.cn/law-search/search/flfgDetails?bbbs=2c909fdd678bf17901678bf5aba10073 |
| Ministry of Home Affairs (India), The Citizenship Act, 1955 (PDF actualizado al 02/01/2025), captura Wayback del 10/11/2025 | P | https://web.archive.org/web/20251110012137id_/https://www.mha.gov.in/sites/default/files/2025-01/CitizenshipAct1955_02012025.pdf |
| Presidencia de Rusia, Ley Federal 138-FZ (28/04/2023) "Sobre la ciudadanía", p. 1 | P | http://www.kremlin.ru/acts/bank/49216/page/1 |
| Al Meezan (portal legal oficial de Qatar), Ley 38/2005, art. 11 | P | https://www.almeezan.qa/LawArticles.aspx?LawArticleID=39318&LawId=2591&language=en |
| passportindex.org, página About ("Legal notes"), captura Wayback del 03/07/2026 | R | https://web.archive.org/web/20260703044038id_/https://www.passportindex.org/about.php |

## Fuentes fallidas

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

## Limitaciones

- El SCF 2022 está en dólares de 2022 y tiene cuatro años de antigüedad; no se calcularon errores muestrales (pesos replicados) y excluye a los Forbes 400. Hogares ≠ individuos.
- "Sin esfuerzo" es una definición arbitraria (≤ 10 %, 5 % o 1 % del patrimonio). El patrimonio neto incluye activos ilíquidos; la variante con activos financieros es una aproximación a la liquidez.
- El índice usa solo los 34 mercados con número de millonarios publicado. Excluye a Argentina y a vecinos como Chile, Colombia y Uruguay, y a Canadá, entre otros. No pondera la calidad de los destinos: no es lo mismo Schengen que un país pequeño.
- La matriz de visados es una compilación privada (passportindex.org, de Arton Capital, vía un dataset MIT) de febrero de 2026, sin verificación contra cada país de destino y sin licencia explícita de la fuente original (B52). No es comparable con el puntaje de Henley. La cobertura Schengen sí está verificada contra la fuente primaria.
- La doble nacionalidad está verificada solo para China, India, Rusia y Qatar. Arabia Saudita, Sudáfrica, Turquía, Taiwán, México e Israel quedan sin verificar. Para Rusia se usó el texto publicado en 2023, sin revisar reformas posteriores.
- No hay datos sobre los motivos de los compradores de CBI. La relación entre movilidad y demanda es una **HIPÓTESIS**.
- La versión consolidada del 2018/1806 es al 30/12/2025. La única novedad de 2026 que registra la ficha EUR-Lex es la suspensión para los pasaportes diplomáticos de Georgia (B53, B54), que no toca los anexos.
