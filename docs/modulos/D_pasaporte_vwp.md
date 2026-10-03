# Módulo D — Pasaporte argentino y Visa Waiver Program de EE.UU.

**Resumen (5 líneas)**
1. **ESTIMACIÓN (fuente R):** con datos de Passport Index Data (febrero de 2026; no es el Henley), el pasaporte argentino entra sin visa previa a 148 de 198 destinos, puesto 45 de 199. Empata con Chile (148), queda apenas detrás de Brasil (149) y por delante de Uruguay (137) y México (136). Lo que separa a Argentina de Chile es EE.UU. (visa frente a ESTA) y Canadá (visa o eTA condicional frente a eTA) (D60–D68, D41–D43). El Henley no se usó porque sus términos de uso prohíben el acceso automatizado (D01–D02).
2. **DATO:** la ley (8 U.S.C. §1187(c)) dice que el DHS "**may** designate" (puede designar) a un país. Para eso exige una tasa de rechazo de visas de visitante del año fiscal anterior **menor al 3,0%**, o bien un promedio de dos años **menor al 2,0%** con cada año **menor al 2,5%**. Exige además pasaporte electrónico, acuerdo de intercambio de información sobre amenazas, reporte de pasaportes perdidos en 24 h, repatriación en 3 semanas y una evaluación de seguridad del DHS. El 3% es necesario, pero no suficiente (D03–D12, D14–D16).
3. **DATO:** Chile fue nominado por el Departamento de Estado el 03/06/2013, designado el 28/02/2014 y opera en el VWP desde el 31/03/2014; es el único país latinoamericano entre los 42 del programa. Argentina fue miembro entre 1996 y 2002. La sacaron por la crisis y por el uso del programa para quedarse a trabajar; en aquella baja EE.UU. señaló que el proceso para obtener los documentos base del pasaporte "lacks integrity" (carece de integridad) (D18–D19, D23–D27, D44).
4. **DATO:** el 28/07/2025, DHS y el Gobierno argentino firmaron una **declaración de intención** para el reingreso de Argentina al VWP. DHS habla de cumplir los criterios "in the coming years" (en los próximos años). Según DHS/CBP, el overstay de visitantes argentinos fue de 0,81% en FY2024, contra 2,32% de Chile, que ya está en el programa (D28–D33). **No se pudo verificar en fuente primaria la tasa de rechazo de Argentina en FY2025**: web.archive.org cortó todas las conexiones, aunque las 20 capturas FY2006–FY2025 existen y están registradas.
5. **HIPÓTESIS:** la CBI puede jugar en contra de la candidatura. El DHS evalúa la integridad de la identidad de quienes viajan con el pasaporte, y hay antecedentes concretos: FinCEN 2014 sobre St. Kitts (rescindido en 2026), la visa que el Reino Unido impuso a Dominica y Vanuatu en 2023, la UE con Vanuatu (B34) y la observación de 2002 sobre los documentos argentinos. Rumania muestra que una designación ya otorgada puede revocarse por discrecionalidad (D21–D22, D27, D70–D73).

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

## 3. Serie de la tasa de rechazo ajustada de visas B (pregunta 3) — NO OBTENIDA

