# Módulo C — Benchmark de programas de ciudadanía por inversión

**Resumen (5 líneas)**
1. **DATO:** En el Caribe Oriental la donación mínima vigente está entre USD 200.000 y 250.000 y cubre a una familia de hasta 4 personas (Dominica pide USD 250.000 para la familia). Dominica cobra USD 200.000 (EDF), Antigua 230.000 (NDF), Granada 235.000 (NTF), Santa Lucía 240.000 (NEF) y St Kitts 250.000 (SISC), todas vigentes desde junio–agosto de 2024. Vanuatu cobra USD 130.000 (DSP) y Nauru 105.000, rebajados a 90.000 durante 2026. Turquía y Jordania no tienen donación: Turquía pide un inmueble de USD 400.000 o una inversión de 500.000; Jordania, un proyecto productivo de JOD 500.000–700.000 con empleo o acciones por JOD 1.000.000 (C01–C17, C91–C99).
2. **ESTIMACIÓN:** el aporte argentino (USD 350.000) cuesta entre 1,40 y 1,75 veces la donación caribeña, y la familia tipo (USD 500.000) entre 2,0 y 2,2 veces. Solo Jordania, por la vía de acciones (≈ USD 1,41 M), pide más que el bono argentino (USD 800.000). A cambio, el pasaporte argentino llega a más destinos sin visa que todos salvo Malta: 148, contra 123–136 en el Caribe y 111 en Turquía (C80–C83, C99, A01–A05, B36).
3. **ESTIMACIÓN:** el CBI llegó a recaudar el 38% del PBI en Dominica (año fiscal 2022) y el 26% en St Kitts (2022). Los cinco programas caribeños juntos recaudaron unos USD 2.460 M de ingreso fiscal en 2020–2024, unos USD 490 M por año, ≈1.400 aportes argentinos por año (C84–C90). Según los Article IV 2026, en 2025 la recaudación cae a ≈ USD 420 M (≈1.200 aportes; C77); con la serie revisada, 2021–2025 promedia ≈ USD 545 M por año (C78).
4. **DATO — contrapeso:** la UE suspendió y después eliminó la exención de visado Schengen de Vanuatu por su CBI (2022 → 2025). En 2025 hizo del CBI sin vínculo genuino una causal general de suspensión (Reg. 2025/2441, que cita lavado de dinero y corrupción), y en diciembre de 2025 la Comisión señaló a los cinco programas caribeños por sus volúmenes y bajas tasas de rechazo (C28). El TJUE declaró ilegal el programa maltés (C-181/23), y Malta lo derogó. EE.UU. restringió la entrada de nacionales de Antigua y Dominica por su "CBI sin residencia" (C50–C57, C18–C19).
5. **DATO + HIPÓTESIS — dependencia fiscal:** el ingreso CBI de St Kitts cayó de 22% a 8% del PBI en un año tras endurecer controles, y el de Vanuatu de ~14% a 5,4% tras perder la exención Schengen. El FMI vincula la dependencia del CBI a la menor presión tributaria de la región (C21, C22, C26). **HIPÓTESIS:** un programa argentino quedaría expuesto a los mismos instrumentos (el pasaporte argentino figura en el Anexo II de la UE, B32–B33), con el agravante de que lo que está en juego es una exención de visado más valiosa.

---

## 1. Montos mínimos vigentes (solo fuente gubernamental)

Archivo: `data/processed/C_montos_minimos.csv`. Gráfico: `outputs/charts/C_montos_minimos.{png,svg}`.

