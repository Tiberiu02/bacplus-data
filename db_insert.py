import re
import sqlite3
import argparse
import unidecode
import load_dotenv
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("year", type=int)
    parser.add_argument("input_path")
    parser.add_argument("--input_schema", default="meta/edu-initial.schema.csv")
    parser.add_argument("--dot_gov", action="store_true")
    parser.add_argument("--siiir", default="meta/siiir.csv")
    parser.add_argument("--siiir_schema", default="meta/siiir.schema.csv")
    parser.add_argument("--sirues", default="meta/sirues.csv")
    parser.add_argument("--sirues_schema", default="meta/sirues.schema.csv")
    parser.add_argument("--preserve_existing_db_entries", action="store_true")
    parser.add_argument("--preserve_existing_licee", action="store_true")

    return parser.parse_args()


def load_schema(schema_file):
    schema = []

    with open(schema_file, "r") as f:
        for ix, line in enumerate(f.read().strip("\n").split("\n")):
            el = line.split(",")
            if len(el) != 2:
                raise Exception(
                    f"Error while parsing chema file '{schema_file}' at line {ix + 1}, expected 2 values, but found {el}"
                )

            name, type = el

            if len(name) == 0:
                raise Exception(
                    f"Error while parsing chema file '{schema_file}' at line {ix + 1}, empty name"
                )
            if type not in ["str", "num"]:
                raise Exception(
                    f"Error while parsing chema file '{schema_file}' at line {ix + 1}, unknown type '{type}'. Possible types: 'str', 'num'"
                )

            schema.append((name, type))

    return schema


def load_data(data_file, schema_file):
    schema = load_schema(schema_file)

    data = []

    with open(data_file, "r", encoding="utf-8") as f:
        for ix, line in enumerate(f.read().strip("\n").split("\n")):
            el = line.split("\t")

            if len(el) != len(schema):
                raise Exception(
                    f"Error while parsing data file '{data_file}' at line {ix + 1}, expected {len(schema)} values, but found {len(el)}"
                )

            entry = {}

            for (name, type), value in zip(schema, el):
                if type == "num":
                    try:
                        entry[name] = float(value)
                    except:
                        entry[name] = None
                elif type == "str":
                    entry[name] = value.strip()

            data.append(entry)

    return data


def get_county_code(county_name):
    counties = [
        ("AB", "ALBA"),
        ("AG", "ARGES"),
        ("AR", "ARAD"),
        ("B", "BUCURESTI"),
        ("BC", "BACAU"),
        ("BH", "BIHOR"),
        ("BN", "BISTRITA"),
        ("BR", "BRAILA"),
        ("BT", "BOTOSANI"),
        ("BV", "BRASOV"),
        ("BZ", "BUZAU"),
        ("CJ", "CLUJ"),
        ("CL", "CALARASI"),
        ("CS", "CARAS"),
        ("CT", "CONSTANTA"),
        ("CV", "COVASNA"),
        ("DB", "DAMBOVITA"),
        ("DJ", "DOLJ"),
        ("GJ", "GORJ"),
        ("GL", "GALATI"),
        ("GR", "GIURGIU"),
        ("HD", "HUNEDOARA"),
        ("HR", "HARGHITA"),
        ("IF", "ILFOV"),
        ("IL", "IALOMITA"),
        ("IS", "IASI"),
        ("MH", "MEHEDINTI"),
        ("MM", "MARAMURES"),
        ("MS", "MURES"),
        ("NT", "NEAMT"),
        ("OT", "OLT"),
        ("PH", "PRAHOVA"),
        ("SB", "SIBIU"),
        ("SJ", "SALAJ"),
        ("SM", "SATU"),
        ("SV", "SUCEAVA"),
        ("TL", "TULCEA"),
        ("TM", "TIMIS"),
        ("TR", "TELEORMAN"),
        ("VL", "VALCEA"),
        ("VN", "VRANCEA"),
        ("VS", "VASLUI"),
    ]

    name = unidecode.unidecode(county_name).upper()

    for code, county in counties:
        if county in name:
            return code

    raise Exception(f"Unknown county {name}")


def process_dot_gov(data, args):
    siiir = load_data(args.siiir, args.siiir_schema)
    sirues = load_data(args.sirues, args.sirues_schema)

    school_name_by_siiir = {int(el["cod_siiir"]): el["nume_unitate"] for el in siiir}
    county_by_siiir = {
        int(el["cod_siiir"]): get_county_code(el["judet"]) for el in siiir
    }

    school_name_by_sirues = {
        int(el["cod_sirues"]): el["nume_unitate"]
        for el in sirues
        if el["cod_sirues"] != ""
    }
    county_by_sirues = {
        int(el["cod_sirues"]): get_county_code(el["judet"])
        for el in sirues
        if el["cod_sirues"] != ""
    }

    bad_codes = 0
    for el in data:
        el["promotie_anterioara"] = (
            "NU" if el["promotie"] == f"{args.year - 1}-{args.year}" else "NU"
        )

        for x in ["lr", "lm", "do", "da"]:
            if x + "_contestatie" in el and el[x + "_contestatie"] != None:
                el[x + "_final"] = el[x + "_contestatie"]
            elif x + "_initial" in el:
                el[x + "_final"] = el[x + "_initial"]
            else:
                el[x + "_final"] = None

        if int(el["siiir"]) in school_name_by_siiir:
            el["liceu"] = school_name_by_siiir[int(el["siiir"])]
            el["judet"] = county_by_siiir[int(el["siiir"])]
        elif el["sirues"] != "" and int(el["sirues"]) in school_name_by_sirues:
            el["liceu"] = school_name_by_sirues[int(el["sirues"])]
            el["judet"] = county_by_sirues[int(el["sirues"])]
        else:
            el["liceu"] = None
            el["judet"] = None
            bad_codes += 1

    print(f"Unknown SIIIR and SIRUES codes for {bad_codes}/{len(data)} entries")


