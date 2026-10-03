"""Módulo A — Marco normativo del Programa de Ciudadanía por Inversión.

Descarga las normas y sentencias, verifica citas textuales contra las copias locales y escribe:
  data/processed/A_cronologia.csv   línea de tiempo normativa y judicial
  docs/claims_ledger.csv            afirmaciones del módulo con su cita literal
"""
from __future__ import annotations

import csv

from common import PROCESSED, download, local_text, quote, sha256, write_ledger

GDRIVE = "https://drive.google.com/uc?export=download&id={}"

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
]

# Hitos sin cita literal en una sola fuente o que son inferencias: van al informe con su etiqueta, no al ledger como DATO.
CRONOLOGIA = [
    ("2025-05-29", "DNU 366/2025 publicado: crea la vía 'inversión relevante' (Ley 346 art. 2 inc. 2) y la Agencia", "dnu366"),
    ("2025-07-31", "Decreto 524/2025: procedimiento de solicitud y evaluación", "dec524"),
    ("2026-04-28", "Decreto 285/2026: designación de la directora ejecutiva (desde 22/04/2026)", "dec285"),
    ("2026-06-30", "CNE, causa 'Yang': declara nulo el DNU 366/2025", "cne_yang"),
    ("2026-08-12", "Juzgado Federal de Esquel: inconstitucionalidad de arts. 4, 37 y 39 (efecto para el caso)", "jf_esquel"),
    ("2026-10-02", "Anuncio MECON: USD 350.000 aporte / USD 800.000 bono; operativo en 4T-2026", "anuncio"),
]


def main() -> None:
    files, texts = {}, {}
    for sid, (url, name, ext, _desc, _t) in SOURCES.items():
        files[sid] = download(url, name, ext)
        texts[sid] = local_text(files[sid])

    rows = []
    for cid, label, claim, value, sid, needle in CLAIMS:
        url, _name, _ext, desc, tipo = SOURCES[sid]
        rows.append(dict(claim_id=cid, etiqueta=label, afirmacion=claim, valor=value, fuente=desc, tipo_fuente=tipo,
                         url=url, archivo_local=str(files[sid].relative_to(files[sid].parents[2])),
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
