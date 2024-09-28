from fastapi import HTTPException
from  psycopg2 import OperationalError
import psycopg2
import os

# Configuración de PostgreSQL
PG_SERVER_USER = os.getenv("PG_USERNAME")
PG_SERVER_PASSWORD = os.getenv("PG_PASSWORD")
PG_SERVER_HOST = os.getenv("PG_SERVER")
PG_SERVER_PORT = os.getenv("PG_PORT", "5432")
PG_SERVER_DB = os.getenv("PG_DATABASE")

def get_pg_server_connection():
  try:
    conn = psycopg2.connect(
      host=PG_SERVER_HOST,
      dbname=PG_SERVER_DB,
      user=PG_SERVER_USER,
      password=PG_SERVER_PASSWORD,
      port=PG_SERVER_PORT,
    )
    print("Conexión exitosa")
    return conn
  except OperationalError as e:
    print(f"Error al conectar: {e}")
    return None


def test_postgres_connection():
  try:
    conn = get_pg_server_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    current_database = cursor.fetchall()
    conn.close()
    print({"postgres_connection": f"Connected to PostgreSQL database: {current_database}"})
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error connecting to PostgreSQL: {e}")