| País | Vía | Tipo | Mínimo principal (USD) | Familia tipo (USD) | Vigencia | Claim |
|---|---|---|---:|---:|---|---|
| **Argentina** | Aporte al Tesoro | Donación | **350.000** | **500.000** | Anuncio 02/10/2026 (sin norma, A17) | A01, A05 |
| **Argentina** | Título público | Bono | **800.000** | — | Anuncio 02/10/2026 | A02 |
| St Kitts y Nevis | SISC | Donación a fondo | 250.000 | 250.000 (hasta 4 personas) | SRO 20/2024 (8/7/2024) | C01, C02 |
| St Kitts y Nevis | Desarrollo inmobiliario aprobado | Inmobiliario | 325.000 | — | SRO 43/2024 (25/10/2024) | C03 |
| Antigua y Barbuda | NDF | Donación a fondo | 230.000 | 230.000 (hasta 4; tasas aparte) | S.I. 2024 No. 50 (oferta previa vencida 31/7/2024) | C04, C05* |
| Antigua y Barbuda | Inmueble aprobado | Inmobiliario | 300.000 | — | Web oficial | C06 |
| Granada | NTF | Donación a fondo | 235.000 | 235.000 (principal + 3) | SRO 15/2024, vigente 1/7/2024 | C07 |
| Granada | Unidad en proyecto aprobado (cuota) / proyecto | Inmobiliario | 270.000 / 350.000 | — | SRO 15/2024 | C09 |
| Santa Lucía | NEF | Donación a fondo | 240.000 | 240.000 (principal + 3) | S.I. 106/2024, vigente 1/7/2024 | C10, C11 |
| Turquía | Inmueble (3 años sin vender) | Inmobiliario | 400.000 | n/p | Reglamento 2010/139 art. 20 (mod. 2022) | C14 |
| Turquía | Capital fijo / depósito / bonos del Estado | Inversión / bono | 500.000 | n/p | Ídem | C15 |
| Nauru | ECRCP (oferta 2026) | Donación a fondo | 90.000 (regular 105.000) | n/p | Oferta desde 3/2/2026 hasta 31/12/2026 | C16, C17 |
| Dominica | EDF | Donación a fondo | 200.000 | 250.000 (principal + 3) | S.R.O. 8/2024 (gaceta 28/6/2024); la S.R.O. 46/2025 no toca los montos | C91, C92, C94* |
| Dominica | Inmueble en proyecto aprobado | Inmobiliario | 200.000 (+ tasa de gobierno desde 75.000) | — | S.R.O. 8/2024, Schedule 1, párr. 2 | C92, C93 |
| Vanuatu | DSP (tasas mandadas por el Gobierno) | Donación a fondo | 130.000 | 180.000 (matrimonio + 2 hijos) | Regulation Order 33/2019; web oficial (consulta 04/10/2026) | C95, C96* |
| Jordania | Proyecto productivo nuevo fuera de Amán (10 empleos; pasaporte temporal 3 años) | Inversión | ≈ 705.000 (JOD 500.000) | n/p | Decisión del Consejo de Ministros 4375 (2/7/2025) | C97*, C98, C99 |
| Jordania | Acciones nuevas en empresas jordanas (3 años) | Inversión | ≈ 1.410.000 (JOD 1.000.000) | n/p | Ídem | C97*, C98, C99 |
| Egipto | Decreto PM 876/2023 | Varios | **no verificado** | — | — | — |
| Malta | MEIN | — | **derogado** | — | Act XXI 2025 (24/7/2025) | C18, C19, C56 |

n/p = la fuente no publica el monto familiar. *C05, C94 y C96 son **lecturas visuales** de PDF escaneados sin capa de texto; C97 combina una lectura visual del árabe con fragmentos literales del texto extraído (pdfplumber invierte el orden de los caracteres). Ver Limitaciones. Los montos de Jordania están en dinares; la conversión a USD (0,709 JOD/USD, C98) es ESTIMACIÓN (C99).

