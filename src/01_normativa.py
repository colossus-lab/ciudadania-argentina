"""Módulo A — Marco normativo del Programa de Ciudadanía por Inversión.

Descarga normas, sentencias, fichas parlamentarias (Senado, HCDN) y sumarios del Boletín Oficial;
verifica citas textuales contra las copias locales y escribe:
  data/processed/A_cronologia.csv   línea de tiempo normativa y judicial
  docs/claims_ledger.csv            afirmaciones del módulo con su cita literal
"""
from __future__ import annotations

import csv
from pathlib import Path

from common import PROCESSED, RAW, _session, _throttle, download, local_text, quote, raw_path, sha256, write_ledger

GDRIVE = "https://drive.google.com/uc?export=download&id={}"
HCDN_BUSCADOR = "https://www.hcdn.gob.ar/proyectos/resultado.html"

# Fuentes que solo se obtienen enviando un formulario público de búsqueda (POST, sin registro ni captcha).
POST_DATA = {
    "hcdn_366": dict(zezion="true", strTipo="todos", strNumExp="", strNumExpAnio="", strNumExpOrig="", strCamIni="",
                     strFirmante="", strTipoFirmante="", strComision="", strFechaInicio="", strFechaFin="",
                     strPalabras="366/2025", strOrdenDelDiaNro="", strOrdenDelDiaAnio="", strLey="", strCantPagina="100",
                     strMostrarTramites="on", strMostrarDictamenes="on", strMostrarFirmantes="on",
                     strMostrarComisiones="on"),
}


def download_post(url: str, data: dict, name: str, ext: str = "html") -> Path:
    """Como common.download, pero para un formulario de búsqueda público (POST). Reutiliza la copia existente."""
    existing = [p for p in sorted(RAW.glob(f"{name}_*.{ext}")) if p.stat().st_size > 0]
    if existing:
        return existing[-1]
    _throttle(url)
    r = _session.post(url, data=data, timeout=90)
    r.raise_for_status()
    if not r.content:
        raise ValueError(f"Respuesta vacía (HTTP {r.status_code}) para {url}")
    p = raw_path(name, ext)
    p.write_bytes(r.content)
    return p

SOURCES = {
    # id: (url, nombre local, ext, descripción, tipo)
    "anuncio": ("https://www.argentina.gob.ar/noticias/luis-caputo-anuncio-la-puesta-en-marcha-del-programa-de-ciudadania-por-inversion-de",
                "A_anuncio_mecon", "html", "Ministerio de Economía, anuncio del 02/10/2026", "P"),
    "dnu366": ("https://www.boletinoficial.gob.ar/detalleAviso/primera/326096/20250529",
               "A_bo_dnu366_2025", "html", "Boletín Oficial, DNU 366/2025 (29/05/2025)", "P"),
    "dnu366_mod": ("https://www.argentina.gob.ar/normativa/nacional/norma-413297/normas-modifican",
                   "A_infoleg_dnu366_modifican", "html", "InfoLEG/argentina.gob.ar, normas que modifican o complementan el DNU 366/2025", "P"),
    "dec524": ("https://www.boletinoficial.gob.ar/detalleAviso/primera/329061/20250731",
               "A_bo_dec524_2025", "html", "Boletín Oficial, Decreto 524/2025 (31/07/2025)", "P"),
    "dec285": ("https://www.boletinoficial.gob.ar/pdf/aviso/primera/341227/20260428",
               "A_bo_dec285_2026", "pdf", "Boletín Oficial, Decreto 285/2026 (28/04/2026)", "P"),
    "cne_yang": (GDRIVE.format("1xWgM2IK8QeBFwmNogXJqYmY9RNC7z6gn"),
                 "A_fallo_CNE_Yang_8843-2023", "pdf",
                 "Cámara Nacional Electoral, 'Yang, Liping s/nacionalidad y ciudadanía', Expte. CNE 8843/2023/CA1, 30/06/2026 "
                 "(copia firmada digitalmente, difundida por Palabras del Derecho)", "P"),
    "jf_esquel": (GDRIVE.format("1m8JzZS80fcB-ENA-lI-0gr5Ii01sURig"),
                  "A_fallo_JFEsquel_DNU366", "pdf",
                  "Juzgado Federal de Esquel, Expte. 10640/2025, sentencia definitiva 12/08/2026 "
                  "(copia difundida por Palabras del Derecho)", "P"),
    "senado_46pe25": ("https://www.senado.gob.ar/parlamentario/comisiones/verExp/46.25/PE/DC",
                      "A_senado_exp46-PE-2025", "html",
                      "Senado de la Nación, ficha del Expte. 46/25 PE (Mensaje 52/25: comunica el DNU 366/25), consulta 03/10/2026",
                      "P"),
    "hcdn_366": (HCDN_BUSCADOR, "A_hcdn_busqueda_366-2025", "html",
                 "HCDN, buscador de proyectos (Diputados y Senado), palabras '366/2025', consulta 03/10/2026 "
                 "(formulario público, POST strPalabras=366/2025)", "P"),
    "bo_20261002": ("https://www.boletinoficial.gob.ar/seccion/primera/20261002",
                    "A_bo_primera_20261002", "html",
                    "Boletín Oficial, primera sección, sumario de la edición del 02/10/2026", "P"),
    "bo_vigente": ("https://www.boletinoficial.gob.ar/seccion/primera",
                   "A_bo_primera_vigente", "html",
                   "Boletín Oficial, primera sección, edición vigente al consultar (03/10/2026)", "P"),
}