def id_liceu(entry, id=False) -> str:
    liceu = entry["liceu"]
    judet = entry["judet"]

    if liceu is None or judet is None:
        return None

    # Fix encoding issues
    liceu = liceu.replace("Ăˇ", "Á")
    liceu = liceu.replace("Ă©", "É")
    liceu = liceu.replace("Ĺ‘", "Ő").replace("Ă¶", "Ö").replace("Ăł", "Ó")
    liceu = liceu.replace("â€™", "'").replace("Â€™", "'")

    # Unify quotes
    liceu = liceu.replace("’", "'").replace("‘", "'")
    liceu = (
        liceu.replace("''", '"')
        .replace(",,", '"')
        .replace("„", '"')
        .replace("”", '"')
        .replace("“", '"')
        .replace('""', '"')
    )
    liceu = liceu.replace("'", '"')
    if liceu.count('"') != 0 and liceu.count('"') != 2:
        liceu = liceu.replace('"', "")

    # Remove underscores
    liceu = liceu.replace("_", " ")

    if id:
        # Remove non-alphanumeric characters
        liceu = unidecode.unidecode(liceu)
        liceu = re.sub(r"[^a-zA-Z0-9 ]+", " ", liceu)
        # Add county name
        liceu = liceu + " " + judet
    else:
        # Unify Romanian diacritics
        for a, b in [("Ş", "Ș"), ("Ţ", "Ț")]:
            liceu = liceu.replace(a, b)
            liceu = liceu.replace(a.lower(), b.lower())

    # Convert to uppercase
    liceu = liceu.upper()

    # Fix whitespaces
    liceu = re.sub(r" +", " ", liceu)
    liceu = liceu.strip()

    if id:
        # Replace spaces with underscores
        liceu = liceu.replace(" ", "_")

    return liceu


def rezultat_final(s):
    s = unidecode.unidecode(s).upper()

    if "ABSENT" == s or "NEPREZENTAT" == s:
        return "ABSENT"
    elif "RESPINS" == s or "NEPROMOVAT" == s:
        return "RESPINS"
    elif "ELIMINAT" == s or "ELIMINAT DIN EXAMEN" == s:
        return "ELIMINAT"
    elif "ADMIS" == s or "PROMOVAT" == s or "REUSIT" == s:
        return "REUSIT"
    else:
        raise Exception(f"Unknown result {s}")


if __name__ == "__main__":
    args = parse_args()

    print(f"Loading data...")

    data = load_data(args.input_path, args.input_schema)

    if args.dot_gov:
        process_dot_gov(data, args)

    print(f"Loaded {len(data)} entries!")

    load_dotenv.load_dotenv()

    conn = sqlite3.connect(os.getenv("DB_FILE"))
    cur = conn.cursor()

    if not args.preserve_existing_db_entries:
        cnt = cur.execute(
            f"SELECT COUNT(*) FROM elevi WHERE an = {args.year}"
        ).fetchone()[0]
        print(f"Deleting {cnt} entries from database...")
        cur.execute(f"DELETE FROM elevi WHERE an = {args.year}")

    print(f"Inserting {len(data)} entries into database...")

    licee = {}

    for entry in tqdm(data):
        liceu = id_liceu(entry, id=True)

        if liceu not in licee and liceu is not None:
            cnt = cur.execute(
                f"SELECT COUNT(*) FROM licee WHERE ID_LICEU = ?", (liceu,)
            ).fetchone()[0]
            nume = id_liceu(entry)
            licee[liceu] = nume
            if int(cnt) == 0:
                cur.execute(
                    f"INSERT INTO licee(ID_LICEU,NUME_LICEU) VALUES(?,?)", (liceu, nume)
                )
            elif not args.preserve_existing_db_entries:
                cur.execute(
                    f"UPDATE licee SET NUME_LICEU = ? WHERE ID_LICEU = ?", (nume, liceu)
                )

        rezultat = rezultat_final(entry["rezultat_final"])

        my_medie = None
        if rezultat == "REUSIT" or rezultat == "RESPINS":
            my_medie = (
                entry["lr_final"]
                + entry["do_final"]
                + entry["da_final"]
                + (entry["lm_final"] if entry["lm_final"] is not None else 0)
            ) / (4 if entry["lm_final"] is not None else 3)

        cur.execute(
            f"INSERT INTO elevi(AN,COD_CANDIDAT,ID_JUDET,ID_LICEU,PROMOTIE_ANTERIOARA,SPECIALIZARE,LR_INIT,LR_CONT,LR_FINAL,LM_INIT,LM_CONT,LM_FINAL,LIMBA_MODERNA,DISCIPLINA_OBLIGATORIE,DO_INIT,DO_CONT,DO_FINAL,DISCIPLINA_ALEGERE,DA_INIT,DA_CONT,DA_FINAL,MEDIE,MY_MEDIE,REZULTAT) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                args.year,
                entry["cod_candidat"],
                entry["judet"],
                liceu,
                entry["promotie_anterioara"],
                entry["specializare"],
                entry["lr_initial"],
                entry["lr_contestatie"],
                entry["lr_final"],
                entry["lm_initial"],
                entry["lm_contestatie"],
                entry["lm_final"],
                entry["limba_straina"],
                entry["disciplina_obligatorie"],
                entry["do_initial"],
                entry["do_contestatie"],
                entry["do_final"],
                entry["disciplina_la_alegere"],
                entry["da_initial"],
                entry["da_contestatie"],
                entry["da_final"],
                entry["medie"],
                my_medie,
                rezultat,
            ),
        )
    conn.commit()
    conn.close()