- **DATO:** en Santa Lucía, el S.I. 57/2026 (23/3/2026) limita a 1.500 por año las solicitudes aprobadas (C27). Es el primer cupo explícito del Caribe.
- **DATO:** St Kitts llevó en julio de 2023 la opción en efectivo de USD 125.000 a 250.000 (C24). Según el FMI, los cinco países firmaron en marzo de 2024 un Memorando de Acuerdo con un piso de USD 200.000 (C20). **Dominica cobra exactamente ese piso:** USD 200.000 para un solicitante y 250.000 para una familia de hasta 4 (EDF), o un inmueble de USD 200.000 más una tasa de gobierno desde USD 75.000 (C91–C93).
- **DATO:** en Vanuatu, la Oficina de Ciudadanía fija para el DSP una contribución mínima al Gobierno de USD 80.000 y un precio mínimo de venta de USD 130.000 (USD 180.000 para matrimonio con 2 hijos), más USD 5.000 de debida diligencia (C95, C96). Es el programa por donación más barato del benchmark después de Nauru.
- **DATO:** Jordania no tiene donación ni depósito: desde la decisión 4375 (2/7/2025) la nacionalidad requiere acciones nuevas por JOD 1.000.000 o un proyecto productivo con empleo para jordanos (JOD 700.000 en Amán con 20 empleos; JOD 500.000 fuera de Amán con 10 empleos), con un pasaporte temporal de 3 años antes de la nacionalidad (C97). En USD: ≈ 705.000 y ≈ 1.410.000 (ESTIMACIÓN, C99).
- **Malta (tras el TJUE):** la sentencia C-181/23 (29/4/2025) declaró que el programa de "naturalización por servicios excepcionales por inversión directa" incumplía el art. 20 TFUE y el art. 4.3 TUE (C56). La Act XXI de 2025 eliminó la figura "individual investor programme" y reemplazó el art. 10(9) por una naturalización "por mérito" (C18, C19). **No hay hoy monto de inversión vigente en Malta.**

## 2. Recaudación CBI en USD y % del PBI (FMI)

Archivo: `data/processed/C_recaudacion_cbi.csv`. Gráfico: `outputs/charts/C_recaudacion_pbi.{png,svg}`.

**Método:**
- **Extracción.** Cada fila se extrae con pdfplumber de la tabla del Article IV, en la página indicada. La cita literal de la fila (rótulo + valores) queda en el ledger.
- **Conversión a USD (ESTIMACIÓN).** Se usa la fila en USD cuando el FMI la publica (Dominica, 2020–2024). Si no, se convierte desde EC$ a la paridad fija de 2,70 (C42), o se multiplica el % del PBI por el PBI en EC$ de la misma tabla.
- **% del PBI (ESTIMACIÓN).** Es USD / PBI nominal de la API DataMapper (NGDPD, C70–C75). El % que publica el FMI va al lado como DATO para validar: las diferencias son menores a 2 puntos.
- **Dos conceptos.** "Ingreso fiscal" (lo que entra al presupuesto) y "flujo BdP" (entradas totales CBI en balanza de pagos, incluido lo inmobiliario). Para Vanuatu solo hay el segundo.

| País | Pico (% PBI, DataMapper) | 2024 (est. FMI) | 2025 (informes 2026) | Acumulado fiscal 2020–2024 (USD M) | 2025 (USD M) | Claims |
|---|---|---|---|---:|---:|---|
| Dominica (año fiscal jul–jun) | 38,1% (FY2022) | 31,5% | 28,4% (FY2025/26, proyección) | ≈1.007 | ≈211 | C30–C35, C63, C84 |
| St Kitts y Nevis | 25,8% (2022) | 8,6% | 5,3% (est.) | ≈869 | ≈57 | C36–C39, C64–C65, C85 |
| Granada (ingreso fiscal) | 12,4% (2024) | 12,4% | 4,6% (est.) | ≈354 | ≈65 | C43–C45, C67, C87 |
| Granada (flujo BdP) | 32,1% (2024) | 32,1% | — | — | — | C44 |
| Antigua y Barbuda | 2,6% (2020) | 1,3% | 2,6% (est.) | ≈146 | ≈58 | C40–C41, C66, C86 |
| Santa Lucía (año fiscal abr–mar) | 1,0% (FY2022) | 0,8% | 1,0% (FY2025/26, proyección) | ≈86 | ≈27 | C46–C47, C68–C69, C88 |
| Vanuatu (ECP, BdP) | 12,2% (2020) | 2,7% | — (ingreso fiscal ECP: 5,4% previsto, C76) | ≈411 | — | C48–C49, C76, C89 |

