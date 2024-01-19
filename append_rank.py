import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

conn = sqlite3.connect(os.getenv("DB_FILE"))
cur = conn.cursor()

licee = cur.execute(
    "SELECT id_liceu, AVG(medie) FROM bac WHERE an = 2023 AND medie is not null GROUP BY id_liceu ORDER BY AVG(medie) DESC"
).fetchall()

cur.execute("UPDATE licee SET rank = 1000000")

for i, (id_liceu, medie) in enumerate(licee):
    cur.execute(
        "UPDATE licee SET rank = ? WHERE id_liceu = ?",
        (i + 1, id_liceu),
    )

conn.commit()

print(f"Updated {len(licee)} licee.")