- travel.state.gov devuelve 403 a clientes automatizados. Con la API de disponibilidad de archive.org (que sí responde) se **ubicaron las 20 capturas FY2006–FY2025** del mismo PDF oficial (`RefusalRates/FY{yy}.pdf`), entre ellas la de FY25.pdf del 2026-05-01 (`20260501063449`). Las URL y timestamps están en `data/processed/D_wayback_capturas.csv` y las respuestas JSON en `data/raw/D_dos_refusal_rates_FY*_wbavail_2026-10-03.json`.
- **La descarga falló:** web.archive.org devolvió `ConnectionResetError` en todos los intentos, del 2026-10-03 13:45 al 14:50 aprox. Un sondeo cada ~90 s dio siempre el mismo resultado. El proxy del entorno informó `ws_closed_mid_exchange` para web.archive.org:443. Otros espejos tampoco sirvieron: Library of Congress Web Archive (desafío Cloudflare), arquivo.pt (403) y archive.ph (reset). Los informes del CRS (crsreports.congress.gov) devolvieron 403.
- **No se rellenó con prensa ni con memoria.** El script está preparado para completar la serie, el CSV `data/processed/D_tasa_rechazo_B.csv`, los claims D45–D52 y el gráfico `D_tasa_rechazo_B_AR_CL` (con la línea del 3% y la designación de Chile) en cuanto web.archive.org responda. Basta con correr `python src/04_pasaporte_vwp.py`.
- Por la misma causa, **la pregunta "¿Argentina está hoy por debajo o por encima del 3%?" queda sin respuesta verificada.** La prensa publica cifras para FY2025, pero son S y no se usan. **HIPÓTESIS:** la frase del DHS del 28/07/2025, "as it works diligently to meet eligibility criteria in the coming years" (D30), sugiere que en ese momento Argentina no cumplía todos los criterios. No dice cuáles.

## 4. Precedente de Chile y candidatura argentina (pregunta 4)

**Chile (DATO, Federal Register 79 FR 17852):**
- nominado por el Secretario de Estado el **03/06/2013** (D24);
- designado el **28/02/2014** (D23);
- regla vigente y viaje VWP desde el **31/03/2014** (D25, D18).

La designación cae en el año fiscal FY2014; los años de referencia para el umbral son FY2012 y FY2013. Sus tasas de rechazo de esos años **no se pudieron extraer** (sección 3).

**Argentina, antecedente (DATO, 67 FR 7943, 21/02/2002):** fue país VWP entre el 08/07/1996 y el 21/02/2002 (D19). La baja se fundó en "the current economic crisis in Argentina and the increase in the number of Argentine nationals attempting to use the program to live and work illegally" (D26). El texto agrega que "the process for obtaining the documents to procure a passport lacks integrity" (D27). Uruguay salió del programa el 15/04/2003 (D20).

**Candidatura actual (fuentes primarias):**

| Fecha | Hecho | Fuente | Claim |
|---|---|---|---|
| 28/07/2025 | DHS (Sec. Noem), Cancillería (Werthein) y Seguridad (Bullrich) firman una declaración de intención "to work toward Argentina's reentry to the Visa Waiver Program" | DHS, comunicado | D28 |
| 28/07/2025 | Presidencia: "firmaron una declaración de intención para el ingreso al Programa de Exención de Visas" | argentina.gob.ar | D31 |
| 28/07/2025 | DHS: "Argentina now has the lowest visa overstay rate in all of Latin America"; el proceso "takes time … in the coming years" | DHS | D29, D30 |

- **S (solo para fechar; no se afirma como hecho):** según la prensa (El Economista, Cadena 3, Los Andes, El Esquiú, mayo de 2026), la ministra de Seguridad, Alejandra Monteoliva, estimó que el beneficio podría estar operativo "en los primeros meses de 2027". No se encontró un comunicado oficial con esa fecha. **No hay en el DHS una nominación ni una designación de Argentina** a la fecha de consulta: la lista vigente del DHS no la incluye (D44: 42 países).

**Overstay (DATO, DHS/CBP Entry/Exit Overstay Reports), un argumento a favor de Argentina:**

| FY | Argentina (B1/B2) | Chile (VWP + B1/B2) | Uruguay | Brasil |
|---|---|---|---|---|
| 2022 | 1,38% (D38) | 2,97% (D39) | — | — |
| 2023 | 0,97% (D36) | 2,62% (D37) | — | — |
| 2024 | 0,81% (D32) | 2,32% (D33) | 1,97% (D34) | 1,25% (D35) |

- El promedio de los países VWP en FY2024 fue 0,49% (D40).
- **ESTIMACIÓN:** el overstay argentino está por debajo del umbral del 2% que el DHS aplica a los miembros, y por debajo del de Chile en los tres años.
- **Advertencia de comparabilidad:** para Chile se usa la Tabla 2 (visitantes VWP y B1/B2); para Argentina, la Tabla 3 (B1/B2 de países no VWP). Gráfico: `outputs/charts/D_overstay_AR_CL.{png,svg}`.

