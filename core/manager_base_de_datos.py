import uuid
try:
    import pyodbc
    _PYODBC_DISPONIBLE = True
except ImportError:
    pyodbc = None
    _PYODBC_DISPONIBLE = False

try:
    import pymysql
    _PYMYSQL_DISPONIBLE = True
except ImportError:
    pymysql = None
    _PYMYSQL_DISPONIBLE = False

from core import config  
from tkinter import messagebox

class ManagerBaseDeDatos:


    def __init__(self):

        self.conn_str = config.SQL_SERVER_CONNECTION_STRING

        if getattr(config, "DB_MODO_DEMO", False):
            print("[ManagerBaseDeDatos] MODO_DEMO activo. No se conecta a la BD.")
            return

        self._conector = getattr(config, "DB_CONNECTOR", "odbc")

        if self._conector == "pymysql":
            if not _PYMYSQL_DISPONIBLE:
                raise ConnectionError("PyMySQL no está instalado. Instale con: pip install PyMySQL")
            try:
                with pymysql.connect(
                    host=config.DB_SERVER,
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    database=config.DB_NAME,
                    port=int(config.DB_PORT),
                    charset="utf8mb4",
                    autocommit=True,
                ) as conn:
                    print("ManagerBaseDeDatos (PyMySQL): Conexión de prueba exitosa.")
            except Exception as ex:
                raise ConnectionError(f"Error de conexión a la base de datos (PyMySQL): {ex}")
            return

        if not _PYODBC_DISPONIBLE:
            raise ConnectionError("pyodbc no disponible y DB_CONNECTOR=odbc. Instale pyodbc o cambie a DB_CONNECTOR='pymysql'.")

        try:
            # Intenta una conexión de prueba para asegurar que el servidor esté vivo
            with pyodbc.connect(self.conn_str):
                print("ManagerBaseDeDatos: Conexión de prueba a la DB exitosa.")
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"ERROR: No se pudo conectar a la base de datos: {sqlstate}")
            # El Controlador atrapa este error y cierra la app si es necesario
            raise ConnectionError(f"Error de conexión a la base de datos: {sqlstate}")



    def buscar_libros_o_tesis(self, termino, carrera_id=None):
        sql_base = """
            SELECT 
                T.TEGID, 
                T.Titulo, 
                GROUP_CONCAT(CONCAT(A.Nombre, ' ', A.Apellido) SEPARATOR ', ') AS Autores, 
                C.Nombre AS Carrera, 
                T.AnioPublicacion,
                T.RutaArchivoPDF
            FROM TEG T
            JOIN TEGAutores TA ON T.TEGID = TA.TEGID
            JOIN Autores A ON TA.AutorID = A.AutorID
            JOIN Carreras C ON T.CarreraID = C.CarreraID
            WHERE 
                (T.Titulo LIKE {p} OR 
                 T.Resumen LIKE {p} OR 
                 T.PalabrasClave LIKE {p})
            GROUP BY T.TEGID, T.Titulo, C.Nombre, T.AnioPublicacion, T.RutaArchivoPDF
            ORDER BY T.AnioPublicacion DESC
        """
        
        termino_like = f"%{termino}%"
        resultados = []
        
        if getattr(config, "DB_MODO_DEMO", False):
            print("[ManagerBaseDeDatos] Búsqueda llamada en modo DEMO (sin BD). Retornando lista vacía.")
            return []

        if getattr(self, "_conector", "odbc") == "pymysql":
            where_extra = ""
            params = [termino_like, termino_like, termino_like]
            if carrera_id:
                where_extra = " AND T.CarreraID = %s"
                params.append(carrera_id)
            sql_exec = sql_base.replace("GROUP BY", where_extra + "\n            GROUP BY").format(p="%s")
            try:
                with pymysql.connect(
                    host=config.DB_SERVER,
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    database=config.DB_NAME,
                    port=int(config.DB_PORT),
                    charset="utf8mb4",
                ) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(sql_exec, tuple(params))
                        resultados = cursor.fetchall()
            except Exception as ex:
                messagebox.showerror("Error de Búsqueda", f"No se pudo ejecutar la búsqueda (PyMySQL): {ex}")
        else:
            # ODBC
            if not _PYODBC_DISPONIBLE:
                messagebox.showerror("Error de Búsqueda", "pyodbc no disponible.")
                return []
            where_extra = ""
            params = [termino_like, termino_like, termino_like]
            if carrera_id:
                where_extra = " AND T.CarreraID = ?"
                params.append(carrera_id)
            sql_exec = sql_base.replace("GROUP BY", where_extra + "\n            GROUP BY").format(p="?")
            try:
                with pyodbc.connect(self.conn_str) as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql_exec, *params)
                    resultados = cursor.fetchall()
            except pyodbc.Error as ex:
                sqlstate = ex.args[0]
                messagebox.showerror("Error de Búsqueda", f"No se pudo ejecutar la búsqueda en la DB. Código: {sqlstate}")
        
        return resultados


    def obtener_resumen_disponibilidad(self):

        sql = """
            SELECT 
                C.Nombre AS Carrera, 
                COUNT(T.TEGID) AS CantidadTEG
            FROM TEG T
            JOIN Carreras C ON T.CarreraID = C.CarreraID
            GROUP BY C.Nombre
            ORDER BY CantidadTEG DESC;
        """
        if getattr(config, "DB_MODO_DEMO", False):
            print("[ManagerBaseDeDatos] obtener_resumen_disponibilidad en modo DEMO. Retornando lista vacía.")
            return []

        if getattr(self, "_conector", "odbc") == "pymysql":
            try:
                with pymysql.connect(
                    host=config.DB_SERVER,
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    database=config.DB_NAME,
                    port=int(config.DB_PORT),
                    charset="utf8mb4",
                ) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(sql)
                        return cursor.fetchall()
            except Exception as ex:
                messagebox.showerror("Error de Datos", f"No se pudo obtener el resumen (PyMySQL): {ex}")
                return []
        else:
            if not _PYODBC_DISPONIBLE:
                messagebox.showerror("Error de Datos", "pyodbc no disponible.")
                return []
            try:
                with pyodbc.connect(self.conn_str) as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    return cursor.fetchall()
            except pyodbc.Error as ex:
                sqlstate = ex.args[0]
                messagebox.showerror("Error de Datos", f"No se pudo obtener el resumen para el gráfico. Código: {sqlstate}")
                return []


    # ====================================================================
    # II. MÉTODOS DE ADMIN (CREATE, UPDATE, DELETE - Para uso futuro)
    # ====================================================================
    def insertar_nueva_tesis(self, tesis_data, autores_existentes, autores_nuevos):
        
        sql_insert_tesis = """
            INSERT INTO TEG (GuidGlobal, Titulo, Resumen, AnioPublicacion, PalabrasClave, 
                             RutaArchivoPDF, UsuarioAgregaID, CarreraID)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        sql_insert_autor = "INSERT INTO Autores (Nombre, Apellido) VALUES (?, ?);"
        sql_insert_tesis_autores = "INSERT INTO TEGAutores (TEGID, AutorID) VALUES (?, ?);"
        sql_select_autor = "SELECT AutorID FROM Autores WHERE Nombre = ? AND Apellido = ?;"
        # Variantes para PyMySQL (%s)
        sql_insert_tesis_p = """
            INSERT INTO TEG (GuidGlobal, Titulo, Resumen, AnioPublicacion, PalabrasClave, 
                             RutaArchivoPDF, UsuarioAgregaID, CarreraID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        sql_insert_autor_p = "INSERT INTO Autores (Nombre, Apellido) VALUES (%s, %s);"
        sql_insert_tesis_autores_p = "INSERT INTO TEGAutores (TEGID, AutorID) VALUES (%s, %s);"
        sql_select_autor_p = "SELECT AutorID FROM Autores WHERE Nombre = %s AND Apellido = %s;"
        
        if getattr(config, "DB_MODO_DEMO", False):
            print("[ManagerBaseDeDatos] insertar_nueva_tesis llamado en modo DEMO. No se insertará en BD.")
            return True

        teg_guid = str(uuid.uuid4())
        tesis_data['guid'] = teg_guid

        if getattr(self, "_conector", "odbc") == "pymysql":
            try:
                with pymysql.connect(
                    host=config.DB_SERVER,
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    database=config.DB_NAME,
                    port=int(config.DB_PORT),
                    charset="utf8mb4",
                    autocommit=False,
                ) as conn:
                    with conn.cursor() as cursor:
                        nuevos_ids = []
                        for nombre, apellido in autores_nuevos:
                            cursor.execute(sql_select_autor_p, (nombre, apellido))
                            existente = cursor.fetchone()
                            if existente:
                                nuevos_ids.append(existente[0])
                            else:
                                cursor.execute(sql_insert_autor_p, (nombre, apellido))
                                nuevos_ids.append(cursor.lastrowid)

                        cursor.execute(sql_insert_tesis_p, (
                            teg_guid,
                            tesis_data['titulo'], tesis_data['resumen'], tesis_data['anio'],
                            tesis_data['palabras_clave'], tesis_data['ruta_pdf'],
                            tesis_data['usuario_id'], tesis_data['materia_id']
                        ))
                        tesis_id = cursor.lastrowid

                        todos_autores_ids = autores_existentes + nuevos_ids
                        for autor_id in todos_autores_ids:
                            cursor.execute(sql_insert_tesis_autores_p, (tesis_id, autor_id))

                        conn.commit()
                        return True
            except Exception as ex:
                if 'conn' in locals():
                    conn.rollback()
                messagebox.showerror("Error de Inserción", f"Fallo la inserción del TEG (PyMySQL): {ex}")
                return False
        else:
            if not _PYODBC_DISPONIBLE:
                messagebox.showerror("Error de Inserción", "pyodbc no disponible.")
                return False
            try:
                with pyodbc.connect(self.conn_str) as conn:
                    cursor = conn.cursor()
                    conn.autocommit = False
                    
                    nuevos_ids = []
                    for nombre, apellido in autores_nuevos:
                        cursor.execute(sql_select_autor, nombre, apellido)
                        existente = cursor.fetchone()
                        if existente:
                            nuevos_ids.append(existente[0])
                        else:
                            cursor.execute(sql_insert_autor, nombre, apellido)
                            cursor.execute("SELECT LAST_INSERT_ID();") 
                            nuevo_id = cursor.fetchone()[0]
                            nuevos_ids.append(nuevo_id)
                    
                    cursor.execute(sql_insert_tesis,
                        teg_guid,
                        tesis_data['titulo'], tesis_data['resumen'], tesis_data['anio'], 
                        tesis_data['palabras_clave'], tesis_data['ruta_pdf'], 
                        tesis_data['usuario_id'], tesis_data['materia_id']
                    )
                    cursor.execute("SELECT LAST_INSERT_ID();")
                    tesis_id = cursor.fetchone()[0]
                    
                    
                    todos_autores_ids = autores_existentes + nuevos_ids
                    
                    for autor_id in todos_autores_ids:
                        cursor.execute(sql_insert_tesis_autores, tesis_id, autor_id)
                    
                    conn.commit()
                    return True

            except pyodbc.Error as ex:
                conn.rollback()
                sqlstate = ex.args[0]
                messagebox.showerror("Error de Inserción", 
                                     f"Fallo la inserción del TEG. Cambios deshechos. Código: {sqlstate}")
                return False
            
            finally:
                if 'conn' in locals():
                    conn.autocommit = True

    def eliminar_teg(self, teg_id):
        if getattr(config, "DB_MODO_DEMO", False):
            print("[ManagerBaseDeDatos] eliminar_teg llamado en modo DEMO. No se eliminará nada.")
            return True, None

        ruta_pdf = None
        if getattr(self, "_conector", "odbc") == "pymysql":
            try:
                with pymysql.connect(
                    host=config.DB_SERVER,
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    database=config.DB_NAME,
                    port=int(config.DB_PORT),
                    charset="utf8mb4",
                    autocommit=False,
                ) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT RutaArchivoPDF FROM TEG WHERE TEGID = %s", (teg_id,))
                        row = cursor.fetchone()
                        ruta_pdf = row[0] if row else None
                        cursor.execute("DELETE FROM TEGAutores WHERE TEGID = %s", (teg_id,))
                        cursor.execute("DELETE FROM TEG WHERE TEGID = %s", (teg_id,))
                    conn.commit()
                return True, ruta_pdf
            except Exception as ex:
                messagebox.showerror("Error de Eliminación", f"No se pudo eliminar el TEG (PyMySQL): {ex}")
                return False, None
        else:
            if not _PYODBC_DISPONIBLE:
                messagebox.showerror("Error de Eliminación", "pyodbc no disponible.")
                return False, None
            conn = None
            cursor = None
            try:
                conn = pyodbc.connect(self.conn_str)
                conn.autocommit = False
                cursor = conn.cursor()
                cursor.execute("SELECT RutaArchivoPDF FROM TEG WHERE TEGID = ?", (teg_id,))
                row = cursor.fetchone()
                ruta_pdf = row[0] if row else None
                cursor.execute("DELETE FROM TEGAutores WHERE TEGID = ?", (teg_id,))
                cursor.execute("DELETE FROM TEG WHERE TEGID = ?", (teg_id,))
                conn.commit()
                return True, ruta_pdf
            except pyodbc.Error as ex:
                if conn:
                    conn.rollback()
                sqlstate = ex.args[0]
                messagebox.showerror("Error de Eliminación", f"No se pudo eliminar el TEG. Código: {sqlstate}")
                return False, None
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
    
    def obtener_todas_materias(self):
        sql = "SELECT CarreraID, Nombre FROM Carreras ORDER BY Nombre"
        if getattr(config, "DB_MODO_DEMO", False):
            print("[ManagerBaseDeDatos] obtener_todas_materias (Carreras) en MODO_DEMO. Retornando lista vacía.")
            return []

        if getattr(self, "_conector", "odbc") == "pymysql":
            try:
                with pymysql.connect(
                    host=config.DB_SERVER,
                    user=config.DB_USER,
                    password=config.DB_PASSWORD,
                    database=config.DB_NAME,
                    port=int(config.DB_PORT),
                    charset="utf8mb4",
                ) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(sql)
                        filas = cursor.fetchall()
                        return [(row[0], row[1]) for row in filas]
            except Exception as ex:
                messagebox.showerror("Error de Datos", f"No se pudo obtener Carreras (PyMySQL): {ex}")
                return []

        if not _PYODBC_DISPONIBLE:
            messagebox.showerror("Error de Datos", "pyodbc no disponible.")
            return []

        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                filas = cursor.fetchall()
                return [(row[0], row[1]) for row in filas]
                conn.autocommit = False
                
                nuevos_ids = []
                for nombre, apellido in autores_nuevos:
                    cursor.execute(sql_select_autor, nombre, apellido)
                    existente = cursor.fetchone()
                    if existente:
                        nuevos_ids.append(existente[0])
                    else:
                        cursor.execute(sql_insert_autor, nombre, apellido)
                        cursor.execute("SELECT LAST_INSERT_ID();") 
                        nuevo_id = cursor.fetchone()[0]
                        nuevos_ids.append(nuevo_id)
                
                cursor.execute(sql_insert_tesis,
                    tesis_data['titulo'], tesis_data['resumen'], tesis_data['anio'], 
                    tesis_data['palabras_clave'], tesis_data['ruta_pdf'], 
                    tesis_data['usuario_id'], tesis_data['materia_id']
                )
                cursor.execute("SELECT LAST_INSERT_ID();")
                tesis_id = cursor.fetchone()[0]
                
                
                todos_autores_ids = autores_existentes + nuevos_ids
                
                for autor_id in todos_autores_ids:
                    cursor.execute(sql_insert_tesis_autores, tesis_id, autor_id)
                
                conn.commit()
                return True

        except pyodbc.Error as ex:
            conn.rollback()
            sqlstate = ex.args[0]
            messagebox.showerror("Error de Inserción", 
                                 f"Fallo la inserción del TEG. Cambios deshechos. Código: {sqlstate}")
            return False
            
        finally:
            if 'conn' in locals():
                conn.autocommit = True
    
def obtener_todas_materias(self):
    sql = "SELECT CarreraID, Nombre FROM Carreras ORDER BY Nombre"
    if getattr(config, "DB_MODO_DEMO", False):
        print("[ManagerBaseDeDatos] obtener_todas_materias (Carreras) en MODO_DEMO. Retornando lista vacía.")
        return []

    if getattr(self, "_conector", "odbc") == "pymysql":
        try:
            with pymysql.connect(
                host=config.DB_SERVER,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=config.DB_NAME,
                port=int(config.DB_PORT),
                charset="utf8mb4",
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    filas = cursor.fetchall()
                    return [(row[0], row[1]) for row in filas]
        except Exception as ex:
            messagebox.showerror("Error de Datos", f"No se pudo obtener Carreras (PyMySQL): {ex}")
            return []

    if not _PYODBC_DISPONIBLE:
        messagebox.showerror("Error de Datos", "pyodbc no disponible.")
        return []

    try:
        with pyodbc.connect(self.conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            filas = cursor.fetchall()
            return [(row[0], row[1]) for row in filas]
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        messagebox.showerror("Error de Datos", f"No se pudo obtener Carreras. Código: {sqlstate}")
        return []

def eliminar_teg(self, teg_id):
    if getattr(config, "DB_MODO_DEMO", False):
        print("[ManagerBaseDeDatos] eliminar_teg llamado en modo DEMO. No se eliminará nada.")
        return True, None

    ruta_pdf = None
    if getattr(self, "_conector", "odbc") == "pymysql":
        try:
            with pymysql.connect(
                host=config.DB_SERVER,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=config.DB_NAME,
                port=int(config.DB_PORT),
                charset="utf8mb4",
                autocommit=False,
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT RutaArchivoPDF FROM TEG WHERE TEGID = %s", (teg_id,))
                    row = cursor.fetchone()
                    ruta_pdf = row[0] if row else None
                    cursor.execute("DELETE FROM TEGAutores WHERE TEGID = %s", (teg_id,))
                    cursor.execute("DELETE FROM TEG WHERE TEGID = %s", (teg_id,))
                conn.commit()
            return True, ruta_pdf
        except Exception as ex:
            messagebox.showerror("Error de Eliminación", f"No se pudo eliminar el TEG (PyMySQL): {ex}")
            return False, None
    else:
        if not _PYODBC_DISPONIBLE:
            messagebox.showerror("Error de Eliminación", "pyodbc no disponible.")
            return False, None
        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT RutaArchivoPDF FROM TEG WHERE TEGID = ?", (teg_id,))
                row = cursor.fetchone()
                ruta_pdf = row[0] if row else None
                cursor.execute("DELETE FROM TEGAutores WHERE TEGID = ?", (teg_id,))
                cursor.execute("DELETE FROM TEG WHERE TEGID = ?", (teg_id,))
                conn.commit()
            return True, ruta_pdf
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            messagebox.showerror("Error de Eliminación", f"No se pudo eliminar el TEG. Código: {sqlstate}")
            return False, None
