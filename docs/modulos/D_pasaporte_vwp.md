# Módulo D — Pasaporte argentino y Visa Waiver Program de EE.UU.

**Resumen (5 líneas)**
1. **ESTIMACIÓN (fuente R):** con datos de Passport Index Data (febrero de 2026; no es el Henley), el pasaporte argentino entra sin visa previa a 148 de 198 destinos, puesto 45 de 199. Empata con Chile (148), queda apenas detrás de Brasil (149) y por delante de Uruguay (137) y México (136). Lo que separa a Argentina de Chile es EE.UU. (visa frente a ESTA) y Canadá (visa o eTA condicional frente a eTA) (D60–D68, D41–D43). El Henley no se usó porque sus términos de uso prohíben el acceso automatizado (D01–D02).
2. **DATO:** la ley (8 U.S.C. §1187(c)) dice que el DHS "**may** designate" (puede designar) a un país. Para eso exige una tasa de rechazo de visas de visitante del año fiscal anterior **menor al 3,0%**, o bien un promedio de dos años **menor al 2,0%** con cada año **menor al 2,5%**. Exige además pasaporte electrónico, acuerdo de intercambio de información sobre amenazas, reporte de pasaportes perdidos en 24 h, repatriación en 3 semanas y una evaluación de seguridad del DHS. El 3% es necesario, pero no suficiente (D03–D12, D14–D16).
3. **DATO:** Chile fue nominado por el Departamento de Estado el 03/06/2013, designado el 28/02/2014 y opera en el VWP desde el 31/03/2014; es el único país latinoamericano entre los 42 del programa. Argentina fue miembro entre 1996 y 2002. La sacaron por la crisis y por el uso del programa para quedarse a trabajar; en aquella baja EE.UU. señaló que el proceso para obtener los documentos base del pasaporte "lacks integrity" (carece de integridad) (D18–D19, D23–D27, D44).
4. **DATO — Argentina hoy NO cumple el umbral de rechazo:** la tasa ajustada de rechazo de visas B fue de **7,47% en FY2025**, 8,90% en FY2024 y 8,21% en FY2023 (D45, D46, D59). Estuvo por debajo del 3% durante once años seguidos (FY2011–FY2021, D52), pero lo superó en FY2022 (3,66%, D58) y desde entonces más que lo duplica. Para cumplir la vía (ii) necesita bajar unos 4,5 puntos (D76). Chile entró con 2,8% (FY2012) y 1,6% (FY2013) (D47–D48); Uruguay ya está por debajo del 3% (2,59% en FY2025, D50).
5. **DATO + HIPÓTESIS:** el 28/07/2025, DHS y el Gobierno argentino firmaron una **declaración de intención** para el reingreso al VWP. DHS habló de cumplir los criterios "in the coming years" (D28–D30), con Argentina en 8,90% en el año fiscal en curso. El overstay argentino (0,81% en FY2024, contra 2,32% de Chile) juega a favor (D32–D33). **HIPÓTESIS:** la CBI puede jugar en contra, por la integridad de la identidad de los portadores (FinCEN 2014, Reino Unido 2023, UE con Vanuatu, la observación de 2002 sobre los documentos argentinos), aunque Malta mantuvo el VWP con su programa (D75). Rumania muestra que una designación puede revocarse por discrecionalidad (D21–D22, D27, D70–D73).

---

## 1. Valor del pasaporte argentino (pregunta 1)

**Henley Passport Index: no se usó.** Los *Terms of Use* de henleyglobal.com (copia del Módulo B, `data/raw/B_henley_terms_of_use_2026-10-03.html`) dicen: *"Use any robot, spider, scraper, or other automated means to access the website for any purpose"* (D01). También prohíben el uso comercial del contenido sin licencia (D02). `henleypassportindex.com` redirige a henleyglobal.com, y la API `api.henleypassportindex.com` no tiene términos propios ni documentación. Por eso no se descargó ningún dato de Henley, y la **serie histórica del puesto argentino en Henley queda sin fuente** (ver Fuentes fallidas).

