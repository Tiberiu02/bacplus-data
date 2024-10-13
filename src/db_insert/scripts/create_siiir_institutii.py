import psycopg2
from tqdm import tqdm
import argparse
import json
from dotenv import load_dotenv
import os
from connectors.postgresql import pg_insert
from utils.siiir_codes import compute_siiir_matching, get_siiir_by_name
from utils.parsing import fix_name_encoding, parse_cod_candidat, parse_grade, parse_sex
from utils.dataloader import load_data_file

load_dotenv()

db_url = os.getenv("DATABASE_URL")

if db_url is None:
    print("Make sure to specify DATABASE_URL in .env file")
    exit(1)

conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute("SELECT id, nume, cod_siiir FROM institutii")
institutii = cur.fetchall()

print(f"Loaded {len(institutii)} institutii")


schools = set((row[1], row[0].split("_")[-1]) for row in institutii)
compute_siiir_matching(schools, os.getenv("DATABASE_URL"), True)

institutii = [
    {
        "id": row[0],
        "nume": row[1],
        "stored_siiir": row[2],
        "predicted_siiir": get_siiir_by_name(row[1], row[0].split("_")[-1]),
    }
    for row in institutii
]

# Find exsting duplicates in stored_siiir

institutii_dupa_siiir_stored = {}
for row in institutii:
    if row["stored_siiir"] not in institutii_dupa_siiir_stored:
        institutii_dupa_siiir_stored[row["stored_siiir"]] = []
    institutii_dupa_siiir_stored[row["stored_siiir"]].append(row)

print("Duplicates in stored_siiir:")
for siiir, rows in institutii_dupa_siiir_stored.items():
    if len(rows) > 1 and siiir is not None:
        print(f"Duplicate SIIIR {siiir}:")
        for row in rows:
            print(f"  {row['nume']}")
        print()
if all(
    len(rows) == 1 or siiir is None
    for siiir, rows in institutii_dupa_siiir_stored.items()
):
    print("No duplicates found")

insitutii_dupa_siiir_predicted = {}
for row in institutii:
    if row["predicted_siiir"] not in insitutii_dupa_siiir_predicted:
        insitutii_dupa_siiir_predicted[row["predicted_siiir"]] = []
    insitutii_dupa_siiir_predicted[row["predicted_siiir"]].append(row)

matches = 0

# Find mismatches between stored and predicted SIIIR
for row in institutii:
    predicted_siiir = row["predicted_siiir"]
    stored_siiir = row["stored_siiir"]
    name = row["nume"]
    id = row["id"]
    previous_name = (
        institutii_dupa_siiir_stored.get(predicted_siiir, [])[0]["nume"]
        if predicted_siiir is not None
        and len(institutii_dupa_siiir_stored.get(predicted_siiir, [])) > 0
        else None
    )
    previous_id = (
        institutii_dupa_siiir_stored.get(predicted_siiir, [])[0]["id"]
        if predicted_siiir is not None
        and len(institutii_dupa_siiir_stored.get(predicted_siiir, [])) > 0
        else None
    )

    if stored_siiir is None and predicted_siiir is not None:
        if len(institutii_dupa_siiir_stored.get(predicted_siiir, [])) == 0:
            print(
                f"Predicted SIIIR {predicted_siiir} for {name} ({id}) has no stored match"
            )
            cur.execute(
                "UPDATE institutii SET cod_siiir = %s WHERE id = %s",
                (predicted_siiir, id),
            )
            matches += 1
        else:
            print(
                f"Predicted SIIIR {predicted_siiir} for {name} ({id}) has a stored match"
            )
            print(
                f"Stored SIIIR {stored_siiir} for {name} ({id}) matches {previous_name} ({previous_id})"
            )

conn.commit()
conn.close()

print(f"Found {matches} matches")