Los porcentajes de 2025 son USD / PBI DataMapper; se verifican al correr el script (ver `C_recaudacion_cbi.csv`).

- **ESTIMACIÓN:** los cinco programas caribeños suman ≈ USD 2.460 M de ingreso fiscal en 2020–2024 (≈ USD 490 M por año), unos 1.400 aportes argentinos por año (C90). Esto sirve para dimensionar los escenarios del Módulo G: el techo de G (3.000 solicitantes por año) duplica lo que recauda hoy todo el Caribe.
- **2025 (Article IV 2026, ESTIMACIÓN):** con los informes publicados entre enero y junio de 2026 (St Kitts CR 26/93, Dominica CR 26/117, Antigua CR 26/97, Granada CR 26/9, Santa Lucía CR 26/3; C63–C69) el ingreso fiscal CBI de los cinco caribeños baja a ≈ USD 419 M en 2025, ≈ 1.200 aportes argentinos (C77). Por país: Dominica 211 (proyección del ejercicio 2025/26), Granada 65, Antigua 58, St Kitts 57 (5,3% del PBI, desde 8,6% en 2024 y ≈ 26% en 2022) y Santa Lucía 27 (proyección). Es el nivel más bajo desde 2020.
- **Revisión de la serie (ESTIMACIÓN):** los informes 2026 revisan hacia arriba 2021–2024 (≈ +7%), sobre todo por Granada, cuya nueva fila "Government CBI revenue" incluye la donación al NTF también antes de 2023, y por Dominica 2024. Con esa vintage, 2021–2025 suma ≈ USD 2.716 M, ≈ USD 543 M por año (C78). **C90 no cambia** (sigue midiendo 2020–2024 con los informes 2025), pero el Módulo G debería tener presente que el promedio anual ronda USD 490–545 M según la vintage, y que el último año observado (2025) es ≈ USD 420 M.
- **Vanuatu, ingreso fiscal del ECP (CR 25/277):** 11,2% del PBI en 2021, 5,3% en 2023 y 5,4% previsto para 2025 (C76). Es un concepto distinto del flujo de balanza de pagos que usa el gráfico (C48).
- **DATO:** el FMI proyecta que el ingreso CBI regional baje de 7% del PBI de la ECCU (2024) a 4% (2029) (C23).
- **Comparabilidad:** en Santa Lucía y Antigua el ingreso que llega al presupuesto es chico (≈1–2,6% del PBI) porque el grueso va a fondos fuera del presupuesto (NEF) o a inversión inmobiliaria. En Granada, hasta 2022 la donación al NTF se registraba como "grants" y no como ingreso CBI (nota 1/ de la tabla del FMI): la serie fiscal subestima los años previos a 2023, y el flujo BdP es la medida comparable.

## 3. Casos regulatorios (fuente primaria)

Archivo: `data/processed/C_casos_regulatorios.csv`.

