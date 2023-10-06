import re
import sqlite3
import argparse
import unidecode
from dotenv import load_dotenv
from tqdm import tqdm
import os
from judete import get_county_code
import json
from unification import cannonicalize_name


load_dotenv()


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("year", type=int)
    parser.add_argument("input_path")
    parser.add_argument("--repartizare", action="store_true")

    return parser.parse_args()


def parse_grade(s):
    try:
        g = float(s)
        return g if g >= 1 else None
    except:
        return None


if __name__ == "__main__":
    args = parse_args()

    print(f"Loading data...")

    data = json.loads(open(args.input_path, "r", encoding="utf-8").read())

    print(f"Loaded {len(data)} entries!")

    if os.getenv("DB_FILE") is None:
        print("Make sure to specify DB_FILE in .env file")
        exit(1)

    print(f"Connecting to database at '{os.getenv('DB_FILE')}'")

    conn = sqlite3.connect(os.getenv("DB_FILE"))
    cur = conn.cursor()

    # Remove existing entries
    cnt = cur.execute(f"SELECT COUNT(*) FROM en WHERE an = {args.year}").fetchone()[0]
    print(f"Deleting {cnt} entries from database...")
    cur.execute(f"DELETE FROM en WHERE an = {args.year}")

    print(f"Inserting {len(data)} entries into database...")

    scoli = {}

    for entry in tqdm(data):
        if not args.repartizare:
            # Example entry: {'index': 1, 'county': 'AB', 'name': 'AB8640025', 'school': 'SCOALA GIMNAZIALA AVRAM IANCU ALBA IULIA', 'schoolCode': '0161103405', 'ri': 10, 'ra': None, 'rf': None, 'mi': 10, 'ma': None, 'mf': None, 'lmp': '-', 'lmi': None, 'lma': None, 'lmf': None, 'mev': 10}
            cod_candidat = entry["name"]
            id_judet = entry["county"]
            id_scoala = cannonicalize_name(entry["school"], id_judet, id=True)
            nume_scoala = cannonicalize_name(entry["school"], id_judet)
            cod_siiir = entry["schoolCode"]

            lr_final = (
                parse_grade(entry["rf"])
                if entry["rf"] is not None
                else parse_grade(entry["ri"])
            )

            ma_final = (
                parse_grade(entry["mf"])
                if entry["mf"] is not None
                else parse_grade(entry["mi"])
            )

            limba_materna = entry["lmp"] if entry["lmp"] != "-" else None
            lm_final = (
                parse_grade(entry["lmf"])
                if entry["lmf"] is not None
                else parse_grade(entry["lmi"])
            )

            medie_ev = parse_grade(entry["mev"])
            medie_abs = None
            medie_adm = None

            repartizat_id_liceu = None
            repartizat_specializare = None

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

            medie_ev = parse_grade(entry["mev"])
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

        if id_scoala not in scoli:
            cnt = cur.execute(
                f"SELECT COUNT(*) FROM scoli WHERE ID_SCOALA = ?", (id_scoala,)
            ).fetchone()[0]

            scoli[id_scoala] = nume_scoala
            if int(cnt) == 0:
                cur.execute(
                    f"INSERT INTO scoli(id_scoala,nume_scoala,cod_siiir) VALUES(?,?,?)",
                    (id_scoala, nume_scoala, cod_siiir),
                )
            else:
                cur.execute(
                    f"UPDATE scoli SET nume_scoala = ?, cod_siiir = ? WHERE id_scoala = ?",
                    (nume_scoala, cod_siiir, id_scoala),
                )

        cur.execute(
            f"INSERT INTO en(AN,COD_CANDIDAT,ID_JUDET,ID_SCOALA,LR_FINAL,MA_FINAL,LIMBA_MATERNA,LM_FINAL,MEDIE_EN,MEDIE_ABS,MEDIE_ADM,REPARTIZAT_ID_LICEU,REPARTIZAT_SPECIALIZARE) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                args.year,
                cod_candidat,
                id_judet,
                id_scoala,
                lr_final,
                ma_final,
                limba_materna,
                lm_final,
                medie_ev,
                medie_abs,
                medie_adm,
                repartizat_id_liceu,
                repartizat_specializare,
            ),
        )

    conn.commit()
    conn.close()
