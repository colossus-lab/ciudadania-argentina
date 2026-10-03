# Resumen ejecutivo

El 02/10/2026 el Ministerio de Economía anunció el Programa de Ciudadanía por Inversión (CBI). Este estudio pregunta cuatro cosas: si la base legal resiste, quién podría comprar, cuánto aportaría y si el "momento Argentina" que lo justifica se sostiene con datos.

## Las respuestas, en una línea cada una

| Pregunta | Respuesta | Etiqueta |
|---|---|---|
| ¿Cuánto cuesta? | USD 350.000 de aporte o USD 800.000 en un bono. Una familia tipo paga USD 500.000. Las solicitudes se reciben desde el 4T-2026 (A01–A06) | DATO |
| ¿Tiene base legal firme? | **No.** El DNU 366/2025 no fija montos: delega en Economía qué inversión es "relevante". Al 03/10/2026 no hay ninguna norma publicada con los montos anunciados, y la Cámara Nacional Electoral declaró nulo el DNU el 30/06/2026 (A10, A17, A18, A20) | DATO |
| ¿Es caro o barato? | Es el programa verificado más caro: 1,4–1,5 veces la donación caribeña, o 2,0–2,2 veces para una familia. A cambio ofrece un pasaporte con más destinos sin visa que cualquier programa caribeño (C80–C83) | ESTIMACIÓN |
| ¿Quién podría comprarlo? | En EE.UU., 4,8 M de hogares superan USD 5 M de patrimonio, y para ellos el aporte es menos del 4% (B03–B07). Pero a un estadounidense el pasaporte argentino le abre solo 7 destinos nuevos. La ganancia de movilidad se concentra en China, India, Rusia y los países del Golfo (B31–B43) | ESTIMACIÓN / HIPÓTESIS |
| ¿Cuánto recaudaría? | Con 1.000 solicitantes por año, unos USD 345 M (el 2,9% de los vencimientos externos de 2027). Para igualar a los cinco programas del Caribe juntos (USD 492 M/año) harían falta unos 1.430 solicitantes por año (G04–G06, C90) | ESCENARIO |
| ¿Argentina está "de moda" desde Qatar? | **Parcialmente.** Hubo un escalón de atención que en Wikipedia ya se disipó y en Google persiste moderado. El turismo desde EE.UU. creció menos que el resto de Sudamérica (E07–E15, E32) | ESTIMACIÓN |
| ¿Se busca el pasaporte argentino? | **Sí, y cada vez más.** En EE.UU., "argentina passport" pasó de un índice promedio de 2 a 4 (2021–2024) a 32,5 en 2026. El anuncio generó un pico mundial inmediato, y "argentina citizenship by investment program" fue la búsqueda relacionada de mayor ascenso (+1.300%) (E50–E64) | DATO / ESTIMACIÓN |
| ¿Es un "refugio austral"? | **Solo en recursos.** Argentina lidera en alimentos, litio y energía, pero queda última de seis comparables en todos los indicadores de instituciones, paz y estabilidad macro (F001–F122) | DATO / HIPÓTESIS |
| ¿Ayuda a entrar sin visa a EE.UU.? | Hoy no: el pasaporte argentino necesita visa para EE.UU. En 2025 se firmó una declaración de intención para el reingreso al Visa Waiver Program (D28). La CBI puede jugar en contra, porque EE.UU. sacó a Argentina en 2002 cuestionando la integridad de sus documentos (D27) | DATO / HIPÓTESIS |

## Los tres riesgos que más pesan

1. **Riesgo judicial (DATO).** La Cámara Nacional Electoral resolvió "declarar nulo el decreto de necesidad y urgencia N° 366/2025" porque la ciudadanía es materia electoral, vedada a los DNU (A18). El Juzgado Federal de Esquel declaró inconstitucional el art. 37, que es justamente el que crea la vía por inversión (A20). **HIPÓTESIS:** como el control judicial argentino vale para cada caso, cada carta de ciudadanía por inversión queda expuesta a impugnación hasta que haya una ley del Congreso o un fallo de la Corte Suprema.
2. **Riesgo regulatorio externo (DATO).** El Reglamento (UE) 2025/2441 convirtió la CBI "sin vínculo genuino" en causal de suspensión de la exención de visa Schengen, y Argentina figura en el Anexo II (B32–B33). Vanuatu ya la perdió por ese motivo, y EE.UU. restringió la entrada de nacionales de Antigua y Dominica por su CBI sin residencia (C50–C57). Lo que estaría en juego es el acceso Schengen de **todos** los argentinos.
3. **Riesgo de expectativas (ESCENARIO).** Ni el escenario más alto (3.000 solicitantes por año, USD 1.350 M) cubre más del 11% de los vencimientos de capital externo de 2027. Esa cifra es, además, más del doble de lo que recauda todo el Caribe junto.

## Qué no se pudo verificar
- La tasa de rechazo de visas B de EE.UU. para Argentina en FY2025: la copia de archivo no fue accesible desde el entorno (Módulo D).
- El dictamen de la Comisión Bicameral sobre el DNU 366/2025, y si la causa "Yang" llegó a la Corte Suprema.
- El resultado de Argentina en el Mundial 2026: no se asume.
- Si China e India permiten la doble nacionalidad, de lo que depende el ranking de mercados (Módulo B).
- Los montos de Dominica, Vanuatu, Jordania y Egipto (Módulo C).

## Cómo leer este informe
Cada afirmación lleva un código (A01, B31…) que remite a `docs/claims_ledger.csv`. Ahí figuran la fuente, el archivo local, su hash y la cita literal o el localizador. `src/09_auditoria.py` verifica cada cita contra la copia descargada; el resultado está en `docs/auditoria.csv`.
