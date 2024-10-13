import argparse
import json
import re
from dotenv import load_dotenv
import os

from unidecode import unidecode
from connectors.postgresql import pg_insert
from utils.siiir_codes import compute_siiir_matching, get_siiir_by_name
from utils.parsing import (
    parse_cod_candidat,
    parse_cod_judet,
    parse_grade,
    parse_sex,
    parse_siiir_code,
)
from utils.dataloader import load_data_file

load_dotenv()


def load_schema(filename):
    print("Loading schema...")
    schema = json.load(open(filename, "r", encoding="utf-8"))

    required_keys = [
        "cod_candidat",
    ]
    possible_keys = required_keys + [
        "sex",
        "lr_init",
        "lr_cont",
        "limba_materna",
        "lm_init",
        "lm_cont",
        "ma_init",
        "ma_cont",
        "medie_en",
        "medie_abs",
        "medie_adm",
        "unitate_siiir",
        "unitate_nume",
        "unitate_cod_judet",
        "repartizat_liceu_nume",
        "repartizat_specializare",
        "repartizat_cod_judet",
    ]

    # Check required keys
    for key in required_keys:
        if key not in schema:
            raise ValueError(f"Missing key '{key}' in schema")

    # Check for unknown keys
    for key in schema:
        if key not in possible_keys:
            raise ValueError(f"Unknown key '{key}' in schema")

    # Check unitate
    if not ("unitate_siiir" in schema or "unitate_nume" in schema):
        raise ValueError("Missing 'unitate_siiir' or 'unitate_nume' key in schema")
    if "unitate_nume" in schema and not "unitate_cod_judet" in schema:
        raise ValueError(
            "Key 'unitate_cod_judet' required when 'unitate_nume' is present in schema"
        )

    return schema


parser = argparse.ArgumentParser()
parser.add_argument("year", type=int)
parser.add_argument("data_file", type=str)
parser.add_argument("schema_file", type=str)
parser.add_argument("--update-existing", action="store_true")
parser.add_argument("--detect-siiir", action="store_true")
parser.add_argument("--detect-siiir-repartizare", action="store_true")
args = parser.parse_args()

schema = load_schema(args.schema_file)
rows = load_data_file(args.data_file)


