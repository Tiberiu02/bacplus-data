import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

conn = sqlite3.connect(os.getenv("DB_FILE"))
cur = conn.cursor()

cur.execute("UPDATE institutii SET rank = 1000000")

scoli = cur.execute(
    "SELECT id_scoala, AVG(medie_en) FROM en WHERE an = 2023 AND medie_en is not null GROUP BY id_scoala ORDER BY AVG(medie_en) DESC"
).fetchall()

for i, (id_scoala, medie) in enumerate(scoli):
    cur.execute(
        "UPDATE institutii SET rank = ? WHERE id = ?",
        (i + 1, id_scoala),
    )

print(f"Updated {len(scoli)} scoli.")

licee = cur.execute(
    "SELECT id_liceu, AVG(medie) FROM bac WHERE an = 2023 AND medie is not null GROUP BY id_liceu ORDER BY AVG(medie) DESC"
).fetchall()

for i, (id_liceu, medie) in enumerate(licee):
    cur.execute(
        "UPDATE institutii SET rank = ? WHERE id = ?",
        (i + 1, id_liceu),
    )

print(f"Updated {len(licee)} licee.")

conn.commit()
