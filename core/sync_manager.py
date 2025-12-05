import datetime
import json
import os
import shutil
import tempfile
import zipfile
from typing import Dict, List, Optional, Tuple

from core import config

try:
    import pyodbc
except ImportError:
    pyodbc = None

try:
    import pymysql
except ImportError:
    pymysql = None


def _convertir_fecha(valor) -> Optional[str]:
    if valor is None:
        return None
    if isinstance(valor, str):
        return valor
    return valor.isoformat()


def _obtener_conexion():
    conector = getattr(config, "DB_CONNECTOR", "odbc")
    if conector == "pymysql":
        if pymysql is None:
            raise ConnectionError("PyMySQL no está disponible para la exportación.")
        return pymysql.connect(
            host=config.DB_SERVER,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            port=int(config.DB_PORT),
            charset="utf8mb4",
            autocommit=True,
        ), True
    if pyodbc is None:
        raise ConnectionError("pyodbc no está disponible para la exportación.")
    return pyodbc.connect(config.SQL_SERVER_CONNECTION_STRING), False


def _leer_tegs(carrera_id: Optional[int], desde: Optional[str]) -> Tuple[List[Dict[str, object]], Dict[str, Dict[str, object]]]:
    connection, es_pymysql = _obtener_conexion()
    placeholder = "%s" if es_pymysql else "?"
    query = """
        SELECT
            T.TEGID,
            T.GuidGlobal AS TGuid,
            T.Titulo,
            T.Resumen,
            T.AnioPublicacion,
            T.PalabrasClave,
            T.RutaArchivoPDF,
            T.CarreraID,
            T.FechaActualizacion,
            A.AutorID,
            A.GuidGlobal AS AGuid,
            A.Nombre,
            A.Apellido,
            A.FechaActualizacion AS AutorFecha
        FROM TEG T
        LEFT JOIN TEGAutores TA ON T.TEGID = TA.TEGID
        LEFT JOIN Autores A ON TA.AutorID = A.AutorID
    """
    filtros: List[str] = []
    params: List[object] = []
    if carrera_id:
        filtros.append(f"T.CarreraID = {placeholder}")
        params.append(carrera_id)
    if desde:
        filtros.append(f"T.FechaActualizacion >= {placeholder}")
        params.append(desde)
    if filtros:
        query += " WHERE " + " AND ".join(filtros)
    query += " ORDER BY T.FechaActualizacion ASC"

    tegs_map: Dict[str, Dict[str, object]] = {}
    autores_map: Dict[str, Dict[str, object]] = {}

    try:
        cursor = connection.cursor()
        if es_pymysql:
            cursor.execute(query, tuple(params))
        else:
            cursor.execute(query, *params)
        rows = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    for row in rows:
        teg_guid = row[1]
        if not teg_guid:
            continue
        if teg_guid not in tegs_map:
            tegs_map[teg_guid] = {
                "GuidGlobal": teg_guid,
                "TEGID": row[0],
                "Titulo": row[2],
                "Resumen": row[3],
                "AnioPublicacion": row[4],
                "PalabrasClave": row[5],
                "RutaArchivoPDF": row[6],
                "CarreraID": row[7],
                "FechaActualizacion": _convertir_fecha(row[8]),
                "UsuarioAgregaID": None,
                "AutorGuids": [],
            }
        autor_guid = row[10]
        if autor_guid:
            if autor_guid not in autores_map:
                autores_map[autor_guid] = {
                    "GuidGlobal": autor_guid,
                    "Nombre": row[11],
                    "Apellido": row[12],
                    "FechaActualizacion": _convertir_fecha(row[13]),
                }
            if autor_guid not in tegs_map[teg_guid]["AutorGuids"]:
                tegs_map[teg_guid]["AutorGuids"].append(autor_guid)
    return list(tegs_map.values()), autores_map