**Sustituto (tipo R):** Passport Index Data (imorte/passport-index-data, licencia MIT, actualizado al 17/02/2026, compilado a partir de passportindex.org), con la misma definición que el Módulo B (B36). Cuenta como destino sin visa previa cualquier número de días sin visa, "visa free", "visa on arrival" o "eta". El puesto se calcula como 1 + la cantidad de pasaportes con más destinos.

| Pasaporte | Destinos sin visa previa (de 198) | Puesto (de 199) | EE.UU. | Canadá | Claim |
|---|---|---|---|---|---|
| Brasil | 149 | 44 | visa | visa | D63 |
| **Argentina** | **148** | **45** | **visa** | **visa** (eTA condicional según IRCC) | D60, D65, D67 |
| Chile | 148 | 45 | **eta (ESTA/VWP)** | **eta** | D61, D66, D68 |
| Uruguay | 137 | 53 | visa | visa | D62 |
| México | 136 | 54 | visa | visa | D64 |

- **DATO (P, IRCC):** Canadá ubica a Argentina entre los países que requieren visa. Algunos ciudadanos pueden usar eTA si cumplen requisitos, como haber tenido visa canadiense en los últimos 10 años o tener visa de EE.UU. vigente (D41, D43). Chile está en la lista de países que solo necesitan eTA (D42).
- **ESTIMACIÓN:** en cantidad de destinos, el pasaporte argentino ya equivale al chileno. La diferencia práctica está en EE.UU. y Canadá. Para un comprador de CBI, el atractivo diferencial del pasaporte argentino frente al chileno sería, entonces, un eventual reingreso al VWP. Hoy ese reingreso no existe.
- Advertencia: Passport Index Data es una compilación privada (R) hecha a partir de passportindex.org, que pertenece a Arton Capital, una firma que también asesora en CBI. No es el Henley y no se publica como serie histórica. No se reconstruyó serie histórica.

Gráfico: `outputs/charts/D_destinos_sin_visa_AR_comparables.{png,svg}`.

## 2. Requisitos legales del VWP (pregunta 2) — 8 U.S.C. §1187

Texto de Cornell LII; uscode.house.gov estaba en mantenimiento. Citas literales en `docs/claims/claims_D.csv`.

| Requisito | Texto (resumen; cita literal en el claim) | Claim |
|---|---|---|
| Facultad discrecional | "The Secretary of Homeland Security, in consultation with the Secretary of State, **may** designate any country…" | D03 |
| Rechazo, vía (ii) | rechazo del año fiscal completo anterior "less than 3.0 percent" | D04 |
| Rechazo, vía (i) | promedio de dos años "less than 2.0 percent" **y** cada año "less than 2.5 percent" | D05 |
| Pasaporte electrónico | "electronic passport that is fraud-resistant, contains relevant biographic and biometric information" | D06 |
| Seguridad | el DHS "determines that such interests would not be compromised" | D07 |
| Intercambio de información | acuerdo "to share information regarding whether citizens and nationals … represent a threat", "fully implements" | D08 |
| Pasaportes perdidos o robados | reporte "not later than 24 hours" | D09 |
| Repatriación | "not later than three weeks" | D10 |
| Dispensa del 3% (hasta 10% u overstay máximo) | solo tras certificar el sistema de salida aérea. La facultad quedó **suspendida desde el 01/07/2009** hasta esa notificación | D11, D12 |
| Overstay | definido como cociente de *overstays* sobre admitidos con visa (§1187(c)(8)(C)(ii)) | D13 |

Requisitos administrativos del DHS (página oficial):
- tasa de rechazo B "less than three percent" (D14);
- **evaluación independiente de inteligencia** (DHS I&A, por el DNI) para la designación inicial (D15);
- desde 2022, requisito **EBSP** de intercambio de información, con cotejo biométrico, para "current and aspiring VWP countries" (D16);
- desde 2017, los países con overstay ≥2% deben hacer una campaña pública de información (D17).