## 5. Visas B1/B2 emitidas a argentinos (pregunta 5) — NO OBTENIDA

Las *NIV Detail Tables* del DoS (p. ej., `FY24NIVDetailTable.xlsx`, captura `20260430115050`; `FY13NIVDetailTable.xls`, captura `20260430115053`) **están archivadas en Wayback**, pero fallaron por el mismo corte de web.archive.org. El script las procesa, con salida en `data/processed/D_visas_B1B2_argentinos.csv`, claims D53–D56 y el gráfico `D_visas_B1B2_argentinos`, cuando la conexión vuelva.

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
   - **HIPÓTESIS, no verificada en fuente primaria en este módulo:** Malta figura en la lista VWP del DHS y tuvo un programa de ciudadanía por inversión (ver Módulo C) sin perder el VWP. Tampoco se verificó en el DHS si alguna evaluación VWP consideró explícitamente un programa CBI.
   - El decreto 524/2025 prevé informes de SIDE, UIF, Seguridad y RENAPER (Módulo A, A15). Eso podría presentarse ante el DHS como mitigación (**HIPÓTESIS**).
4. **ESCENARIO:** si el DHS considerara el CBI como riesgo de identidad, podría pedir condiciones como el intercambio de las listas de naturalizados por inversión o ESTA reforzada, demorar la nominación o, como con Rumania, revertir una designación. No hay fuente primaria que vincule el CBI argentino con el proceso VWP. Es una conjetura que habría que contrastar con el DHS o el Departamento de Estado.

## Método
- `src/04_pasaporte_vwp.py` descarga con `download()`/`get()` de `common.py` y verifica cada cita con `quote()` contra la copia local.
- Wayback: usa la API de disponibilidad (archive.org) y guarda el JSON en data/raw. Descarga con `web.archive.org/web/<ts>id_/<url>`; si web.archive.org no responde, registra la falla por año en vez de reintentar.
- El parser de los PDF de rechazo busca "País NN.NN%" con pdfplumber y descarta el archivo si el título no coincide con el año fiscal.
- Salidas: `data/processed/D_destinos_sin_visa.csv`, `D_requisitos_destinos_clave.csv`, `D_overstay.csv`, `D_wayback_capturas.csv`, `D_tasa_rechazo_B.csv` (vacío por ahora), `D_visas_B1B2_argentinos.csv` (vacío por ahora) y `D_fuentes_fallidas.csv`.

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
| archive.org Wayback availability API (ubicación de capturas DoS) | P (copia de) | https://archive.org/wayback/available |
| Prensa sobre la fecha "primeros meses de 2027" (El Economista, Cadena 3, Los Andes, El Esquiú) | S | p. ej. https://eleconomista.com.ar/politica/estados-unidos-gobierno-revelo-cuando-argentinos-podran-viajar-visa-n95064 |

## Fuentes fallidas

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

## Limitaciones
- **El núcleo cuantitativo del módulo, la serie de rechazo B, no se obtuvo.** Por eso no se puede afirmar si Argentina cumple hoy el umbral del 3%, ni con qué tasa entró Chile.
- El dato de destinos sin visa viene de una compilación privada (R) hecha a partir de passportindex.org, propiedad de una firma de CBI. No equivale al Henley y no tiene serie histórica en este módulo.
- Los overstay de Argentina y de Chile vienen de tablas distintas del informe del DHS (B1/B2 frente a VWP + B1/B2), y el informe cuenta eventos, no personas.
- La frase del DHS sobre "lowest visa overstay rate in all of Latin America" (D29) es una declaración oficial. No se recalculó contra todos los países de la región.
- No se verificó si el DHS ya reactivó la dispensa de hasta 10% de rechazo (D11–D12).
- El vínculo entre el CBI y el VWP es una **HIPÓTESIS**: no hay pronunciamiento del DHS ni del Departamento de Estado sobre el programa argentino.
