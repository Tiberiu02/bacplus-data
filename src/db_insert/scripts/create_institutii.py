import psycopg2
from tqdm import tqdm
import argparse
import json
from dotenv import load_dotenv
import os
from connectors.postgresql import pg_insert
from utils.gpt_name_formatter import format_name_basic
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

cur.execute("SELECT nume, cod_siiir FROM institutii")
institutii = cur.fetchall()
institutii_dict = {row[1]: row[0] for row in institutii}

print(f"Loaded {len(institutii)} institutii")

cur.execute("SELECT cod_siiir_unitate, denumire_lunga_unitate FROM siiir")
siiir = cur.fetchall()
siiir_dict = {row[0]: row for row in siiir}

cur.execute(
    "SELECT unitate_siiir, unitate_nume, unitate_cod_judet FROM en WHERE unitate_siiir IS NOT NULL AND unitate_nume IS NOT NULL AND unitate_cod_judet IS NOT NULL GROUP BY unitate_siiir, unitate_nume, unitate_cod_judet"
)
institutii_en = cur.fetchall()

for siiir, nume, cod_judet in institutii_en:
    if siiir not in institutii_dict:
        print(
            f"Missing school '{nume}' with SIIIR code {siiir} and county code {cod_judet}"
        )
        print(f"Formatted name: {format_name_basic(nume)}")
        cur.execute(
            "INSERT INTO institutii (nume, cod_judet, cod_siiir) VALUES (%s, %s, %s)",
            (nume, cod_judet, siiir),
        )
        print(f"Inserted {nume} into institutii")
        print()

conn.commit()
conn.close()