**Contrapeso (DATO + HIPÓTESIS):** el 3% es una condición *necesaria*, no *suficiente*. La designación es facultativa ("may", D03) y requiere una determinación de seguridad del DHS (D07), la evaluación de inteligencia (D15) y el acuerdo EBSP con cotejo biométrico (D16). El caso de Rumania lo confirma: fue designada el 09/01/2025 y la designación se **rescindió el 02/05/2025** sin implementarse. El motivo invocado fue "this Administration's focus on border and immigration security" (D21, D22). **HIPÓTESIS:** no está verificado si el DHS ya hizo la notificación biométrica que reactivaría la dispensa de hasta 10% (D12). La página del DHS solo menciona el umbral del 3% (D14), así que se trata ese umbral como el vigente.

## 3. Serie de la tasa de rechazo ajustada de visas B (pregunta 3)

**Fuente:** U.S. Department of State, *Adjusted Refusal Rate – B-Visas Only, by Nationality*, un PDF por año fiscal (`RefusalRates/FY{yy}.pdf`). travel.state.gov devuelve 403 a clientes automatizados, así que se usaron las **copias del mismo PDF oficial en la Wayback Machine**: 20 de 20 años (FY2006–FY2025). La URL y el timestamp de cada captura están en `data/processed/D_wayback_capturas.csv`; la serie, con la línea literal de cada PDF, en `data/processed/D_tasa_rechazo_B.csv`. En la primera corrida, web.archive.org no era accesible desde el entorno; el 03/10/2026 se re-corrió el script desde otra red y la serie se completó.

| FY | Argentina | Chile | Uruguay | Brasil |
|---|---|---|---|---|
| 2006 | 6,7% | 7,5% | 12,6% | 13,2% |
| 2008 | 3,1% | 8,9% | 9,5% | 5,5% |
| 2010 | 3,1% | 5,0% | 5,6% | 5,2% |
| 2011 | **2,5%** | 3,4% | 3,8% | 3,8% |
| 2012 | **1,5%** | **2,8%** (D47) | **2,7%** | 3,2% |
| 2013 | **1,7%** | **1,6%** (D48) | **2,8%** | 3,5% |
| 2014 | **1,4%** | **2,4%** | **1,8%** | 3,2% |
| 2016 | **2,14%** | 11,43% | 3,14% | 16,70% |
| 2018 | **1,73%** | 11,34% | 4,11% | 12,73% |
| 2020 | **2,79%** | 11,54% | 9,77% | 23,16% |
| 2021 | **2,31%** (D57) | 13,42% | 8,82% | 14,25% |
| 2022 | 3,66% (D58) | 13,75% | 5,70% | 14,48% |
| 2023 | 8,21% (D59) | 16,12% | 3,21% | 11,94% |
| 2024 | 8,90% (D46) | 20,15% | **2,63%** | 15,48% |
| 2025 | **7,47%** (D45) | 16,38% (D49) | **2,59%** (D50) | 14,87% (D51) |

En negrita, los valores por debajo del 3%. La serie completa, año por año, está en el CSV y en el gráfico `outputs/charts/D_tasa_rechazo_B_AR_CL.{png,svg}`.

