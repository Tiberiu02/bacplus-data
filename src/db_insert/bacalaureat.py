import argparse
import json
from dotenv import load_dotenv
import os
from connectors.postgresql import pg_insert
from utils.siiir_codes import compute_siiir_matching, get_siiir_by_name
from utils.parsing import (
    fix_name_encoding,
    parse_cod_candidat,
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
        "specializare",
        "lr_init",
        "lr_cont",
        "limba_materna",
        "lm_init",
        "lm_cont",
        "disciplina_obligatorie",
        "do_init",
        "do_cont",
        "disciplina_alegere",
        "da_init",
        "da_cont",
        "limba_moderna",
        "medie",
        "rezultat",
    ]
    possible_keys = required_keys + [
        "promotie",
        "promotie_anterioara",
        "unitate_siiir",
        "unitate_nume",
        "unitate_cod_judet",
        "sex",
        "clasa",
    ]

    # Check required keys
    for key in required_keys:
        if key not in schema:
            raise ValueError(f"Missing key '{key}' in schema")

    # Check for unknown keys
    for key in schema:
        if key not in possible_keys:
            raise ValueError(f"Unknown key '{key}' in schema")

    # Check promotie
    if not ("promotie" in schema or "promotie_anterioara" in schema):
        raise ValueError("Missing 'promotie' or 'promotie_anterioara' key in schema")
    if "promotie" in schema and "promotie_anterioara" in schema:
        raise ValueError("Both 'promotie' and 'promotie_anterioara' keys in schema")

    # Check unitate
    if not ("unitate_siiir" in schema or "unitate_nume" in schema):
        raise ValueError("Missing 'unitate_siiir' or 'unitate_nume' key in schema")
    if "unitate_siiir" in schema and "unitate_nume" in schema:
        raise ValueError("Both 'unitate_siiir' and 'unitate_nume' keys in schema")
    if "unitate_siiir" in schema and "unitate_cod_judet" in schema:
        raise ValueError("Both 'unitate_siiir' and 'unitate_cod_judet' keys in schema")
    if "unitate_nume" in schema and not "unitate_cod_judet" in schema:
        raise ValueError(
            "Key 'unitate_cod_judet' required when 'unitate_nume' is present in schema"
        )

    return schema


parser = argparse.ArgumentParser()
parser.add_argument("year", type=int)
parser.add_argument("data_file", type=str)
parser.add_argument("schema_file", type=str)
parser.add_argument("--detect-siiir", action="store_true")
args = parser.parse_args()

schema = load_schema(args.schema_file)
rows = load_data_file(args.data_file)


def parse_row_bac(row, schema, an):
    cod_candidat = parse_cod_candidat(row[schema["cod_candidat"]])
    specializare = row[schema["specializare"]]

    clasa = row[schema["clasa"]] if "clasa" in schema else None

    sex = parse_sex(row[schema["sex"]]) if "sex" in schema else None

    promotie_anterioara = None
    if "promotie" in schema:
        promotie = row[schema["promotie"]]
        promotie_anterioara = promotie != f"{args.year - 1}-{args.year}"
    else:
        promotie_anterioara = row[schema["promotie_anterioara"]].upper() == "DA"

    unitate_nume = (
        fix_name_encoding(row[schema["unitate_nume"]])
        if "unitate_nume" in schema
        else None
    )
    unitate_cod_judet = (
        row[schema["unitate_cod_judet"]] if "unitate_cod_judet" in schema else None
    )

    unitate_siiir = (
        parse_siiir_code(row[schema["unitate_siiir"]])
        if "unitate_siiir" in schema
        else None
    )

    lr_init = parse_grade(row[schema["lr_init"]])
    lr_cont = parse_grade(row[schema["lr_cont"]])
    lr_final = lr_cont if lr_cont is not None else lr_init

    limba_materna = (
        row[schema["limba_materna"]] if row[schema["limba_materna"]] != "" else None
    )
    lm_init = parse_grade(row[schema["lm_init"]])
    lm_cont = parse_grade(row[schema["lm_cont"]])
    lm_final = lm_cont if lm_cont is not None else lm_init

    disciplina_obligatorie = row[schema["disciplina_obligatorie"]]
    do_init = parse_grade(row[schema["do_init"]])
    do_cont = parse_grade(row[schema["do_cont"]])
    do_final = do_cont if do_cont is not None else do_init

    disciplina_alegere = row[schema["disciplina_alegere"]]
    da_init = parse_grade(row[schema["da_init"]])
    da_cont = parse_grade(row[schema["da_cont"]])
    da_final = da_cont if da_cont is not None else da_init

    limba_moderna = row[schema["limba_moderna"]]

    medie = parse_grade(row[schema["medie"]])
    if (
        lr_final is not None
        and do_final is not None
        and da_final is not None
        and (lm_final is not None or limba_materna is None)
    ):
        sum_grades = sum([lr_final, do_final, da_final, lm_final or 0])
        num_grades = 4 if lm_final is not None else 3

        my_medie = sum_grades / num_grades
        my_medie = (my_medie + 1e-5) // 0.01 / 100

        if medie is not None and medie != my_medie:
            raise ValueError(
                f"Computed average {my_medie} does not match provided average {medie} for candidate {cod_candidat}"
            )
        elif medie is None:
            medie = my_medie

    rezultat = row[schema["rezultat"]].lower()
    if rezultat == "reusit":
        rezultat = "promovat"
    elif rezultat == "respins":
        rezultat = "nepromovat"
    elif rezultat == "neprezentat":
        rezultat = "absent"
    elif rezultat == "eliminat din examen":
        rezultat = "eliminat"
    if rezultat not in ["promovat", "nepromovat", "absent", "eliminat"]:
        raise ValueError(f"Invalid result '{rezultat}' for candidate {cod_candidat}")

    return {
        "an": an,
        "cod_candidat": cod_candidat,
        "sex": sex,
        "specializare": specializare,
        "promotie_anterioara": promotie_anterioara,
        "unitate_siiir": unitate_siiir,
        "unitate_nume": unitate_nume,
        "unitate_cod_judet": unitate_cod_judet,
        "clasa": clasa,
        "lr_init": lr_init,
        "lr_cont": lr_cont,
        "lr_final": lr_final,
        "limba_materna": limba_materna,
        "lm_init": lm_init,
        "lm_cont": lm_cont,
        "lm_final": lm_final,
        "disciplina_obligatorie": disciplina_obligatorie,
        "do_init": do_init,
        "do_cont": do_cont,
        "do_final": do_final,
        "disciplina_alegere": disciplina_alegere,
        "da_init": da_init,
        "da_cont": da_cont,
        "da_final": da_final,
        "limba_moderna": limba_moderna,
        "medie": medie,
        "rezultat": rezultat,
    }


data = [parse_row_bac(row, schema, args.year) for row in rows]

if args.detect_siiir:
    schools = set((row["unitate_nume"], row["unitate_cod_judet"]) for row in data)
    compute_siiir_matching(schools, os.getenv("DATABASE_URL"))
    for row in data:
        if (
            row["unitate_nume"] is not None
            and row["unitate_cod_judet"] is not None
            and row["unitate_siiir"] is None
        ):
            row["unitate_siiir"] = get_siiir_by_name(
                row["unitate_nume"], row["unitate_cod_judet"]
            )

# Insert data into database

pg_insert(
    data,
    "public.bac_new",
    os.getenv("DATABASE_URL"),
    f"an = {args.year}",
)
