# Fuentes fallidas

| Fecha | Fuente / host | URL | Error | Causa | Acción |
|---|---|---|---|---|---|
| 2026-10-03 | 52 URLs de 39 dominios (ver `docs/probe_fuentes.csv`) | varias | `ProxyError` — HTTP 403 al `CONNECT` | Política de red del entorno de ejecución (no es una falla de la fuente) | Pedido de habilitación de red; reintentar con `src/00_probe_fuentes.py` |
| 2026-10-03 | datos.energia.gob.ar | http://datos.energia.gob.ar/api/3/action/package_search?q=produccion | HTTP 403 (texto plano del proxy) | El proxy del entorno no admite HTTP plano; además, bloqueo de política | Usar `https://` al reintentar |
| 2026-10-03 | www.argentina.gob.ar, www.boletinoficial.gob.ar (vía WebFetch) | anuncio MECON, Dec. 524/2025, 285/2026, ficha DNU 366/2025 | `EGRESS_BLOCKED` | Misma política de red | Idem |
