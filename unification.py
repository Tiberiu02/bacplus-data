import re
import unidecode


def cannonicalize_name(liceu, cod_judet, id=False) -> str:
    if liceu is None or cod_judet is None:
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
        liceu = liceu + " " + cod_judet
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
