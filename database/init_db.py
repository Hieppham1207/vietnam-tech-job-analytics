import os

from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    sslmode="require"
)

cursor = conn.cursor()

with open("database/schema.sql", "r", encoding="utf-8") as f:
    sql = f.read()

cursor.execute(sql)

conn.commit()

print("✅ Database initialized successfully!")

cursor.close()
conn.close()