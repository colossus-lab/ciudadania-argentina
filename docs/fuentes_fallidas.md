# Fuentes fallidas

Registro de fuentes que no pudieron descargarse o verificarse, con causa y acción. Una falla no se rellena "a ojo":
se documenta y se sigue.

| Fecha | Fuente / host | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | 52 URLs de 39 dominios (primer probe) | varias | `ProxyError` — HTTP 403 al `CONNECT` | Política de red del entorno (no era una falla de las fuentes) | **Resuelto:** red habilitada en un nuevo entorno; probe re-corrido (48/55 OK) |
| 2026-10-03 | www.imm.gov.gd (Granada) | https://www.imm.gov.gd/ | Conexión rechazada en el destino | Sitio caído o inexistente | Buscar el programa CBI de Granada en otra fuente gubernamental (Investment Migration Agency) o FMI Art. IV |
| 2026-10-03 | www.imf.org (páginas de país) | https://www.imf.org/en/Countries/DMA | HTTP 403 | Protección anti-bots del sitio (la API DataMapper sí responde) | Usar API DataMapper y PDFs de Article IV vía enlace directo o copia Wayback |
| 2026-10-03 | travel.state.gov | RefusalRates/FY25.pdf, páginas de estadísticas NIV y Report of the Visa Office | HTTP 403 (también con User-Agent de navegador) | Protección anti-bots del sitio | Usar copias de la **Wayback Machine** (archive.org) del mismo PDF oficial; se registra la URL y fecha de captura en `fuentes.md` |
| 2026-10-03 | faostatservices.fao.org (API) | /api/v1/en/... | HTTP 401 | La API nueva exige token | Usar la descarga masiva `bulks-faostat.fao.org` (responde 200) |
| 2026-10-03 | whc.unesco.org | /en/list/xml/ | HTTP 403 | Protección anti-bots | Copia Wayback del XML (captura 2025-07-16) |
| 2026-10-03 | api.bcra.gob.ar v3.0 | /estadisticas/v3.0/monetarias | HTTP 410 Gone | API v3 discontinuada | **Resuelto:** v4.0 responde 200 |
| 2026-10-03 | hcdn.gob.ar / senado.gob.ar / argentina.gob.ar / trade.gov | rutas de bicameral, deuda, I-92 | HTTP 404 | Cambio de URL | **Resuelto:** URLs corregidas en `src/00_probe_fuentes.py` |