- **DATO:** Argentina estuvo por debajo del 3% en 11 de los 20 años disponibles, todos seguidos: FY2011–FY2021 (D52). Lo superó en FY2022 (3,66%) y desde FY2023 está entre 7,5% y 8,9% (D45, D46, D58, D59).
- **ESTIMACIÓN:** para cumplir la vía (ii) del umbral (año fiscal anterior < 3,0%, D04), la tasa argentina tiene que bajar unos **4,5 puntos** desde el 7,47% de FY2025 (D76). La vía (i) (promedio de dos años < 2,0% y cada año < 2,5%, D05) está todavía más lejos. Como la designación usa el año fiscal completo anterior, ningún año fiscal anterior a FY2026 (que cerró el 30/09/2026) habilita hoy la designación.
- **DATO:** en FY2012 el Departamento de Estado empezó a usar "a new calculation methodology" (D74). Los años FY2006–FY2011 no son estrictamente comparables con los posteriores (línea punteada en el gráfico).
- **HIPÓTESIS (lectura de Chile y Brasil):** después de entrar al VWP en 2014, la tasa de Chile mide solo a quienes igual piden visa B (porque no califican para el ESTA o necesitan otra condición). Es un universo residual y más riesgoso: por eso su tasa saltó a 11–20%. No es comparable con la de un país fuera del programa. La suba de Brasil desde FY2016 no tiene esa explicación; no se analizó.
- **HIPÓTESIS (por qué subió la de Argentina):** la suba coincide con la vuelta de la demanda pospandemia (visas emitidas de 32.821 en FY2021 a 273.206 en FY2023, D78, sección 5) y con la crisis macroeconómica de 2022–2023 (Módulo F). Los PDF no informan motivos de rechazo; no se verificó la causa.
- La frase del DHS del 28/07/2025, "as it works diligently to meet eligibility criteria in the coming years" (D30), queda explicada por los datos: en ese momento Argentina venía de 8,21% (FY2023) y 8,90% (FY2024).

## 4. Precedente de Chile y candidatura argentina (pregunta 4)

**Chile (DATO, Federal Register 79 FR 17852):**
- nominado por el Secretario de Estado el **03/06/2013** (D24);
- designado el **28/02/2014** (D23);
- regla vigente y viaje VWP desde el **31/03/2014** (D25, D18).

La designación cae en el año fiscal FY2014; los años de referencia para el umbral son FY2012 y FY2013. Chile tuvo **2,8% en FY2012 y 1,6% en FY2013** (D47, D48): cumplió la vía (ii), con el año previo por debajo del 3%, pero no la vía (i), porque el promedio fue 2,2%. **ESTIMACIÓN:** FY2012 cerró el 30/09/2012; la nominación llegó ocho meses después (03/06/2013) y la designación, nueve meses más tarde (28/02/2014) (D24, D23). Argentina, con 7,47% en FY2025, está hoy más lejos que Chile en 2012.

**Argentina, antecedente (DATO, 67 FR 7943, 21/02/2002):** fue país VWP entre el 08/07/1996 y el 21/02/2002 (D19). La baja se fundó en "the current economic crisis in Argentina and the increase in the number of Argentine nationals attempting to use the program to live and work illegally" (D26). El texto agrega que "the process for obtaining the documents to procure a passport lacks integrity" (D27). Uruguay salió del programa el 15/04/2003 (D20).

**Candidatura actual (fuentes primarias):**

| Fecha | Hecho | Fuente | Claim |
|---|---|---|---|
| 28/07/2025 | DHS (Sec. Noem), Cancillería (Werthein) y Seguridad (Bullrich) firman una declaración de intención "to work toward Argentina's reentry to the Visa Waiver Program" | DHS, comunicado | D28 |
| 28/07/2025 | Presidencia: "firmaron una declaración de intención para el ingreso al Programa de Exención de Visas" | argentina.gob.ar | D31 |
| 28/07/2025 | DHS: "Argentina now has the lowest visa overstay rate in all of Latin America"; el proceso "takes time … in the coming years" | DHS | D29, D30 |

- **S (solo para fechar; no se afirma como hecho):** según la prensa (El Economista, Cadena 3, Los Andes, El Esquiú, mayo de 2026), la ministra de Seguridad, Alejandra Monteoliva, estimó que el beneficio podría estar operativo "en los primeros meses de 2027". No se encontró un comunicado oficial con esa fecha. **No hay en el DHS una nominación ni una designación de Argentina** a la fecha de consulta: la lista vigente del DHS no la incluye (D44: 42 países).
- **HIPÓTESIS:** con 7,47% en FY2025 (D45), una designación a comienzos de 2027 por la vía del umbral exigiría que la tasa de FY2026 (cerrado el 30/09/2026, todavía sin publicar) haya caído por debajo del 3%, una baja de más de 4 puntos en un año. La dispensa de hasta 10% (D11) también la habilitaría, pero está suspendida desde 2009 salvo notificación del DHS (D12), que no se verificó.