def parse_row(row, schema, an):
    cod_candidat = parse_cod_candidat(row[schema["cod_candidat"]])

    sex = parse_sex(row[schema["sex"]]) if "sex" in schema else None

    unitate_siiir = (
        parse_siiir_code(row[schema["unitate_siiir"]])
        if "unitate_siiir" in schema
        else None
    )
    unitate_nume = row[schema["unitate_nume"]] if "unitate_nume" in schema else None
    unitate_cod_judet = (
        parse_cod_judet(row[schema["unitate_cod_judet"]])
        if "unitate_cod_judet" in schema
        else None
    )

    lr_init = parse_grade(row[schema["lr_init"]]) if "lr_init" in schema else None
    lr_cont = parse_grade(row[schema["lr_cont"]]) if "lr_cont" in schema else None
    lr_final = lr_cont if lr_cont is not None else lr_init

    limba_materna = row[schema["limba_materna"]] if "limba_materna" in schema else None
    if limba_materna == "-":
        limba_materna = None
    lm_init = parse_grade(row[schema["lm_init"]]) if "lm_init" in schema else None
    lm_cont = parse_grade(row[schema["lm_cont"]]) if "lm_cont" in schema else None
    lm_final = lm_cont if lm_cont is not None else lm_init

    ma_init = parse_grade(row[schema["ma_init"]]) if "ma_init" in schema else None
    ma_cont = parse_grade(row[schema["ma_cont"]]) if "ma_cont" in schema else None
    ma_final = ma_cont if ma_cont is not None else ma_init

    medie_en = parse_grade(row[schema["medie_en"]]) if "medie_en" in schema else None
    if (
        lr_final is not None
        and ma_final is not None
        and (lm_final is not None or limba_materna is None)
    ):
        sum_grades = sum([lr_final, ma_final, lm_final or 0])
        num_grades = 3 if lm_final is not None else 2

        my_medie = sum_grades / num_grades
        my_medie = (my_medie + 1e-5) // 0.01 / 100

        if medie_en is not None and medie_en != my_medie:
            raise ValueError(
                f"Computed average {my_medie} does not match provided average {medie_en} for candidate {cod_candidat}"
            )
        elif medie_en is None:
            medie_en = my_medie

    medie_abs = parse_grade(row[schema["medie_abs"]]) if "medie_abs" in schema else None
    medie_adm = parse_grade(row[schema["medie_adm"]]) if "medie_adm" in schema else None

    repartizat_liceu_nume = (
        (
            row[schema["repartizat_liceu_nume"]]
            .replace("<b>", "")
            .replace("</b>", "")
            .split("<br/>")[0]
        )
        if "repartizat_liceu_nume" in schema
        else None
    )
    specializare = (
        row[schema["repartizat_specializare"]]
        if "repartizat_specializare" in schema
        else None
    )
    repartizat_cod_judet = (
        row[schema["repartizat_cod_judet"]]
        if "repartizat_cod_judet" in schema
        else None
    )

    if specializare is not None and specializare.lower() == "nerepartizat":
        specializare = None
    if specializare is not None:
        specializare = specializare.replace("<b>", "").replace("</b>", "")
        id_specializare = re.search(r"(\(\d+\))", specializare).group(1)
        specializare = specializare.replace(id_specializare, "")
        specializare, limba = specializare.split("<br/>")
        specializare = specializare.strip()
        if limba.count("/") > 0:
            specializare = specializare + ", " + limba.split("/")[-1].strip()
        specializare = id_specializare + " " + specializare

    return {
        "an": an,
        "cod_candidat": cod_candidat,
        "sex": sex,
        "unitate_siiir": unitate_siiir,
        "unitate_nume": unitate_nume,
        "unitate_cod_judet": unitate_cod_judet,
        "lr_init": lr_init,
        "lr_cont": lr_cont,
        "lr_final": lr_final,
        "limba_materna": limba_materna,
        "lm_init": lm_init,
        "lm_cont": lm_cont,
        "lm_final": lm_final,
        "ma_init": ma_init,
        "ma_cont": ma_cont,
        "ma_final": ma_final,
        "medie_en": medie_en,
        "medie_abs": medie_abs,
        "medie_adm": medie_adm,
        "repartizat_liceu_nume": repartizat_liceu_nume,
        "repartizat_specializare": specializare,
        "repartizat_cod_judet": repartizat_cod_judet,
    }


data = [parse_row(row, schema, args.year) for row in rows]

if args.detect_siiir:
    print("Detecting SIIIRs for provenence school")
    schools = set((row["unitate_nume"], row["unitate_cod_judet"]) for row in data)
    compute_siiir_matching(schools, os.getenv("DATABASE_URL"), True)
    for row in data:
        if (
            row["unitate_nume"] is not None
            and row["unitate_cod_judet"] is not None
            and row["unitate_siiir"] is None
        ):
            row["unitate_siiir"] = get_siiir_by_name(
                row["unitate_nume"], row["unitate_cod_judet"]
            )

if args.detect_siiir_repartizare:
    print("Detecting SIIIRs for repartizare school")
    schools = set(
        (row["repartizat_liceu_nume"], row["repartizat_cod_judet"])
        for row in data
        if row["repartizat_liceu_nume"] is not None
        and row["repartizat_cod_judet"] is not None
    )
    compute_siiir_matching(schools, os.getenv("DATABASE_URL"), True)
    for row in data:
        if (
            row["repartizat_liceu_nume"] is not None
            and row["repartizat_cod_judet"] is not None
        ):
            row["repartizat_liceu_siiir"] = get_siiir_by_name(
                row["repartizat_liceu_nume"], row["repartizat_cod_judet"]
            )

# Insert data into database

pg_insert(
    data,
    "en_new",
    os.getenv("DATABASE_URL"),
    f"en_new.an = {args.year}",
    "cod_candidat" if args.update_existing else None,
)
