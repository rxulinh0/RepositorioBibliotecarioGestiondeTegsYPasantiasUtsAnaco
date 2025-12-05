# GESTOR DE AUTENTICACIÓN
# ---------------------------------------------------------------------------
# Clase responsable de toda la lógica de inicio de sesión y seguridad.
# ---------------------------------------------------------------------------

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

class ManagerAutenticacion:


    def __init__(self):

        self.conn_str = config.SQL_SERVER_CONNECTION_STRING

        self._conector = getattr(config, "DB_CONNECTOR", "odbc")

        if getattr(config, "DB_MODO_DEMO", False):
            print("[ManagerAutenticacion] MODO_DEMO activo. No se conecta a la BD.")
        elif self._conector == "pymysql" and not _PYMYSQL_DISPONIBLE:
            print("[ManagerAutenticacion] PyMySQL no instalado. Instale con: pip install PyMySQL")
        elif self._conector == "odbc" and not _PYODBC_DISPONIBLE:
            print("[ManagerAutenticacion] pyodbc no está disponible. Ejecutando en modo DEMO sin conexión a BD.")
        else:
            print("AuthManager: Inicializado y listo para conectar.")


    def _obtener_hash_usuario(self, usuario):
        if getattr(config, "DB_MODO_DEMO", False):
            print("[ManagerAutenticacion] _obtener_hash_usuario en modo DEMO. Retornando None.")
            return None

        if getattr(self, "_conector", "odbc") == "pymysql":
            sql = "SELECT ContrasenaHash FROM Usuarios WHERE NombreUsuario = %s"
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
                        cursor.execute(sql, (usuario,))
                        resultado = cursor.fetchone()
                        if resultado:
                            return resultado[0]
                        return None
            except Exception as ex:
                print(f"Error de DB (PyMySQL) al obtener hash: {ex}")
                return None
        else:
            if not _PYODBC_DISPONIBLE:
                print("pyodbc no disponible para autenticación")
                return None
            sql = "SELECT ContrasenaHash FROM Usuarios WHERE NombreUsuario = ?"
            try:
                with pyodbc.connect(self.conn_str) as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql, usuario)
                    resultado = cursor.fetchone()
                    if resultado:
                        return resultado[0]
                    return None
            except pyodbc.Error as ex:
                sqlstate = ex.args[0]
                print(f"Error de DB al obtener hash: {sqlstate}")
                return None


    def verificar_credenciales(self, usuario, password_ingresada):
        
        hash_almacenado = self._obtener_hash_usuario(usuario)
        
        if hash_almacenado is None:
            
            return False

        if password_ingresada == hash_almacenado:
            return True
        
        return False