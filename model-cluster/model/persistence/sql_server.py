import pymssql
import os

# Configuración de SQL Server
SQL_SERVER_HOST = os.getenv("SQL_SERVER")
SQL_SERVER_DATABASE = os.getenv("SQL_DATABASE")
SQL_SERVER_USERNAME = os.getenv("SQL_USERNAME")
SQL_SERVER_PASSWORD = os.getenv("SQL_PASSWORD")

def get_sql_server_connection():
  try:
    conn = pymssql.connect(
      server=SQL_SERVER_HOST,
      user=SQL_SERVER_USERNAME,
      password=SQL_SERVER_PASSWORD,
      database=SQL_SERVER_DATABASE
    )
    return conn
  except pymssql.OperationalError as e:
    print(f"Error al conectar: {e}")
    return None