**Overstay (DATO, DHS/CBP Entry/Exit Overstay Reports), un argumento a favor de Argentina:**

| FY | Argentina (B1/B2) | Chile (VWP + B1/B2) | Uruguay | Brasil |
|---|---|---|---|---|
| 2022 | 1,38% (D38) | 2,97% (D39) | — | — |
| 2023 | 0,97% (D36) | 2,62% (D37) | — | — |
| 2024 | 0,81% (D32) | 2,32% (D33) | 1,97% (D34) | 1,25% (D35) |

- El promedio de los países VWP en FY2024 fue 0,49% (D40).
- **ESTIMACIÓN:** el overstay argentino está por debajo del umbral del 2% que el DHS aplica a los miembros, y por debajo del de Chile en los tres años.
- **Advertencia de comparabilidad:** para Chile se usa la Tabla 2 (visitantes VWP y B1/B2); para Argentina, la Tabla 3 (B1/B2 de países no VWP). Gráfico: `outputs/charts/D_overstay_AR_CL.{png,svg}`.

## 5. Visas B1/B2 emitidas a argentinos (pregunta 5)

**Fuente:** U.S. Department of State, *Nonimmigrant Visa Detail Tables*, columna B1/B2 (o "B-1,2"), fila Argentina; copias Wayback del xls/xlsx oficial de cada año. Se obtuvieron FY2006–FY2024 (19 años). FY2015–FY2018 se publicaron con otro nombre de archivo (`FY15 NIV Detail Table.xls`); se ubicaron con el índice CDX de la Wayback. **FY2025 todavía no está publicado ni archivado.**

| FY | Visas B1/B2 emitidas | Claim |
|---|---|---|
| 2006 | 81.430 | — |
| 2012 | 249.029 | — |
| 2013 | 240.653 | D53 |
| 2017 | **353.555** (máximo) | D77 |
| 2019 | 212.011 | D54 |
| 2021 | 32.821 (mínimo, pandemia) | D78 |
| 2023 | 273.206 | — |
| 2024 | 272.762 | D55 |

- **ESTIMACIÓN:** la demanda de visas de turismo y negocios de argentinos se multiplicó por 4,3 entre FY2006 y FY2017. Cayó con la crisis de 2018–2019 y la pandemia, y en FY2023–FY2024 volvió a unos 273.000 por año, todavía 23% por debajo del pico. Serie completa en `data/processed/D_visas_B1B2_argentinos.csv`; gráfico `outputs/charts/D_visas_B1B2_argentinos.{png,svg}`.
- **HIPÓTESIS:** el volumen es relevante para el VWP en dos sentidos. Con ~270.000 visas por año, un VWP argentino eliminaría un costo y una espera para muchos viajeros, lo que da peso político a la candidatura. Pero la tasa de rechazo (sección 3) se calcula sobre ese mismo volumen, y hoy está lejos del umbral.

## 6. Contrapeso obligatorio: cómo la CBI puede jugar en CONTRA del VWP — HIPÓTESIS

El mecanismo propuesto es una **HIPÓTESIS**; los hechos de apoyo son **DATO**.
1. **Integridad de identidad.** El VWP exime de la entrevista consular a *todos* los portadores del pasaporte. Una vía de naturalización sin residencia (DNU 366/2025, ver Módulo A) agrega portadores cuya identidad de origen no verificó el Estado argentino con el estándar de un nacional nativo. El DHS evalúa precisamente la seguridad (D07), exige evaluación de inteligencia (D15) y cotejo biométrico EBSP (D16). En 2002, EE.UU. ya había objetado la integridad del proceso para obtener los documentos base del pasaporte argentino (D27).
2. **Precedentes:**
   - FinCEN (2014) advirtió que el CBI de St. Kitts y Nevis "maintains lax controls as to who may be granted citizenship" (D70) y que se usaba para "mask their identity and geographic background" y evadir sanciones (D71).
   - El Reino Unido (2023) impuso visa a Dominica y Vanuatu por "clear and evident abuse" de sus programas CBI (D73).
   - La UE suspendió la exención de visa de Vanuatu (Módulo B, B34).
   - Ninguno de estos casos es una exclusión del VWP: esos países nunca fueron miembros. Lo que muestran es la reacción de terceros Estados frente a pasaportes CBI.
