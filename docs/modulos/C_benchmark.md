# Módulo C — Benchmark de programas de ciudadanía por inversión

**Resumen (5 líneas)**
1. **DATO:** En el Caribe Oriental la donación mínima vigente está entre USD 230.000 y 250.000 y cubre a una familia de hasta 4 personas. Antigua cobra USD 230.000 (NDF), Granada 235.000 (NTF), Santa Lucía 240.000 (NEF) y St Kitts 250.000 (SISC), todas vigentes desde julio–agosto de 2024. Nauru cobra USD 105.000, rebajados a 90.000 durante 2026. Turquía no tiene donación: pide un inmueble de USD 400.000 o una inversión, depósito o bono de USD 500.000 (C01–C17).
2. **ESTIMACIÓN:** el aporte argentino (USD 350.000) cuesta entre 1,40 y 1,52 veces la donación caribeña, y la familia tipo (USD 500.000) entre 2,0 y 2,2 veces. Ningún programa del benchmark con monto verificado pide más que el bono argentino (USD 800.000). A cambio, el pasaporte argentino llega a más destinos sin visa que todos salvo Malta: 148, contra 123–136 en el Caribe y 111 en Turquía (C80–C83, A01–A05, B36).
3. **ESTIMACIÓN:** el CBI llegó a recaudar el 38% del PBI en Dominica (año fiscal 2022) y el 26% en St Kitts (2022). Los cinco programas caribeños juntos recaudaron unos USD 2.460 M de ingreso fiscal en 2020–2024, unos USD 490 M por año. Eso equivale a ≈1.400 aportes argentinos por año (C84–C90).
4. **DATO — contrapeso:** la UE suspendió y después eliminó la exención de visado Schengen de Vanuatu por su CBI (2022 → 2025). En 2025 hizo del CBI sin vínculo genuino una causal general de suspensión (Reg. 2025/2441, que cita lavado de dinero y corrupción). El TJUE declaró ilegal el programa maltés (C-181/23), y Malta lo derogó. EE.UU. restringió la entrada de nacionales de Antigua y Dominica por su "CBI sin residencia" (C50–C57, C18–C19).
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
| Dominica | EDF | Donación | **no verificado** | — | — | (piso regional MoA 2024: USD 200.000, C20) |
| Vanuatu | DSP | Donación | **no verificado** | — | — | — |
| Egipto | Decreto PM 876/2023 | Varios | **no verificado** | — | — | — |
| Jordania | Criterios del Consejo de Ministros | Depósito / bono / inversión | **no verificado** | — | — | — |
| Malta | MEIN | — | **derogado** | — | Act XXI 2025 (24/7/2025) | C18, C19, C56 |

n/p = la fuente no publica el monto familiar. *C05 es una **lectura visual** de un PDF escaneado sin capa de texto (ver Limitaciones).

- **DATO:** en Santa Lucía, el S.I. 57/2026 (23/3/2026) limita a 1.500 por año las solicitudes aprobadas (C27). Es el primer cupo explícito del Caribe.
- **DATO:** St Kitts llevó en julio de 2023 la opción en efectivo de USD 125.000 a 250.000 (C24). Según el FMI, los cinco países firmaron en marzo de 2024 un Memorando de Acuerdo con un piso de USD 200.000 (C20).
- **Malta (tras el TJUE):** la sentencia C-181/23 (29/4/2025) declaró que el programa de "naturalización por servicios excepcionales por inversión directa" incumplía el art. 20 TFUE y el art. 4.3 TUE (C56). La Act XXI de 2025 eliminó la figura "individual investor programme" y reemplazó el art. 10(9) por una naturalización "por mérito" (C18, C19). **No hay hoy monto de inversión vigente en Malta.**

## 2. Recaudación CBI en USD y % del PBI (FMI)

Archivo: `data/processed/C_recaudacion_cbi.csv`. Gráfico: `outputs/charts/C_recaudacion_pbi.{png,svg}`.

**Método:**
- **Extracción.** Cada fila se extrae con pdfplumber de la tabla del Article IV, en la página indicada. La cita literal de la fila (rótulo + valores) queda en el ledger.
- **Conversión a USD (ESTIMACIÓN).** Se usa la fila en USD cuando el FMI la publica (Dominica, 2020–2024). Si no, se convierte desde EC$ a la paridad fija de 2,70 (C42), o se multiplica el % del PBI por el PBI en EC$ de la misma tabla.
- **% del PBI (ESTIMACIÓN).** Es USD / PBI nominal de la API DataMapper (NGDPD, C70–C75). El % que publica el FMI va al lado como DATO para validar: las diferencias son menores a 2 puntos.
- **Dos conceptos.** "Ingreso fiscal" (lo que entra al presupuesto) y "flujo BdP" (entradas totales CBI en balanza de pagos, incluido lo inmobiliario). Para Vanuatu solo hay el segundo.

| País | Pico (% PBI, DataMapper) | Último año (2024, est. FMI) | Acumulado fiscal 2020–2024 (USD M) | Claims |
|---|---|---|---:|---|
| Dominica (año fiscal jul–jun) | 38,1% (FY2022) | 31,5% | ≈1.007 | C30–C35, C84 |
| St Kitts y Nevis | 25,8% (2022) | 8,6% | ≈869 | C36–C39, C85 |
| Granada (ingreso fiscal) | 12,4% (2024) | 12,4% | ≈354 | C43–C45, C87 |
| Granada (flujo BdP) | 32,1% (2024) | 32,1% | — | C44 |
| Antigua y Barbuda | 2,6% (2020) | 1,3% | ≈146 | C40–C41, C86 |
| Santa Lucía (año fiscal abr–mar) | 1,0% (FY2022) | 0,8% | ≈86 | C46–C47, C88 |
| Vanuatu (ECP, BdP) | 12,2% (2020) | 2,7% | ≈411 | C48–C49, C89 |