# (claim_id, etiqueta, afirmación, valor, fuente, cita literal que debe estar en la copia local)
CLAIMS = [
    ("A01", "DATO", "Aporte no reembolsable al Tesoro del solicitante principal", "USD 350.000", "anuncio",
     "realizar un aporte directo y no reembolsable al Tesoro Nacional por USD 350.000"),
    ("A02", "DATO", "Alternativa: suscripción de un título público específico", "USD 800.000", "anuncio",
     "suscribir un título público de USD 800.000 creado específicamente para este Programa"),
    ("A03", "DATO", "Aporte por cónyuge e hijos de 18 a 25 años solteros y sin hijos", "USD 100.000", "anuncio",
     "podrán solicitar la ciudadanía mediante un aporte de USD 100.000 al Tesoro Nacional"),
    ("A04", "DATO", "Aporte por hijo menor de 18 años", "USD 25.000", "anuncio",
     "Los menores de 18 años podrán hacerlo mediante un aporte de USD 25.000"),
    ("A05", "DATO", "Total para familia tipo (principal + cónyuge + 2 menores)", "USD 500.000", "anuncio",
     "podrá solicitar la ciudadanía argentina por un total de USD 500.000"),
    ("A06", "DATO", "Inicio de recepción de solicitudes", "4.º trimestre de 2026", "anuncio",
     "estará operativo para recibir solicitudes en el transcurso del cuarto trimestre de 2026"),
    ("A07", "DATO", "Organismos que intervienen en la evaluación", "SIDE, UIF, Seguridad, Interior", "anuncio",
     "la Secretaría de Inteligencia del Estado (SIDE), la Unidad de Información Financiera (UIF) y el Ministerio de Seguridad y el de Interior"),
    ("A08", "DATO", "Destino de los fondos", "Posición fiscal y financiera", "anuncio",
     "Los recursos obtenidos se destinarán a continuar fortaleciendo la posición fiscal y financiera de la República Argentina"),
    ("A09", "DATO", "El DNU 366/2025 incorpora la naturalización por 'inversión relevante' sin requisito de residencia", "Ley 346 art. 2 inc. 2", "dnu366",
     "Los extranjeros que acrediten ante la DIRECCIÓN NACIONAL DE MIGRACIONES, cualquiera sea el tiempo de su residencia, haber realizado una inversión relevante en el país"),
    ("A10", "DATO", "El DNU no fija monto: delega en el Ministerio de Economía qué inversión es 'relevante'", "Ley 346 art. 2 bis", "dnu366",
     "el MINISTERIO DE ECONOMÍA establecerá qué inversiones serán consideradas relevantes, pudiendo establecer proyectos específicos de inversión a tal efecto"),
    ("A11", "DATO", "Creación de la Agencia de Programas de Ciudadanía por Inversión", "Ley 346 art. 6 bis", "dnu366",
     "Créase la AGENCIA DE PROGRAMAS DE CIUDADANÍA POR INVERSIÓN como organismo descentralizado actuante en el ámbito del MINISTERIO DE ECONOMÍA"),
    ("A12", "DATO", "La Agencia debe publicar anualmente las inversiones recibidas", "Ley 346 art. 6 ter inc. 2", "dnu366",
     "Publicar anualmente las inversiones recibidas por los programas de ciudadanía por inversión"),
    ("A13", "DATO", "El 366/2025 es un DNU sujeto a la Comisión Bicameral Permanente (Ley 26.122)", "art. 48", "dnu366",
     "Dese cuenta a la COMISIÓN BICAMERAL PERMANENTE del H. CONGRESO DE LA NACIÓN"),
    ("A14", "DATO", "Decreto 524/2025: la DNM resuelve en 30 días hábiles tras el informe de la Agencia", "30 días hábiles", "dec524",
     "La DIRECCIÓN NACIONAL DE MIGRACIONES, en un plazo de TREINTA (30) días hábiles desde que hubiere recibido el informe elaborado por la Agencia"),
    ("A15", "DATO", "Decreto 524/2025: informes de Seguridad, UIF, Reincidencia, RENAPER y SIDE sobre riesgo", "Procedimiento", "dec524",
     "se expidan respecto de si el otorgamiento de la ciudadanía al solicitante podría representar un riesgo para la seguridad nacional o para los intereses nacionales"),
    ("A16", "DATO", "Decreto 285/2026: designación ad honorem de la directora ejecutiva de la Agencia desde el 22/04/2026", "22/04/2026", "dec285",
     "Desígnase, a partir del 22 de abril de 2026, con carácter “ad honorem” en el cargo de Directora Ejecutiva de la AGENCIA DE PROGRAMAS DE CIUDADANÍA POR INVERSIÓN"),
    ("A17", "DATO", "Según InfoLEG (consulta 03/10/2026), el DNU 366/2025 solo es complementado por el Dec. 524/2025 y la Res. 1066/2026 (Salud): no figura norma que fije los montos", "2 normas", "dnu366_mod",
     "Esta norma es complementada o modificada por las siguientes"),
    ("A18", "DATO", "La Cámara Nacional Electoral declaró nulo el DNU 366/2025 (art. 99 inc. 3 CN) en la causa 'Yang'", "30/06/2026", "cne_yang",
     "Declarar nulo el decreto de necesidad y urgencia N° 366/2025, de conformidad con lo establecido por el art. 99, inc. 3°, párrafo segundo de la Constitución Nacional"),
    ("A19", "DATO", "La CNE ordenó comunicar la sentencia a todos los jueces federales con competencia electoral", "30/06/2026", "cne_yang",
     "Poner en conocimiento de la presente a los señores jueces federales con competencia electoral de todo el país"),
    ("A20", "DATO", "El Juzgado Federal de Esquel declaró inconstitucionales e inaplicables al caso los arts. 4, 37 y 39 del DNU 366/2025 (el art. 37 crea la vía por inversión)", "12/08/2026", "jf_esquel",
     "DECLARAR la INCONSTITUCIONALIDAD e INAPLICABILIDAD a su respecto de los artículos 4, 37 y 39 del Decreto de Necesidad y Urgencia 366/2025"),
    # --- Control parlamentario (Ley 26.122) ---
    ("A21", "DATO", "El Mensaje 52/25 que comunica el DNU 366/25 (Senado, Expte. 46/25 PE) fue girado a la Comisión Bicameral Permanente de Trámite Legislativo (Ley 26.122)", "10/06/2025", "senado_46pe25",
     "BICAMERAL PERMANENTE DE TRÁMITE LEGISLATIVO (LEY 26.122) ORDEN DE GIRO: 1 10-06-2025"),
    ("A22", "DATO", "La ficha del Senado no registra dictamen de la Comisión Bicameral sobre el DNU 366/25 ni fecha de egreso del giro (consulta 03/10/2026)", "Sin dictamen", "senado_46pe25",
     "INGRESO DEL DICTAMEN A LA MESA DE ENTRADAS 10-06-2025 SIN FECHA"),
    ("A23", "DATO", "El buscador de proyectos de la HCDN devuelve 5 expedientes que mencionan el DNU 366/2025; ninguno registra dictamen de comisión ni sanción (consulta 03/10/2026)", "5 expedientes", "hcdn_366",
     "Resultados de Búsqueda: 5 Proyectos Encontrados"),
    ("A24", "DATO", "Proyecto de ley 3176-D-2025 (bloques del FIT-U) para anular el DNU 366/2025; girado a Asuntos Constitucionales y Población, sin dictamen", "17/06/2025", "hcdn_366",
     "Expediente Diputados: 3176-D-2025 Publicado en: Trámite Parlamentario N° 75 Fecha: 17/06/2025 ANULESE EL DECRETO DE NECESIDAD Y URGENCIA 366/2025"),
    ("A25", "DATO", "Proyecto de resolución 4025-D-2025 (Unión por la Patria) de repudio al DNU 366/2025, sin dictamen", "24/07/2025", "hcdn_366",
     "Expediente Diputados: 4025-D-2025 Publicado en: Trámite Parlamentario N° 100 Fecha: 24/07/2025 EXPRESAR REPUDIO AL DECRETO N° 366/2025"),
    ("A26", "DATO", "Proyecto de resolución 3233-D-2026 (Coalición Cívica) para declarar la nulidad absoluta del DNU 366/2025; sin dictamen", "02/07/2026", "hcdn_366",
     "Expediente Diputados: 3233-D-2026 Publicado en: Trámite Parlamentario N° 84 Fecha: 02/07/2026 DECLARAR DE NULIDAD ABSOLUTA E INSANABLE EL DNU 366/2025"),
    ("A27", "DATO", "Proyecto de ley 1441-S-2026 (sen. Capitanich): prohíbe la ciudadanía por inversión, deroga los arts. 2 inc. 2, 2 bis, 6 bis–6 quater de la Ley 346 (texto DNU 366/2025) y disuelve la Agencia; sin dictamen", "20/08/2026", "hcdn_366",
     "Expediente Senado: 1441-S-2026 Publicado en: Diario de Asuntos Entrados N° 63 Fecha: 20/08/2026 ESTABLECER UN REGIMEN DE PROTECCION DE LA CIUDADANIA ARGENTINA Y PROHIBICION DE SU OTORGAMIENTO POR INVERSION"),
    # --- ¿Norma que fije los montos anunciados? ---
    ("A28", "DATO", "La primera sección del Boletín Oficial del 02/10/2026 (día del anuncio) no publica decretos: solo resoluciones, disposiciones y avisos, ninguno sobre ciudadanía por inversión", "0 normas sobre el programa", "bo_20261002",
     "Avisos oficiales Avisos oficiales (29) Convenciones colectivas de trabajo (20) Disposiciones Disposiciones (2) Resoluciones Resolucion sintetizada (1) Resoluciones (17) Resolución general (1)"),
    ("A29", "DATO", "Al 03/10/2026 la edición vigente de la primera sección del Boletín Oficial es la del 02/10/2026 (no hubo edición el sábado 03/10)", "02/10/2026", "bo_vigente",
     "Edición del 2 de Octubre de 2026"),
]

