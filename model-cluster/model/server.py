from dotenv import load_dotenv
load_dotenv()

from kafka import KafkaConsumer
from fastapi import FastAPI, HTTPException

from persistence.sql_postgres import get_pg_server_connection
from persistence.sql_server import get_sql_server_connection


app = FastAPI()

@app.get("/")
def read_root():
  return {"message": "Welcome to the FastAPI server!"}

@app.get("/postgres/")
def test_postgres_connection():
  try:
    conn = get_pg_server_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT current_database();")
    current_database = cursor.fetchall()
    conn.close()
    return {"postgres_connection": f"Connected to PostgreSQL database: {current_database}"}
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error connecting to PostgreSQL: {e}")
  
@app.get("/sqlserver/")
def test_sql_server_connection():
  try:
    conn = get_sql_server_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    current_database = cursor.fetchall()
    conn.close()
    return {"sql_server_connection": f"Connected to SQL Server database: {current_database}"}
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error connecting to SQL Server: {e}")

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="localhost", port=8000)
