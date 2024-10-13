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

cur.execute("SELECT nume, cod_siiir, sigla FROM institutii")
institutii = cur.fetchall()

print(f"Loaded {len(institutii)} institutii")

cur.execute("SELECT DISTINCT unitate_siiir FROM en")
siiir_en = cur.fetchall()
cur.execute("SELECT DISTINCT unitate_siiir FROM bac")
siiir_bac = cur.fetchall()

siiir_set = set(row[0] for row in siiir_en + siiir_bac)

for nume, cod_siiir, sigla in institutii:
    if cod_siiir not in siiir_set:
        print(f"[{sigla}] Deleting {nume} with SIIIR code {cod_siiir}")
        cur.execute("DELETE FROM institutii WHERE cod_siiir = %s", (cod_siiir,))

conn.commit()
conn.close()