3. **Contrapeso del contrapeso (DATO):**
   - FinCEN **rescindió** el advisory sobre St. Kitts el 24/02/2026 (D72).
   - **DATO:** Malta es país VWP desde el 30/12/2008 y sigue en la lista vigente del DHS (D75). Tuvo un programa de ciudadanía por inversión hasta que lo derogó en 2025, tras la sentencia C-181/23 del TJUE (Módulo C: C18, C19, C56), y nunca perdió el VWP. **No verificado:** si alguna evaluación VWP del DHS consideró explícitamente un programa CBI.
   - El decreto 524/2025 prevé informes de SIDE, UIF, Seguridad y RENAPER (Módulo A, A15). Eso podría presentarse ante el DHS como mitigación (**HIPÓTESIS**).
4. **ESCENARIO:** si el DHS considerara el CBI como riesgo de identidad, podría pedir condiciones como el intercambio de las listas de naturalizados por inversión o ESTA reforzada, demorar la nominación o, como con Rumania, revertir una designación. No hay fuente primaria que vincule el CBI argentino con el proceso VWP. Es una conjetura que habría que contrastar con el DHS o el Departamento de Estado.

## Método
- `src/04_pasaporte_vwp.py` descarga con `download()`/`get()` de `common.py` y verifica cada cita con `quote()` contra la copia local.
- Wayback: usa la API de disponibilidad (archive.org) y, si no devuelve captura, el índice CDX; guarda el JSON en data/raw. Descarga con `web.archive.org/web/<ts>id_/<url>`; si web.archive.org no responde, registra la falla por año en vez de reintentar.
- El parser de los PDF de rechazo busca "País NN.NN%" con pdfplumber, sin distinguir mayúsculas (desde FY2014 los nombres vienen en mayúsculas), y descarta el archivo si el título no coincide con el año fiscal. Cada valor guarda la línea literal del PDF, que se re-verifica con `quote()`.
- El parser de las NIV Detail Tables busca la fila de encabezado con la columna B1/B2 ("B-1,2" hasta FY2021) y toma la fila "Argentina".
- Salidas: `data/processed/D_destinos_sin_visa.csv`, `D_requisitos_destinos_clave.csv`, `D_overstay.csv`, `D_wayback_capturas.csv`, `D_tasa_rechazo_B.csv` (80 filas: 4 países × 20 años), `D_visas_B1B2_argentinos.csv` (19 años) y `D_fuentes_fallidas.csv`.

## Fuentes