# Hitos sin cita literal en una sola fuente o que son inferencias: van al informe con su etiqueta, no al ledger como DATO.
CRONOLOGIA = [
    ("2025-05-29", "DNU 366/2025 publicado: crea la vía 'inversión relevante' (Ley 346 art. 2 inc. 2) y la Agencia", "dnu366"),
    ("2025-06-10", "Senado, Expte. 46/25 PE: el DNU 366/25 se gira a la Comisión Bicameral Permanente (Ley 26.122); sin dictamen al 03/10/2026", "senado_46pe25"),
    ("2025-06-17", "Diputados, proyecto de ley 3176-D-2025 para anular el DNU 366/2025 (sin dictamen)", "hcdn_366"),
    ("2025-07-24", "Diputados, proyecto de resolución 4025-D-2025 de repudio al DNU 366/2025 (sin dictamen)", "hcdn_366"),
    ("2025-07-31", "Decreto 524/2025: procedimiento de solicitud y evaluación", "dec524"),
    ("2026-04-28", "Decreto 285/2026: designación de la directora ejecutiva (desde 22/04/2026)", "dec285"),
    ("2026-06-30", "CNE, causa 'Yang': declara nulo el DNU 366/2025", "cne_yang"),
    ("2026-07-02", "Diputados, proyecto de resolución 3233-D-2026 para declarar la nulidad del DNU 366/2025 (sin dictamen)", "hcdn_366"),
    ("2026-08-12", "Juzgado Federal de Esquel: inconstitucionalidad de arts. 4, 37 y 39 (efecto para el caso)", "jf_esquel"),
    ("2026-08-20", "Senado, proyecto de ley 1441-S-2026 que prohíbe la ciudadanía por inversión (sin dictamen)", "hcdn_366"),
    ("2026-10-02", "Anuncio MECON: USD 350.000 aporte / USD 800.000 bono; operativo en 4T-2026", "anuncio"),
    ("2026-10-02", "Boletín Oficial (1.ª sección): ninguna norma fija los montos anunciados", "bo_20261002"),
]