| Fecha | Caso | Hecho (DATO) | Claim |
|---|---|---|---|
| 03/03/2022 | Vanuatu | Decisión (UE) 2022/366: suspensión parcial del acuerdo de exención de visados (pasaportes emitidos desde el 25/5/2015) | C50 |
| 31/05/2024 | Vanuatu | Reg. Delegado (UE) 2024/2059: prorroga la suspensión total del 4/8/2024 al 3/2/2025. El CBI sigue sin exigir residencia | C51 |
| 19/12/2024 (DOUE 14/1/2025) | Vanuatu | Reg. (UE) 2025/11: Vanuatu pasa al Anexo I (visa obligatoria). En 2023 la mayoría de los solicitantes venía de China (519) y Rusia (237) | C52, C53 (y B34–B35) |
| 26/11/2025 (DOUE 10/12/2025) | UE, mecanismo de suspensión | Reg. (UE) 2025/2441: nueva causal (e), operar un CBI "sin vínculo genuino". El considerando 7 cita lavado de dinero y corrupción | C54, C55 (y B33) |
| 29/04/2025 | Malta | TJUE C-181/23, parte resolutiva: Malta incumplió el art. 20 TFUE y el art. 4.3 TUE; condena en costas | C56 |
| 24/07/2025 | Malta | Act XXI 2025: se elimina el "individual investor programme" y se pasa a la naturalización por mérito | C18, C19 |
| 16/12/2025 (FR 19/12/2025) | EE.UU. → Antigua y Dominica | Proclamación presidencial: suspende visas de inmigrante y B, F, M y J para ambos países, porque "has historically had CBI without residency" | C57, C58 |
| 06/10/2023 | Portugal | Lei 56/2023, art. 42: no admite nuevos pedidos de autorización de residencia para inversión de las subalíneas I, III y IV (incluida la inmobiliaria) | C60 |
| 02/01/2025 (BOE 3/1/2025) | España | LO 1/2025, DF 21.ª: **deja sin contenido los arts. 63–67 de la Ley 14/2013**. Elimina toda la residencia para inversores, no solo la inmobiliaria. Vigencia general a los 3 meses | C59 |
| 17/02/2022 | Reino Unido | Cierre de la ruta Tier 1 (Investor) "over security concerns". Daba "opportunities for corrupt elites" | C61 |
| 15/02/2023 | Irlanda | Cierre del Immigrant Investor Programme, que había aprobado ≈ €1.252 M | C62 |
| 19/12/2025 | UE → Caribe Oriental | Octavo informe del mecanismo de suspensión de visados (IP/25/3061): los CBI de los cinco Estados del Caribe Oriental "continue to raise concerns" por altos volúmenes, plazos cortos y bajas tasas de rechazo | C28 |

**Presión de la UE en 2026 (sigue sin verificar en fuente primaria):** según la prensa, la Comisión pidió por carta (25/6/2026) a los cinco países caribeños eliminar su CBI hasta el 1/6/2028, bajo amenaza de aplicarles el Reg. 2025/2441. El 04/10/2026 se buscó en el press corner de la Comisión (API de búsqueda: "citizenship by investment", "investor citizenship", "Eastern Caribbean", "Saint Kitts", "Antigua", "Dominica", "Grenada", "golden passports", "visa suspension mechanism"): no hay comunicado sobre la carta. Las piezas de 2026 que aparecen (estrategia de visados y su Q&A del 29/1/2026, QANDA/26/218; suspensión para pasaportes diplomáticos de Georgia, IP/26/564) no la mencionan. La CIU de Antigua tampoco publicó nada en cip.gov.ag. La carta queda como **S**, solo para fechar. Lo verificable es el antecedente de diciembre de 2025 (C28): la Comisión ya señalaba a los cinco programas en su informe anual.

## 4. Posicionamiento de Argentina

Archivo: `data/processed/C_posicionamiento.csv`.

| País | Donación mínima (USD) | Familia tipo (USD) | Destinos sin visa (Módulo B) | Aporte AR / donación | USD por destino sin visa |
|---|---:|---:|---:|---:|---:|
| Argentina | 350.000 | 500.000 | 148 | 1,00 | 2.365 |
| St Kitts y Nevis | 250.000 | 250.000 | 136 | 1,40 | 1.838 |
| Santa Lucía | 240.000 | 240.000 | 125 | 1,46 | 1.920 |
| Granada | 235.000 | 235.000 | 128 | 1,49 | 1.836 |
| Antigua y Barbuda | 230.000 | 230.000 | 132 | 1,52 | 1.742 |
| Dominica | 200.000 | 250.000 | 123 | 1,75 | 1.626 |
| Vanuatu | 130.000 | 180.000 | 80 | 2,69 | 1.625 |
| Nauru | 90.000 | — | 73 | 3,89 | 1.233 |
| Turquía | (inmueble 400.000) | — | 111 | — | — |
| Jordania | (proyecto ≈ 705.000; acciones ≈ 1.410.000) | — | 49 | — | — |
| Malta (derogado) | — | — | 159 | — | — |
| Egipto | no verif. | — | 48 | — | — |