| Fuente | Tipo | URL |
|---|---|---|
| 8 U.S.C. §1187 (Cornell LII) | P | https://www.law.cornell.edu/uscode/text/8/1187 |
| DHS — U.S. Visa Waiver Program | P | https://www.dhs.gov/visa-waiver-program |
| Federal Register 79 FR 17852 — Designación de Chile (govinfo) | P | https://www.govinfo.gov/content/pkg/FR-2014-03-31/html/2014-07254.htm |
| Federal Register 67 FR 7943 — Baja de Argentina (govinfo) | P | https://www.govinfo.gov/content/pkg/FR-2002-02-21/html/02-4260.htm |
| Federal Register API (para ubicar los documentos) | P | https://www.federalregister.gov/api/v1/documents.json |
| DHS — comunicado Argentina VWP, 28/07/2025 | P | https://www.dhs.gov/news/2025/07/28/secretary-noem-kickstarts-process-argentina-rejoin-visa-waiver-program |
| Presidencia — declaración de intención, 28/07/2025 | P | https://www.argentina.gob.ar/noticias/argentina-y-estados-unidos-firmaron-una-declaracion-de-intencion-para-el-ingreso-al |
| DHS — rescisión de Rumania, 02/05/2025 | P | https://www.dhs.gov/news/2025/05/02/dhs-announces-rescission-romanias-designation-visa-waiver-program |
| DHS/CBP — Entry/Exit Overstay Report FY2024 | P | https://www.dhs.gov/sites/default/files/2025-08/25_0826_cbp_entry-exit-overstay-report-fiscal-year-2024.pdf |
| DHS/CBP — Entry/Exit Overstay Report FY2023 (incluye FY2022) | P | https://www.dhs.gov/sites/default/files/2024-10/24_1011_CBP-Entry-Exit-Overstay-Report-FY23-Data.pdf |
| IRCC — Entry requirements by country | P | https://www.canada.ca/en/immigration-refugees-citizenship/services/visit-canada/entry-requirements-country.html |
| FinCEN Advisory FIN-2014-A004 | P | https://www.fincen.gov/resources/advisories/fincen-advisory-fin-2014-a004 |
| UK HC 1715 Explanatory Memorandum (19/07/2023) | P | https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1184544/E02946704_-__HC_1715__-_EXPLANATORY_MEMORANDUM__Web_Accessible_.pdf |
| Passport Index Data (MIT; de passportindex.org) — copia del Módulo B | R | https://raw.githubusercontent.com/imorte/passport-index-data/main/passport-index-tidy-iso3.csv |
| Henley & Partners Terms of Use — copia del Módulo B (solo para documentar la prohibición) | R | https://www.henleyglobal.com/terms-of-use |
| U.S. Department of State — Adjusted Refusal Rate, B-Visas Only, FY2006–FY2025 (20 PDF; copias Wayback, ver `D_wayback_capturas.csv`) | P | https://travel.state.gov/content/dam/visas/Statistics/Non-Immigrant-Statistics/RefusalRates/FY25.pdf |
| U.S. Department of State — Nonimmigrant Visa Detail Tables, FY2006–FY2024 (copias Wayback; URL de cada captura en `D_visas_B1B2_argentinos.csv`) | P | https://travel.state.gov/content/dam/visas/Statistics/Non-Immigrant-Statistics/NIVDetailTables/FY24NIVDetailTable.xlsx |
| archive.org Wayback availability API e índice CDX (ubicación de capturas DoS) | P (copia de) | https://archive.org/wayback/available ; https://web.archive.org/cdx/search/cdx |
| Prensa sobre la fecha "primeros meses de 2027" (El Economista, Cadena 3, Los Andes, El Esquiú) | S | p. ej. https://eleconomista.com.ar/politica/estados-unidos-gobierno-revelo-cuando-argentinos-podran-viajar-visa-n95064 |

## Fuentes fallidas

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

## Limitaciones
- La serie de rechazo B viene de copias de archivo (Wayback) del PDF oficial, no de travel.state.gov directo; cada valor se verificó contra la línea literal del PDF archivado. Tiene un quiebre metodológico en FY2012 (D74).
- Las tasas de Chile desde FY2015 no son comparables con las de países fuera del VWP: miden un universo residual (sección 3, HIPÓTESIS).
- No se verificó la causa de la suba de la tasa argentina desde FY2022; los PDF no informan motivos de rechazo.
- El dato de destinos sin visa viene de una compilación privada (R) hecha a partir de passportindex.org, propiedad de una firma de CBI. No equivale al Henley y no tiene serie histórica en este módulo.
- Los overstay de Argentina y de Chile vienen de tablas distintas del informe del DHS (B1/B2 frente a VWP + B1/B2), y el informe cuenta eventos, no personas.
- La frase del DHS sobre "lowest visa overstay rate in all of Latin America" (D29) es una declaración oficial. No se recalculó contra todos los países de la región.
- No se verificó si el DHS ya reactivó la dispensa de hasta 10% de rechazo (D11–D12).
- El vínculo entre el CBI y el VWP es una **HIPÓTESIS**: no hay pronunciamiento del DHS ni del Departamento de Estado sobre el programa argentino.
