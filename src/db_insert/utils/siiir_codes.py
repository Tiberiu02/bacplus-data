import re
import psycopg2
import unidecode
from Levenshtein import ratio, distance

from utils.parsing import fix_name_encoding


def cannonical_id_from_name(name, cod_judet):
    name = fix_name_encoding(name)

    # Remove underscores
    name = name.replace("_", " ")

    # Remove non-alphanumeric characters
    name = unidecode.unidecode(name)
    name = re.sub(r"[^a-zA-Z0-9 ]+", " ", name)

    # Add county name
    name = cod_judet + " " + name

    # Convert to uppercase
    name = name.upper()

    # Fix whitespaces
    name = re.sub(r" +", " ", name)
    name = name.strip()

    # Replace spaces with underscores
    name = name.replace(" ", "_")

    return name


matching = None


def compute_siiir_matching(source_schools, db_url, gimnaziu=False):

    if db_url is None:
        print("Make sure to specify DATABASE_URL in .env file")
        exit(1)

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    global matching
    matching = {}  # {name: code}

    unmatched_sources = []  # [(name, cod_judet)]
    unmatched_targets = {}  # {cod_judet: {name: code}}

    # Load target schools from database
    cur.execute(
        f"SELECT denumire_lunga_unitate, judet_pj, cod_siiir_unitate FROM bacplus.siiir {"WHERE stare_liceal is not null" if not gimnaziu else ""}"
    )
    for name, cod_judet, cod_siiir in cur.fetchall():
        if cod_judet not in unmatched_targets:
            unmatched_targets[cod_judet] = {}
        name = cannonical_id_from_name(name, cod_judet)
        unmatched_targets[cod_judet][name] = cod_siiir

    # Exact matches
    for name, cod_judet in source_schools:
        name = cannonical_id_from_name(name, cod_judet)
        code = unmatched_targets.get(cod_judet, {}).get(name, None)
        if code is not None:
            matching[name] = code
            unmatched_targets[cod_judet].pop(name)
        else:
            unmatched_sources.append((name, cod_judet))

    # Levenshtein matches
    max_ratios = [0.1, 0.2, 0.3, 0.4] if not gimnaziu else [0.1, 0.2]
    for max_ratio in max_ratios:
        for s_name, s_judet in unmatched_sources[:]:
            if len(unmatched_targets[s_judet]) == 0:
                continue
            best_match = min(
                unmatched_targets[s_judet].keys(),
                key=lambda x: distance(s_name, x),
            )
            ratio = distance(s_name, best_match) / len(s_name)
            if ratio <= max_ratio:
                matching[s_name] = unmatched_targets[s_judet][best_match]
                unmatched_targets[s_judet].pop(best_match)
                unmatched_sources.remove((s_name, s_judet))
                print(
                    f"Found similar school '{best_match}' for '{s_name}' with ratio {ratio:.2f}"
                )

    print("Matched schools:" + str(len(matching)))
    print("Unmatched schools:" + str(len(unmatched_sources)))


def get_siiir_by_name(name, cod_judet):
    if matching is None:
        print("Please run compute_siiir_matching() first")
        exit(1)

    name = cannonical_id_from_name(name, cod_judet)
    code = matching.get(name, None)
    return code