- **ESTIMACIÓN:** Argentina es el programa por donación **más caro** del benchmark: su aporte cuesta entre 1,40 y 1,75 veces la donación de los cinco caribeños y 2,7 veces la de Vanuatu; la familia tipo, entre 2,0 y 2,2 veces (C80, C81). En cambio, ofrece el **mejor pasaporte** del grupo vigente: 148 destinos frente a 136 del mejor caribeño. Aun así, por destino sin visa resulta ≈ 23–45% más caro que el Caribe (USD 2.365 contra 1.626–1.920; C82, C83).
- **ESTIMACIÓN:** el bono argentino (USD 800.000) **ya no es el umbral más alto** del benchmark: Jordania pide JOD 1.000.000 (≈ USD 1,41 M) en acciones, aunque su vía más barata para un inversor nuevo (JOD 500.000, ≈ USD 705.000 fuera de Amán) queda por debajo del bono (C97, C99). Jordania no ofrece donación: exige inversión productiva con empleo.
- **HIPÓTESIS:** el diferencial de precio solo se justifica si el comprador valora atributos que el conteo de destinos no captura (un país grande, residencia efectiva posible, Mercosur). Esa tesis la evalúa el Módulo B. Por monto, Argentina compite con las vías inmobiliarias de Turquía y St Kitts, no con las donaciones caribeñas.

## 5. Contrapesos (riesgos para un programa nuevo)

1. **Pérdida de exenciones de visado (DATO).** El caso Vanuatu muestra la secuencia completa: suspensión parcial (2022), suspensión total (2023–2025) y paso al Anexo I (2025) (C50–C52). Desde el 30/12/2025, el Reg. 2025/2441 permite suspender a **cualquier** país del Anexo II que opere un CBI sin vínculo genuino (C54), y Argentina está en el Anexo II (B32, B33). **HIPÓTESIS:** el esquema anunciado (sin requisito de residencia, A09) encaja en la definición de la causal (e).
2. **Objeciones de la UE y EE.UU. (DATO).** El TJUE considera "comercialización de la ciudadanía" la naturalización a cambio de pagos predeterminados (C56). EE.UU. restringió visas a Antigua y Dominica citando el CBI sin residencia (C57). Argentina es candidata al Visa Waiver Program (Módulo D), y esa candidatura es el activo más expuesto.
3. **Reputación y lavado (DATO).** El Reg. 2025/2441 cita lavado de dinero y corrupción (C55). El FMI marca al ECP de Vanuatu como "an important risk" en su evaluación de riesgo ALA/CFT (C25), y el Reino Unido cerró el Tier 1 por "corrupt elites" (C61).
4. **Dependencia y volatilidad fiscal (DATO + ESTIMACIÓN).** St Kitts pasó de 22% a 8% del PBI en un año (C21). Vanuatu pasó de ~14% a 5,4% en tres años (C26). Según el FMI, la dependencia del CBI frenó la recaudación tributaria (C22), y el FMI proyecta que el CBI regional siga bajando (C23).
5. **Tendencia de cierre (DATO).** Entre 2022 y 2025 cerraron sus visas o ciudadanías por inversión el Reino Unido, Irlanda, Portugal (vía inmobiliaria), España (todas las vías) y Malta (C18, C59–C62). El programa argentino se lanza a contramano de esa tendencia.

## Fuentes

