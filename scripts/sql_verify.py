import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT")
)

cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM analytics.training_lift_day;")
row = cur.fetchone()
if row is None:
    raise RuntimeError("No result returned from COUNT query.")
print("Rows:", row[0])

cur.close()
conn.close()