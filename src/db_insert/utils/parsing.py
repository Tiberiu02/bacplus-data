import re


def parse_grade(grade):
    try:
        g = float(grade)
        if g >= 1 and g <= 10:
            return g
    except:
        pass
    return None


def parse_sex(sex):
    sex = sex.lower()
    if sex == "masculin":
        sex = "m"
    elif sex == "feminin":
        sex = "f"
    if sex not in ["m", "f"]:
        raise ValueError(f"Invalid sex '{sex}'")
    return sex


def parse_cod_candidat(cod):
    match = re.match(r"([A-Z]*)(\d*)", cod, re.I)
    if match:
        return match.group(2)
    else:
        raise ValueError(f"Invalid cod candidat '{cod}'")


def parse_cod_judet(cod):
    match = re.match(r"([A-Z]*)(\d*)", cod, re.I)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Invalid cod judet '{cod}'")


def fix_name_encoding(nume):
    # Fix encoding issues
    nume = nume.replace("Ăˇ", "Á").replace("Ã¡", "Á")
    nume = nume.replace("Ă©", "É").replace("Ã©", "É")
    nume = (
        nume.replace("Ĺ‘", "Ő")
        .replace("Å‘", "Ő")
        .replace("Ã¶", "Ö")
        .replace("Ă¶", "Ö")
        .replace("Ăł", "Ó")
        .replace("Ã³", "Ó")
    )
    nume = nume.replace("â€™", "'").replace("Â€™", "'")

    # Unify quotes
    nume = nume.replace("’", "'").replace("‘", "'")
    nume = (
        nume.replace("''", '"')
        .replace(",,", '"')
        .replace("„", '"')
        .replace("”", '"')
        .replace("“", '"')
        .replace('""', '"')
    )
    nume = nume.replace("'", '"')
    if nume.count('"') != 0 and nume.count('"') != 2:
        nume = nume.replace('"', "")

    # Fix Romanian diacritics
    for a, b in [("Ş", "Ș"), ("Ţ", "Ț")]:
        nume = nume.replace(a, b)
        nume = nume.replace(a.lower(), b.lower())

    return nume
