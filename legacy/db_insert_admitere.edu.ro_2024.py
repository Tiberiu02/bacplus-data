import re
import psycopg2
import argparse
from dotenv import load_dotenv
from tqdm import tqdm
import os
from judete import get_county_code
from cannonicalize_name import cannonicalize_name
import csv


load_dotenv()


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("year", type=int)
    parser.add_argument("input_path")

    return parser.parse_args()


def parse_grade(s):
    try:
        g = float(s)
        return g if g >= 1 else None
    except:
        return None


def extract_cod_judet(cod_candidat):
    match = re.match(r"^([A-Za-z]+)", cod_candidat)
    if match:
        return match.group(1)
    return None


def insert_data(data):
    global cur, conn

    cur.execute(
        f"update en set medie_adm = u.medie_adm, medie_abs = u.medie_abs, repartizat_id_liceu = u.repartizat_id_liceu, repartizat_specializare = u.repartizat_specializare from (values "
        + ",".join(cur.mogrify("(%s,%s,%s,%s,%s)", x).decode("utf-8") for x in data)
        + f") as u(COD_CANDIDAT,MEDIE_ABS,MEDIE_ADM,REPARTIZAT_ID_LICEU,REPARTIZAT_SPECIALIZARE) where en.AN = {args.year} and en.COD_CANDIDAT = u.COD_CANDIDAT",
    )
    conn.commit()


if __name__ == "__main__":
    args = parse_args()

    print(f"Loading data...")

    file = open(args.input_path, "r", encoding="utf-8", newline="")
    spamreader = csv.reader(file)
    num_rows = sum(
        1 for _ in csv.reader(open(args.input_path, "r", encoding="utf-8", newline=""))
    )

    if os.getenv("DATABASE_URL") is None:
        print("Make sure to specify DATABASE_URL in .env file")
        exit(1)

    print(f"Connecting to database at '{os.getenv('DATABASE_URL')}'")

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    # Remove existing entries
    print(f"Updating {num_rows} entries into database...")

    data_to_insert = []

    seed_candidates = set()

    cur.execute(f"select COD_CANDIDAT from en where AN = {args.year}")
    existing_candidates = set([x[0] for x in cur.fetchall()])

    for row in tqdm(spamreader, total=num_rows, unit="row", desc="Processing rows"):
        # Entry structure:
        #  0: Index
        #  1: Codul candidatului
        #  2: Județul de proveniență
        #  3: Școala de proveniență
        #  4: Renunțare lb. maternă
        #  5: Media la admitere
        #  6: Media EN / TSU
        #  7: Media de absolvire
        #  8: Nota / Media la limba română
        #  9: Nota / Media la matematică
        # 10: Limba maternă
        # 11: Nota / Media la limba maternă
        # 12: Liceul în care a fost repartizat
        # 13: Specializarea la care a fost repartizat

        cod_candidat = row[1]
        id_judet = get_county_code(row[2])
        medie_adm = parse_grade(row[5])
        medie_abs = parse_grade(row[7])
        repartizat_id_liceu = None
        repartizat_specializare = None

        if cod_candidat in seed_candidates:
            print(f"Duplicate entry for {cod_candidat}")
        seed_candidates.add(cod_candidat)
        if medie_adm is None:
            print(f"Invalid grade for {cod_candidat}")
        if cod_candidat not in existing_candidates:
            print(f"Unknown candidate {cod_candidat}")

        if row[12] != "":
            repartizat_id_liceu = cannonicalize_name(
                row[12].split("<br/>")[0], id_judet, id=True
            )
            repartizat_specializare = row[13].split("<br/>")[0].strip()
            repartizat_specializare += " (" + row[13].split("<br/>")[1].split("(")[-1]

        data_to_insert.append(
            (
                cod_candidat,
                medie_abs,
                medie_adm,
                repartizat_id_liceu,
                repartizat_specializare,
            ),
        )

        if len(data_to_insert) >= 500:
            insert_data(data_to_insert)
            data_to_insert = []

    insert_data(data_to_insert)

    conn.commit()
    conn.close()
