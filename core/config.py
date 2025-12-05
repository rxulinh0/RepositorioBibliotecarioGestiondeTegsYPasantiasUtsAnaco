import os

DB_NAME = "BibliotecaMariaDB"


MARIADB_ODBC_DRIVER = "MariaDB ODBC 3.1 Driver"
DB_SERVER = "127.0.0.1"
DB_PORT = "3306"
DB_USER = "root"
DB_PASSWORD = "4321"

SQL_SERVER_CONNECTION_STRING = (
    f"Driver={{{MARIADB_ODBC_DRIVER}}};"
    f"Server={DB_SERVER};"
    f"Port={DB_PORT};"
    f"Database={DB_NAME};"
    f"UID=root;"
    f"PWD=4321;"
    f"Option=3;"
)

APP_THEME = "blue"
APP_APPEARANCE = "System"
RUTA_BASE_TESIS = os.path.expanduser("C:\\Users\\z0wq\\Desktop\\RepoTesis")

DB_MODO_DEMO = False

DB_CONNECTOR = "pymysql"