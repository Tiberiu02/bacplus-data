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


def parse_siiir_code(code):
    # The SIIIR code has 10 digits with the following structure:
    # digits 1-2: county code
    # digit 3: institution type (6 for schools)
    # digit 4: 1 = active, 2 = inactive (might change)
    # digit 5: 1 = public, 2 = private, 3 = ucecom (unreliable)
    # digits 6-9: institution code (unique within county)
    # digit 10: control digit

    if code is None:
        return None
    if len(code) != 10:
        raise ValueError(f"Invalid SIIIR code '{code}'")

    def compute_control_digit(code):
        weights = [2, 3, 5, 0, 7, 6, 1, 4, 8]
        digit = sum([int(c) * w for c, w in zip(code, weights)]) % 9
        digit = 9 if digit == 0 else digit
        return str(digit)

    # Fix digits 4 and 5 to ensure consistency

    # 4th digit must be 1
    # (updating control digit is not needed, as the 4th digit has weight 0)
    code = code[:3] + "1" + code[4:]

    # 5th digit cannot be 3 (unreliable)
    if code[4] == "3":
        code = code[:4] + "2" + code[5:]
        code = code[:9] + compute_control_digit(code[:9])

    return code