def main() -> None:
    files, texts = {}, {}
    for sid, (url, name, ext, _desc, _t) in SOURCES.items():
        files[sid] = download_post(url, POST_DATA[sid], name, ext) if sid in POST_DATA else download(url, name, ext)
        texts[sid] = local_text(files[sid])

    # Chequeos de las afirmaciones negativas (A22, A23, A28): si cambian las copias locales, el script falla.
    if "SIN FECHA" not in texts["senado_46pe25"]:
        raise ValueError("A22: la ficha del Senado ya registra fecha de dictamen; revisar")
    if "DICTÁMENES DE COMISIÓN" in texts["hcdn_366"]:
        raise ValueError("A23: algún expediente sobre el DNU 366/2025 registra dictamen; revisar")
    bo = texts["bo_20261002"].upper()
    if "CIUDADAN" in bo or "DECRETO" in bo:
        raise ValueError("A28: el sumario del BO 02/10/2026 menciona decretos o ciudadanía; revisar")

    rows = []
    for cid, label, claim, value, sid, needle in CLAIMS:
        url, _name, _ext, desc, tipo = SOURCES[sid]
        rows.append(dict(claim_id=cid, etiqueta=label, afirmacion=claim, valor=value, fuente=desc, tipo_fuente=tipo,
                         url=url, archivo_local=files[sid].relative_to(files[sid].parents[2]).as_posix(),
                         sha256=sha256(files[sid]), cita_textual=quote(texts[sid], needle)))
    write_ledger("A", rows)

    # Chequeo explícito de la "alerta temprana" del plan: ¿el DNU fija USD 500.000?
    has_amount = any(s in texts["dnu366"] for s in ("500.000", "QUINIENTOS MIL"))
    print(f"¿El texto del DNU 366/2025 menciona USD 500.000? {'sí' if has_amount else 'no'}")

    PROCESSED.mkdir(parents=True, exist_ok=True)
    with (PROCESSED / "A_cronologia.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fecha", "hito", "fuente"])
        for d, h, sid in CRONOLOGIA:
            w.writerow([d, h, SOURCES[sid][3]])
    print(f"{len(rows)} afirmaciones verificadas contra copias locales -> docs/claims_ledger.csv")


if __name__ == "__main__":
    main()
