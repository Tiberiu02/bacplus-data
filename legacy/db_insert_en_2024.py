import re
import psycopg2
import argparse
from dotenv import load_dotenv
from tqdm import tqdm
import os
from judete import get_county_code
from unification import cannonicalize_name
import csv
from gpt_name_formatter import format_nume_advanced
import time


load_dotenv()


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("year", type=int)
    parser.add_argument("input_path")
    parser.add_argument("--repartizare", action="store_true")
    parser.add_argument("--insert", action="store_true")

    return parser.parse_args()


def parse_grade(s):
    try:
        g = float(s)
        return g if g >= 1 else None
    except:
        return None


def extract_letters(s):
    match = re.match(r"^([A-Za-z]+)", s)
    if match:
        return match.group(1)
    return None


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

    print(f"Connecting to database at '{os.getenv('DB_FILE')}'")

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    # Remove existing entries
    if not args.repartizare or args.insert:
        cur.execute(f"SELECT COUNT(*) FROM en WHERE an = {args.year}")
        cnt = cur.fetchone()[0]
        print(f"Deleting {cnt} entries from database...")
        cur.execute(f"DELETE FROM en WHERE an = {args.year}")

        print(f"Inserting {num_rows} entries into database...")
    else:
        print(f"Updating {num_rows} entries into database...")
        not_found = 0

    scoli = {}
    ix = 0

    data_to_insert = []

    for row in tqdm(spamreader, total=num_rows, unit="row", desc="Processing rows"):
        if not args.repartizare:
            # Entry structure:
            #  0: Index
            #  1: Codul candidatului (AB10004268)
            #  2: Poziţia în ierarhia Evaluare Națională 2024
            #  3: Școala de proveniență
            #     [Limba şi literatura română]
            #  4:   Notă
            #  5:   Contestație
            #  6:   Notă finală
            #     [Matematică]
            #  7:   Notă
            #  8:   Contestație
            #  9:   Notă finală
            #     [Limba şi literatura maternă]
            # 10:   Denumire
            # 11:   Notă
            # 12:   Contestație
            # 13:   Notă finală
            # 14: Media la evaluarea națională

            cod_candidat = row[1]
            id_judet = extract_letters(cod_candidat)
            id_scoala = cannonicalize_name(row[3], id_judet, id=True)
            nume_scoala = cannonicalize_name(row[3], id_judet)
            cod_siiir = None

            lr_final = (
                parse_grade(row[6])
                if parse_grade(row[6]) is not None
                else parse_grade(row[4])
            )

            ma_final = (
                parse_grade(row[9])
                if parse_grade(row[9]) is not None
                else parse_grade(row[7])
            )

            limba_materna = row[10] if row[10] != "-" else None
            lm_final = (
                parse_grade(row[13])
                if parse_grade(row[13]) is not None
                else parse_grade(row[11])
            )

            medie_en = parse_grade(row[14])
            medie_abs = None
            medie_adm = None

            repartizat_id_liceu = None
            repartizat_specializare = None

            medie_adm = medie_en  # Aproximare pentru a putea fi inclusi in ierarhie

        else:
            # Example entry: {'ja': 'AB', 'n': 'AB8583021', 'jp': 'ALBA', 's': 'SEMINARUL TEOLOGIC ORTODOX SFANTUL SIMION STEFAN ALBA IULIA', 'sc': '0161102847', 'madm': '9.22', 'mev': '9.10', 'mabs': '9.74', 'nro': '8.70', 'nmate': '9.50', 'lm': '-', 'nlm': '-', 'h': '<b>COLEGIUL NATIONAL LUCIAN BLAGA SEBES</b><br/>Real/Liceal/Zi', 'sp': '<b>(119) Matematică-Informatică</b><br/>Limba română'}
            cod_candidat = entry["n"]
            id_judet = get_county_code(entry["jp"])
            id_scoala = cannonicalize_name(entry["s"], id_judet, id=True)
            nume_scoala = cannonicalize_name(entry["s"], id_judet)
            cod_siiir = entry["sc"]

            lr_final = parse_grade(entry["nro"])
            ma_final = parse_grade(entry["nmate"])

            limba_materna = entry["lm"] if entry["lm"] != "-" else None
            lm_final = parse_grade(entry["nlm"])

            medie_en = parse_grade(entry["mev"])
            medie_abs = parse_grade(entry["mabs"])
            medie_adm = parse_grade(entry["madm"])

            id_judet_admitere = entry["ja"]
            if entry["h"] != "":
                nume_liceu = (
                    entry["h"].split("<br/>")[0].replace("<b>", "").replace("</b>", "")
                )
                repartizat_id_liceu = cannonicalize_name(
                    nume_liceu, id_judet_admitere, id=True
                )
                repartizat_specializare = (
                    entry["sp"].split("<br/>")[0].replace("<b>", "").replace("</b>", "")
                ).lstrip("() 0123456789")
                if entry["sp"].split("<br/>")[1].count("/") > 0:
                    repartizat_specializare += (
                        " (" + entry["sp"].split("<br/>")[1].split("/")[-1] + ")"
                    )
            else:
                repartizat_id_liceu = None
                repartizat_specializare = None

        # print("Entry:")
        # print(
        #     cod_candidat,
        #     id_judet,
        #     id_scoala,
        #     nume_scoala,
        #     cod_siiir,
        #     lr_final,
        #     ma_final,
        #     limba_materna,
        #     lm_final,
        #     medie_en,
        #     medie_abs,
        #     medie_adm,
        #     repartizat_id_liceu,
        #     repartizat_specializare,
        # )

        if id_scoala not in scoli:
            cur.execute("SELECT COUNT(*) FROM institutii WHERE ID = %s", (id_scoala,))
            cnt = cur.fetchone()[0]

            scoli[id_scoala] = nume_scoala

            if int(cnt) == 0:
                nume_bun = format_nume_advanced(nume_scoala, id_scoala, liceu=False)

                print(f"Adding school {nume_scoala} ({id_scoala}) with name {nume_bun}")

                cur.execute(
                    "INSERT INTO institutii(ID, NUME, LAST_UPDATED, GIMNAZIU) VALUES(%s, %s, %s, 'da')",
                    (id_scoala, nume_bun, round(time.time() * 1000)),
                )
                conn.commit()

        data_to_insert.append(
            (
                args.year,
                cod_candidat,
                id_judet,
                id_scoala,
                lr_final,
                ma_final,
                limba_materna,
                lm_final,
                medie_en,
                medie_abs,
                medie_adm,
                repartizat_id_liceu,
                repartizat_specializare,
            ),
        )

        # action = "INSERT"

        # if args.repartizare and not args.insert:
        #     cnt = cur.execute(
        #         f"SELECT COUNT(*) FROM en WHERE AN = %s AND COD_CANDIDAT = %s",
        #         (args.year, cod_candidat),
        #     ).fetchone()[0]

        #     if int(cnt) == 0:
        #         not_found += 1
        #     else:
        #         action = "UPDATE"

        # if action == "UPDATE":
        #     cur.execute(
        #         f"UPDATE en SET MEDIE_EN = %s, MEDIE_ABS = %s, MEDIE_ADM = %s, REPARTIZAT_ID_LICEU = %s, REPARTIZAT_SPECIALIZARE = %s WHERE AN = %s AND COD_CANDIDAT = %s",
        #         (
        #             medie_en,
        #             medie_abs,
        #             medie_adm,
        #             repartizat_id_liceu,
        #             repartizat_specializare,
        #             args.year,
        #             cod_candidat,
        #         ),
        #     )
        # else:
        #     cur.execute(
        #         f"INSERT INTO en(AN,COD_CANDIDAT,ID_JUDET,ID_SCOALA,LR_FINAL,MA_FINAL,LIMBA_MATERNA,LM_FINAL,MEDIE_EN,MEDIE_ABS,MEDIE_ADM,REPARTIZAT_ID_LICEU,REPARTIZAT_SPECIALIZARE) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        #         (
        #             args.year,
        #             cod_candidat,
        #             id_judet,
        #             id_scoala,
        #             lr_final,
        #             ma_final,
        #             limba_materna,
        #             lm_final,
        #             medie_en,
        #             medie_abs,
        #             medie_adm,
        #             repartizat_id_liceu,
        #             repartizat_specializare,
        #         ),
        #     )

        if len(data_to_insert) >= 500:
            cur.execute(
                f"INSERT INTO en(AN,COD_CANDIDAT,ID_JUDET,ID_SCOALA,LR_FINAL,MA_FINAL,LIMBA_MATERNA,LM_FINAL,MEDIE_EN,MEDIE_ABS,MEDIE_ADM,REPARTIZAT_ID_LICEU,REPARTIZAT_SPECIALIZARE) VALUES "
                + ",".join(
                    cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", x).decode(
                        "utf-8"
                    )
                    for x in data_to_insert
                )
            )
            conn.commit()
            data_to_insert = []

    cur.execute(
        f"INSERT INTO en(AN,COD_CANDIDAT,ID_JUDET,ID_SCOALA,LR_FINAL,MA_FINAL,LIMBA_MATERNA,LM_FINAL,MEDIE_EN,MEDIE_ABS,MEDIE_ADM,REPARTIZAT_ID_LICEU,REPARTIZAT_SPECIALIZARE) VALUES "
        + ",".join(
            cur.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", x).decode("utf-8")
            for x in data_to_insert
        )
    )

    if args.repartizare:
        print(f"{not_found} entries not found, had to insert them")

    conn.commit()
    conn.close()
