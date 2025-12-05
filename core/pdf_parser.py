import re
from typing import Dict, List, Optional, Tuple

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


def extraer_datos_pdf(ruta_pdf: str) -> Dict[str, object]:
    """Devuelve campos detectados en el PDF (pueden faltar según el documento)."""
    if PdfReader is None:
        return {}

    try:
        reader = PdfReader(ruta_pdf)
    except Exception:
        return {}

    lineas: List[str] = []
    for pagina in reader.pages:
        texto = pagina.extract_text() or ""
        if not texto:
            continue
        for linea in texto.splitlines():
            limpia = linea.strip()
            if limpia:
                lineas.append(limpia)

    if not lineas:
        return {}

    datos: Dict[str, object] = {}

    titulo = _buscar_titulo(lineas)
    if titulo:
        datos["titulo"] = titulo

    autores = _buscar_autores(lineas)
    if autores:
        datos["autores"] = autores

    resumen = _buscar_resumen(lineas)
    if resumen:
        datos["resumen"] = resumen

    palabras = _buscar_palabras_clave(lineas)
    if palabras:
        datos["palabras_clave"] = palabras

    anio = _buscar_anio(lineas)
    if anio:
        datos["anio"] = anio

    return datos


def _buscar_titulo(lineas: List[str]) -> Optional[str]:
    patron = re.compile(r"AMPLIACI[ÓO]N\s+ANACO", re.IGNORECASE)
    for idx, linea in enumerate(lineas):
        if patron.search(linea):
            for siguiente in lineas[idx + 1:]:
                if siguiente.strip():
                    return siguiente.strip()
            break
    return None


def _buscar_autores(lineas: List[str]) -> List[Tuple[str, str]]:
    patrones = [
        re.compile(r"Autor(?:a)?(?:\s*\(a\))?\s*:\s*(.+)", re.IGNORECASE),
    ]
    autores: List[Tuple[str, str]] = []
    for linea in lineas:
        for patron in patrones:
            coincidencia = patron.search(linea)
            if coincidencia:
                segmento = coincidencia.group(1)
                autores.extend(_segmentar_autores(segmento))
    return autores


def _segmentar_autores(segmento: str) -> List[Tuple[str, str]]:
    segmento = segmento.replace(" y ", ",")
    candidatos = [parte.strip() for parte in re.split(r",|;", segmento) if parte.strip()]
    autores: List[Tuple[str, str]] = []
    for candidato in candidatos:
        partes = candidato.split()
        if len(partes) >= 2:
            nombre = " ".join(partes[:-1])
            apellido = partes[-1]
        else:
            nombre = candidato
            apellido = candidato
        autores.append((nombre.title(), apellido.title()))
    return autores


def _buscar_resumen(lineas: List[str]) -> Optional[str]:
    patron = re.compile(r"^RESUMEN$", re.IGNORECASE)
    for idx, linea in enumerate(lineas):
        if patron.match(linea.strip()):
            acumulado: List[str] = []
            for siguiente in lineas[idx + 1:]:
                if not siguiente.strip():
                    if acumulado:
                        break
                    continue
                if re.match(r"^[A-ZÁÉÍÓÚÑ ]{4,}$", siguiente):
                    if acumulado:
                        break
                acumulado.append(siguiente.strip())
                if len(" ".join(acumulado)) > 1000:
                    break
            if acumulado:
                return " ".join(acumulado)
    return None


def _buscar_palabras_clave(lineas: List[str]) -> Optional[str]:
    patron = re.compile(r"(Palabras\s*Clave|Descriptores?)\s*:\s*(.+)", re.IGNORECASE)
    for linea in lineas:
        coincidencia = patron.search(linea)
        if coincidencia:
            return coincidencia.group(2).strip()
    return None


def _buscar_anio(lineas: List[str]) -> Optional[str]:
    patron = re.compile(r"Anaco,\s*(?:\d{1,2}\s+de\s+\w+\s+de\s+)?(\d{4})", re.IGNORECASE)
    for linea in lineas:
        coincidencia = patron.search(linea)
        if coincidencia:
            return coincidencia.group(1)
    return None