- **ESTIMACIÓN:** los cinco programas caribeños suman ≈ USD 2.460 M de ingreso fiscal en 2020–2024 (≈ USD 490 M por año), unos 1.400 aportes argentinos por año (C90). Esto sirve para dimensionar los escenarios del Módulo G: el techo de G (3.000 solicitantes por año) duplica lo que recauda hoy todo el Caribe.
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

**Presión de la UE en 2026 (no verificado en fuente primaria):** según la prensa, la Comisión pidió por carta (25/6/2026) a los cinco países caribeños eliminar su CBI hasta el 1/6/2028, bajo amenaza de aplicarles el Reg. 2025/2441. La carta no está publicada, y la CIU de Antigua no publicó ninguna declaración sobre el tema en cip.gov.ag (última actualización relevante: 19/12/2025, sobre EE.UU.). Queda como **S**, solo para fechar.

## 4. Posicionamiento de Argentina

Archivo: `data/processed/C_posicionamiento.csv`.

| País | Donación mínima (USD) | Familia tipo (USD) | Destinos sin visa (Módulo B) | Aporte AR / donación | USD por destino sin visa |
|---|---:|---:|---:|---:|---:|
| Argentina | 350.000 | 500.000 | 148 | 1,00 | 2.365 |
| St Kitts y Nevis | 250.000 | 250.000 | 136 | 1,40 | 1.838 |
| Santa Lucía | 240.000 | 240.000 | 125 | 1,46 | 1.920 |
| Granada | 235.000 | 235.000 | 128 | 1,49 | 1.836 |
| Antigua y Barbuda | 230.000 | 230.000 | 132 | 1,52 | 1.742 |
| Nauru | 90.000 | — | 73 | 3,89 | 1.233 |
| Turquía | (inmueble 400.000) | — | 111 | — | — |
| Malta (derogado) | — | — | 159 | — | — |
| Dominica / Vanuatu / Jordania / Egipto | no verif. | — | 123 / 80 / 49 / 48 | — | — |

- **ESTIMACIÓN:** Argentina es el programa **más caro** del benchmark verificado en donación (+40–52%) y en familia tipo (≈2×) (C80, C81). En cambio, ofrece el **mejor pasaporte** del grupo vigente: 148 destinos frente a 136 del mejor caribeño. Aun así, por destino sin visa resulta ≈25–35% más caro que el Caribe (C82, C83).
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
| Prensa (fechado de la carta de la Comisión de junio de 2026; montos de Egipto, Jordania y Vanuatu) | S | No se usa como origen de cifras |

## Fuentes fallidas

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

## Limitaciones

- **C05 (Antigua, S.I. 2024 No. 50)** es un PDF escaneado sin capa de texto (no hay OCR en el entorno). La cita es una **lectura visual** de las pp. 7 y 9, entre corchetes; `quote()` no puede verificarla, y la auditoría automática la da por "OK" con 0 citas. El monto de USD 230.000 sí está verificado de forma literal en la web oficial (C04).
- **Dominica, Vanuatu, Egipto y Jordania** quedan sin monto: no se reemplazaron con cifras de prensa ni de agentes. La regla de fuente gubernamental tiene una excepción parcial: para Nauru la fuente es el sitio oficial del programa (ecrcp.gov.nr, dominio del gobierno).
- **Serie de recaudación:** los Article IV 2026 no fueron accesibles, así que 2024 es una estimación del FMI y faltan 2025–2026. St Kitts no tiene datos de 2018–2019. Antigua y Santa Lucía arrancan en 2020. Las cifras en USD salvo Dominica 2020–2024 son ESTIMACIÓN (paridad EC$ 2,70). Dominica y Santa Lucía usan año fiscal y se dividen por el PBI calendario del año de inicio. En Granada hay un quiebre contable en 2023 (NTF registrado como "grants" antes). El PBI de St Kitts 2015–2017 viene de un Article IV anterior a la revisión de 2021 de sus cuentas nacionales.
- **Turquía:** el texto consolidado atribuye los montos de 400.000 y 500.000 al C.K. 5072 (RG 31711, 6/1/2022), con un cambio de redacción de la letra b) por el C.K. 5554 (RG 31834, 13/5/2022). Turquía no publica un monto para la familia.
- **Nauru:** el monto de USD 90.000 es una oferta por tiempo limitado (solicitudes hasta el 31/12/2026). El regular es USD 105.000.
- **Passport Index Data** es de tipo R (vía Módulo B): un conteo propio de destinos, no el Henley.
- **Montos argentinos:** todavía no tienen norma publicada (A17). El ratio de precios supone que el anuncio se mantiene.

## Archivos
- `src/03_benchmark.py` genera `data/processed/C_montos_minimos.csv`, `C_recaudacion_cbi.csv`, `C_casos_regulatorios.csv`, `C_posicionamiento.csv`, `C_fuentes_fallidas.csv`, `outputs/charts/C_montos_minimos.{png,svg}`, `outputs/charts/C_recaudacion_pbi.{png,svg}` y `docs/claims/claims_C.csv` (74 afirmaciones).