| Fuente | Tipo | URL |
|---|---|---|
| St Kitts y Nevis CIU: SISC, Real Estate, Government Notices; SRO 20/2024 y 43/2024 | P | https://ciu.gov.kn/ |
| Antigua y Barbuda CIU: NDF, Real Estate, S.I. 2024 No. 50, declaración del 19/12/2025 | P | https://cip.gov.ag/ |
| Granada, SRO 15/2024 (Laws of Grenada) | P | https://www.laws.gov.gd/index.php/s-r-o/1527-sr-o-15-of-2024-grenada-citizenship-by-investment-amendment-no-2-regulations/download |
| Santa Lucía CIU: web; S.I. 106/2024 y 57/2026 | P | https://www.cipsaintlucia.com/citizenship-legislation |
| Turquía, Reglamento 2010/139 (texto consolidado) | P | https://www.mevzuat.gov.tr/MevzuatMetin/21.5.2010139.pdf |
| Nauru ECRCP: Contribution y Factsheet 03/2025 | P | https://www.ecrcp.gov.nr/contribution |
| Dominica CBIU: EDF, Real Estate, S.R.O. 8/2024 y S.R.O. 46/2025 | P | https://www.cbiu.gov.dm/investment-options/ (PDF en https://www.cbiu.gov.dm/dominica-citizenship/legislation/) |
| Vanuatu, Citizenship Office and Commission: Fees and Charges; directiva "Enforcement of Government Prescribed Fees" (30/4/2020) | P | https://vancitizenship.gov.vu/index.php/citizenship/fees-and-charges |
| Jordania, Ministerio de Inversión: mecanismo de la decisión del Consejo de Ministros 4375 (2/7/2025) — copia Wayback | P | https://web.archive.org/web/20251008223025id_/https://moin.gov.jo/ebv4.0/root_storage/ar/eb_list_page/… (URL completa en `src/03_benchmark.py`) |
| Banco Central de Jordania, Working Paper sobre el tipo de cambio fijo (paridad JOD 0,709) — copia Wayback | P | https://web.archive.org/web/20250711035218id_/https://www.cbj.gov.jo/EBV4.0/Root_Storage/AR/The_Case_of_a_Hard-Pegged_Exchange_Rate_Regime.pdf |
| Comisión Europea, IP/25/3061 (octavo informe del mecanismo de suspensión de visados), vía API del press corner | P | https://ec.europa.eu/commission/presscorner/detail/en/ip_25_3061 |
| FMI Article IV 2026: St Kitts CR 26/93, Dominica CR 26/117, Antigua CR 26/97, Granada CR 26/9, Santa Lucía CR 26/3; Vanuatu 2025 CR 25/277 | P | https://www.imf.org/-/media/files/publications/cr/2026/english/ (p. ej. 1knaea2026001-source-pdf.pdf) |
| Malta, Act XXI of 2025 | P | https://legislation.mt/eli/act/2025/21/eng/pdf |
| FMI Article IV: Dominica CR 25/130 y 22/40; St Kitts CR 25/107 y 22/351; Antigua CR 25/96; Granada CR 25/39; Santa Lucía CR 25/65; Vanuatu CR 24/278 | P | https://www.imf.org/-/media/Files/Publications/CR/… (enlaces directos en `src/03_benchmark.py`) |
| FMI DataMapper, NGDPD | P | https://www.imf.org/external/datamapper/api/v1/NGDPD/DMA/KNA/ATG/GRD/LCA/VUT |
| UE: Decisión 2022/366; Reg. Delegado 2024/2059; Reg. 2025/11; Reg. 2025/2441 (Oficina de Publicaciones) | P | https://publications.europa.eu/resource/celex/32025R2441 (y CELEX 32022D0366, 32024R2059, 32025R0011) |
| TJUE C-181/23, sentencia de 29/04/2025 (CELEX 62023CJ0181, ES) | P | https://publications.europa.eu/resource/celex/62023CJ0181 |
| EE.UU., Federal Register 2025-23570 (proclamación del 16/12/2025) | P | https://www.govinfo.gov/content/pkg/FR-2025-12-19/pdf/2025-23570.pdf |
| España, BOE-A-2025-76 (LO 1/2025) | P | https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-76 |
| Portugal, Lei 56/2023 (texto consolidado, Portal das Finanças) | P | https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/legislacao/diplomas_legislativos/Documents/Lei_56_2023.pdf |
| Reino Unido, Home Office (gov.uk) | P | https://www.gov.uk/government/news/tier-1-investor-visa-route-closes-over-security-concerns |
| Irlanda, Immigration Service Delivery | P | https://www.irishimmigration.ie/minister-harris-announces-closure-of-the-immigrant-investor-programme/ |
| Destinos sin visa (Passport Index Data, vía Módulo B) | R | data/processed/B_pasaportes_destinos.csv |
| Prensa (fechado de la carta de la Comisión de junio de 2026; monto de Egipto; nota de Ahram Online reproducida por el SIS egipcio, 15/9/2023) | S | No se usa como origen de cifras |