def export_tegs_package(dest_zip_path: str, carrera_id: Optional[int] = None, desde: Optional[str] = None) -> str:
    if getattr(config, "DB_MODO_DEMO", False):
        raise RuntimeError("No se puede exportar en modo demo.")

    tegs, autores_map = _leer_tegs(carrera_id, desde)
    temp_dir = tempfile.mkdtemp(prefix="repositorio_export_")
    try:
        pdf_dir = os.path.join(temp_dir, "pdf")
        os.makedirs(pdf_dir, exist_ok=True)
        for teg in tegs:
            ruta_pdf = teg.get("RutaArchivoPDF")
            if ruta_pdf and os.path.exists(ruta_pdf):
                nombre_pdf = f"{teg['GuidGlobal']}.pdf"
                shutil.copyfile(ruta_pdf, os.path.join(pdf_dir, nombre_pdf))
            teg["ArchivoPDFEmpacado"] = f"pdf/{teg['GuidGlobal']}.pdf"

        manifest = {
            "version": 1,
            "generador": "RepositorioBibliotecaUTSAnaco",
            "fecha": datetime.datetime.utcnow().isoformat() + "Z",
            "tegs": tegs,
            "autores": list(autores_map.values()),
        }

        manifest_path = os.path.join(temp_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        with zipfile.ZipFile(dest_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(manifest_path, "manifest.json")
            for nombre in os.listdir(pdf_dir):
                ruta_archivo = os.path.join(pdf_dir, nombre)
                zipf.write(ruta_archivo, os.path.join("pdf", nombre))
    finally:
        shutil.rmtree(temp_dir)
    return dest_zip_path


def _leer_manifest_zip(zip_path: str) -> Dict[str, object]:
    with zipfile.ZipFile(zip_path, "r") as zipf:
        if "manifest.json" not in zipf.namelist():
            raise FileNotFoundError("El paquete no contiene manifest.json")
        with zipf.open("manifest.json") as f:
            return json.load(f)


def _copiar_pdf_desde_zip(zipf: zipfile.ZipFile, ruta_interna: str, guid: str) -> Optional[str]:
    if not ruta_interna:
        return None
    nombre_destino = f"{guid}.pdf"
    ruta_destino = os.path.join(config.RUTA_BASE_TESIS, nombre_destino)
    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
    try:
        with zipf.open(ruta_interna) as fuente, open(ruta_destino, "wb") as destino:
            shutil.copyfileobj(fuente, destino)
        return ruta_destino
    except KeyError:
        return None


def _eliminar_teg_por_guid(cursor, guid: str, es_pymysql: bool) -> Optional[str]:
    if not guid:
        return None
    placeholder = "%s" if es_pymysql else "?"
    select_sql = f"SELECT TEGID, RutaArchivoPDF FROM TEG WHERE GuidGlobal = {placeholder}"
    params = (guid,) if es_pymysql else (guid,)
    cursor.execute(select_sql, params)
    row = cursor.fetchone()
    if not row:
        return None
    teg_id = row[0]
    ruta_pdf = row[1] if len(row) > 1 else None
    delete_autores_sql = f"DELETE FROM TEGAutores WHERE TEGID = {placeholder}"
    delete_teg_sql = f"DELETE FROM TEG WHERE TEGID = {placeholder}"
    cursor.execute(delete_autores_sql, params)
    cursor.execute(delete_teg_sql, params)
    if ruta_pdf and os.path.exists(ruta_pdf):
        try:
            os.remove(ruta_pdf)
        except Exception:
            pass
    return ruta_pdf


def _eliminar_teg_por_ruta(cursor, ruta: str, es_pymysql: bool) -> Optional[int]:
    if not ruta:
        return None
    placeholder = "%s" if es_pymysql else "?"
    select_sql = f"SELECT TEGID FROM TEG WHERE RutaArchivoPDF = {placeholder}"
    params = (ruta,) if es_pymysql else (ruta,)
    cursor.execute(select_sql, params)
    row = cursor.fetchone()
    if not row:
        return None
    teg_id = row[0]
    delete_autores_sql = f"DELETE FROM TEGAutores WHERE TEGID = {placeholder}"
    delete_teg_sql = f"DELETE FROM TEG WHERE TEGID = {placeholder}"
    cursor.execute(delete_autores_sql, params)
    cursor.execute(delete_teg_sql, params)
    return teg_id


def import_tegs_package(zip_path: str, sobrescribir: bool = False) -> Dict[str, int]:
    if getattr(config, "DB_MODO_DEMO", False):
        raise RuntimeError("No se puede importar en modo demo.")

    manifest = _leer_manifest_zip(zip_path)
    tegs: List[Dict[str, object]] = manifest.get("tegs", [])
    autores: List[Dict[str, object]] = manifest.get("autores", [])

    if not tegs:
        return {"tegs_importados": 0, "autores_creados": 0, "tegs_actualizados": 0}

    connection, es_pymysql = _obtener_conexion()
    placeholder = "%s" if es_pymysql else "?"
    insertar_autor_sql = (
        f"INSERT INTO Autores (Nombre, Apellido, GuidGlobal) VALUES ({placeholder}, {placeholder}, {placeholder})"
    )
    select_autor_sql = f"SELECT AutorID FROM Autores WHERE GuidGlobal = {placeholder}"
    insertar_teg_sql = (
        f"INSERT INTO TEG (GuidGlobal, Titulo, Resumen, AnioPublicacion, PalabrasClave, RutaArchivoPDF, UsuarioAgregaID, CarreraID)"
        f" VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
    )
    select_teg_sql = f"SELECT TEGID FROM TEG WHERE GuidGlobal = {placeholder}"
    actualizar_teg_sql = (
        f"UPDATE TEG SET Titulo = {placeholder}, Resumen = {placeholder}, AnioPublicacion = {placeholder}, PalabrasClave = {placeholder}, RutaArchivoPDF = {placeholder}, CarreraID = {placeholder}"
        f" WHERE GuidGlobal = {placeholder}"
    )
    insertar_relacion_sql = "INSERT IGNORE INTO TEGAutores (TEGID, AutorID) VALUES (%s, %s)"
    if not es_pymysql:
        insertar_relacion_sql = "INSERT INTO TEGAutores (TEGID, AutorID) SELECT ?, ? WHERE NOT EXISTS (SELECT 1 FROM TEGAutores WHERE TEGID = ? AND AutorID = ?)"

    pdf_temp_dir = tempfile.mkdtemp(prefix="repositorio_import_")
    try:
        summary = {"tegs_importados": 0, "tegs_actualizados": 0, "autores_creados": 0}
        cursor = connection.cursor()
        try:
            if not es_pymysql:
                connection.autocommit = False
            else:
                connection.autocommit = False

            autor_ids: Dict[str, int] = {}
            for autor in autores:
                guid = autor.get("GuidGlobal")
                if not guid:
                    continue
                if es_pymysql:
                    cursor.execute(select_autor_sql, (guid,))
                else:
                    cursor.execute(select_autor_sql, guid)
                encontrado = cursor.fetchone()
                if encontrado:
                    autor_ids[guid] = encontrado[0]
                    continue
                nombre = autor.get("Nombre")
                apellido = autor.get("Apellido")
                if es_pymysql:
                    cursor.execute(insertar_autor_sql, (nombre, apellido, guid))
                    autor_ids[guid] = cursor.lastrowid
                else:
                    cursor.execute(insertar_autor_sql, (nombre, apellido, guid))
                    cursor.execute("SELECT LAST_INSERT_ID();")
                    autor_ids[guid] = cursor.fetchone()[0]
                summary["autores_creados"] += 1

            with zipfile.ZipFile(zip_path, "r") as zipf:
                for teg in tegs:
                    guid = teg.get("GuidGlobal")
                    if not guid:
                        continue
                    if es_pymysql:
                        cursor.execute(select_teg_sql, (guid,))
                    else:
                        cursor.execute(select_teg_sql, guid)
                    existent = cursor.fetchone()
                    if existent and sobrescribir:
                        _eliminar_teg_por_guid(cursor, guid, es_pymysql)
                        existent = None
                    ruta_pdf_dest = _copiar_pdf_desde_zip(zipf, teg.get("ArchivoPDFEmpacado"), guid)
                    if not ruta_pdf_dest:
                        ruta_pdf_dest = os.path.join(config.RUTA_BASE_TESIS, f"{guid}.pdf")
                    if ruta_pdf_dest:
                        _eliminar_teg_por_ruta(cursor, ruta_pdf_dest, es_pymysql)
                    if existent and not sobrescribir:
                        continue
                    params = (
                        guid,
                        teg.get("Titulo"),
                        teg.get("Resumen"),
                        teg.get("AnioPublicacion"),
                        teg.get("PalabrasClave"),
                        ruta_pdf_dest or config.RUTA_BASE_TESIS,
                        teg.get("UsuarioAgregaID") or 1,
                        teg.get("CarreraID"),
                    )
                    if existent:
                        update_params = (
                            teg.get("Titulo"),
                            teg.get("Resumen"),
                            teg.get("AnioPublicacion"),
                            teg.get("PalabrasClave"),
                            ruta_pdf_dest or config.RUTA_BASE_TESIS,
                            teg.get("CarreraID"),
                            guid,
                        )
                        cursor.execute(actualizar_teg_sql, update_params)
                        summary["tegs_actualizados"] += 1
                        teg_id = existent[0]
                    else:
                        try:
                            cursor.execute(insertar_teg_sql, params)
                        except Exception as insert_ex:
                            mensaje = str(insert_ex)
                            if "RutaArchivoPDF" in mensaje:
                                if ruta_pdf_dest:
                                    _eliminar_teg_por_ruta(cursor, ruta_pdf_dest, es_pymysql)
                                cursor.execute(insertar_teg_sql, params)
                            else:
                                raise
                        summary["tegs_importados"] += 1
                        if es_pymysql:
                            teg_id = cursor.lastrowid
                        else:
                            cursor.execute("SELECT LAST_INSERT_ID();")
                            teg_id = cursor.fetchone()[0]

                    autor_guids = teg.get("AutorGuids", [])
                    for autor_guid in autor_guids:
                        autor_id = autor_ids.get(autor_guid)
                        if not autor_id:
                            continue
                        if es_pymysql:
                            cursor.execute(insertar_relacion_sql, (teg_id, autor_id))
                        else:
                            cursor.execute(insertar_relacion_sql, (teg_id, autor_id, teg_id, autor_id))

                if not es_pymysql:
                    connection.commit()
            if es_pymysql:
                connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    finally:
        shutil.rmtree(pdf_temp_dir)
        connection.close()
    return summary
