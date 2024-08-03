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