## Fuentes fallidas

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

## Limitaciones

- **Lecturas visuales (C05, C94, C96, C97):** el S.I. 2024 No. 50 de Antigua (C05), la S.R.O. 46/2025 de Dominica (C94) y la directiva DSP de Vanuatu (C96) son PDF escaneados sin capa de texto (no hay OCR en el entorno); la cita va entre corchetes y `quote()` no puede verificarla. Los montos de Antigua, Dominica y Vanuatu sí están verificados de forma literal en las webs oficiales y en la S.R.O. 8/2024 (C04, C91–C93, C95). En Jordania (C97) el PDF tiene texto, pero pdfplumber invierte el orden de los caracteres árabes: la cita combina una lectura visual en árabe con fragmentos literales del texto extraído, que sí se verifican.
- **Jordania:** la copia es de la Wayback Machine (08/10/2025); moin.gov.jo no respondió el 04/10/2026. Los montos están en dinares; la conversión a USD usa la paridad 0,709 (C98) y es ESTIMACIÓN. La vía por proyecto exige además empleo (10–20 jordanos) y un pasaporte temporal de 3 años antes de la nacionalidad, así que no es comparable 1:1 con una donación.
- **Vanuatu:** la tabla de la web oficial no nombra el programa, pero sus montos coinciden con el "precio mínimo de venta" del DSP fijado por la Regulation Order 33/2019 (C96). La contribución que efectivamente recibe el Gobierno es menor (USD 80.000 para un solicitante).
- **Egipto** sigue sin monto: no se reemplazó con cifras de prensa ni de agentes. La regla de fuente gubernamental tiene una excepción parcial: para Nauru la fuente es el sitio oficial del programa (ecrcp.gov.nr, dominio del gobierno).
- **Serie de recaudación:** 2020–2024 sale de los Article IV 2025 (C30–C49) y 2025 de los Article IV 2026 (C63–C69): St Kitts, Antigua y Granada estiman 2025; Dominica y Santa Lucía lo proyectan (ejercicio 2025/26). Los informes 2026 revisan 2021–2024 (≈ +7%, sobre todo Granada); esas revisiones están en C78 pero no reemplazan la serie publicada (C90 queda estable). St Kitts no tiene datos de 2018–2019. Antigua y Santa Lucía arrancan en 2020. Las cifras en USD salvo Dominica son ESTIMACIÓN (paridad EC$ 2,70). Dominica y Santa Lucía usan año fiscal y se dividen por el PBI calendario del año de inicio. En Granada hay un quiebre contable en 2023 (NTF registrado como "grants" antes) en la serie de los informes 2025. El PBI de St Kitts 2015–2017 viene de un Article IV anterior a la revisión de 2021 de sus cuentas nacionales. En el Article IV 2025 de Vanuatu (CR 25/277) la tabla rotula 2024 como pronóstico.
- **Turquía:** el texto consolidado atribuye los montos de 400.000 y 500.000 al C.K. 5072 (RG 31711, 6/1/2022), con un cambio de redacción de la letra b) por el C.K. 5554 (RG 31834, 13/5/2022). Turquía no publica un monto para la familia.
- **Nauru:** el monto de USD 90.000 es una oferta por tiempo limitado (solicitudes hasta el 31/12/2026). El regular es USD 105.000.
- **Passport Index Data** es de tipo R (vía Módulo B): un conteo propio de destinos, no el Henley.
- **Montos argentinos:** todavía no tienen norma publicada (A17). El ratio de precios supone que el anuncio se mantiene.

## Archivos
- `src/03_benchmark.py` genera `data/processed/C_montos_minimos.csv`, `C_recaudacion_cbi.csv`, `C_casos_regulatorios.csv`, `C_posicionamiento.csv`, `C_fuentes_fallidas.csv`, `outputs/charts/C_montos_minimos.{png,svg}`, `outputs/charts/C_recaudacion_pbi.{png,svg}` y `docs/claims/claims_C.csv` (94 afirmaciones).
