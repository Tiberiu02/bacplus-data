import re
import sqlite3
import os
import unidecode
from dotenv import load_dotenv

from tqdm import tqdm

# from unification import cannonicalize_name

load_dotenv()

from openai import OpenAI

client = OpenAI()


def cannonicalize_name(liceu, cod_judet, id=False) -> str:
    if liceu is None or cod_judet is None:
        return None

    # Fix encoding issues
    liceu = liceu.replace("Ăˇ", "Á").replace("Ã¡", "Á")
    liceu = liceu.replace("Ă©", "É").replace("Ã©", "É")
    liceu = (
        liceu.replace("Ĺ‘", "Ő")
        .replace("Å‘", "Ő")
        .replace("Ã¶", "Ö")
        .replace("Ă¶", "Ö")
        .replace("Ăł", "Ó")
        .replace("Ã³", "Ó")
    )
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


def gpt_liceu(name):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": "Put the following names of Romanian high schools in the correct format, respecting the diacritics and the use of capital letters. If the school name contains the name of a person, surround it with quotes. Place a comma between the high school name and the county name, if the county name appears. If abbreviated words appear, do not expand them. Keep the exact form of the words. Don't remove words. Answer only with the correctly formatted name of the high school.",
            },
            {"role": "user", "content": "COLEGIUL NATIONAL, IASI"},
            {"role": "assistant", "content": "Colegiul Național, Iași"},
            {"role": "user", "content": 'LICEUL TEORETIC "SFANTUL IOSIF" ALBA IULIA'},
            {
                "role": "assistant",
                "content": 'Liceul Teoretic "Sfântul Iosif", Alba Iulia',
            },
            {"role": "user", "content": "LICEUL TEHNOLOGIC MOTRU"},
            {"role": "assistant", "content": "Liceul Tehnologic Motru"},
            {
                "role": "user",
                "content": 'COLEGIUL NATIONAL "PREPARANDIA-DIMITRIE TICHINDEAL" ARAD',
            },
            {
                "role": "assistant",
                "content": 'Colegiul Național "Preparandia-Dimitrie Țichindeal", Arad',
            },
            {
                "role": "user",
                "content": 'LICEUL "TIMOTEI CIPARIU" DUMBRĂVENI',
            },
            {
                "role": "assistant",
                "content": 'Liceul "Timotei Cipariu", Dumbrăveni',
            },
            {
                "role": "user",
                "content": 'LICEUL TEORETIC DE INFORMATICA "GHEORGHE SINCAI", IASI',
            },
            {
                "role": "assistant",
                "content": 'Liceul Teoretic de Informatică "Gheorghe Șincai", Iași',
            },
            {
                "role": "user",
                "content": 'SEMINARUL TEOLOGIC ORTODOX "SF. IOAN GURA DE AUR" TARGOVISTE',
            },
            {
                "role": "assistant",
                "content": 'Seminarul Teologic Ortodox "Sf. Ioan Gură de Aur", Târgoviște',
            },
            {
                "role": "user",
                "content": "ȘCOALA GIMNAZIALĂ TEMPFLI JOZSEF URZICENI",
            },
            {
                "role": "assistant",
                "content": 'Școala Gimnazială "Tempfli József", Urziceni',
            },
            {
                "role": "user",
                "content": "SCOALA GIMNAZIALA AVRAM IANCU AVRAM IANCU",
            },
            {
                "role": "assistant",
                "content": 'Școala Gimnazială "Avram Iancu", Avram Iancu',
            },
            {"role": "user", "content": name},
        ],
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    return response.choices[0].message.content


def gpt_scoala(name):
    examples = [
        ["LICEUL TIMOTEI CIPARIU DUMBRĂVENI", 'Liceul "Timotei Cipariu", Dumbrăveni'],
        ["ȘCOALA GIMNAZIALĂ NR. 7 MEDIAȘ", "Școala Gimnazială Nr. 7, Mediaș"],
        ["LICEUL TEHNOLOGIC CISNĂDIE", "Liceul Tehnologic, Cisnădie"],
        [
            "ȘCOALA GIMNAZIALĂ TEMPFLI JOZSEF URZICENI",
            'Școala Gimnazială "Tempfli József", Urziceni',
        ],
        ["ȘCOALA GIMNAZIALĂ, PELEȘ", "Școala Gimnazială, Peleș"],
        [
            "SCOALA GIMNAZIALA AVRAM IANCU AVRAM IANCU",
            'Școala Gimnazială "Avram Iancu", Avram Iancu',
        ],
        [
            "LICEUL TEHNOLOGIC COMUNA RUŞEŢU",
            "Liceul Tehnologic, comuna Rușețu",
        ],
    ]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": "Put the following names of Romanian schools in the correct format. Place a comma between the school name and the location, if the location appears. If the school name contains the name of a person, surround it with quotes. If abbreviated words appear, do not expand them. Keep the exact form of the words. Don't remove words. Surround names of people with quotes. Answer only with the correctly formatted name of the school.",
            },
            *sum(
                [
                    [
                        {"role": "user", "content": format_name_basic(ex[0])},
                        {"role": "assistant", "content": ex[1]},
                    ]
                    for ex in examples
                ],
                [],
            ),
            {"role": "user", "content": name},
        ],
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    return response.choices[0].message.content


def name_sanity_check(name, baseline):
    id_nume = cannonicalize_name(name, "X", id=True)
    id_baseline = cannonicalize_name(baseline, "X", id=True)

    # Merge 'A' and 'I' to allow for Î->Â fixes
    id_nume = id_nume.replace("_", "").replace("A", "I")
    id_baseline = id_baseline.replace("_", "").replace("A", "I")

    return id_nume == id_baseline


def format_name_basic(name):
    # Fix old-style diacritics
    name = name.upper()
    name = name.replace("RIMNICU", "RÂMNICU").replace("RÎMNICU", "RÂMNICU")
    name = name.replace("TIRGU", "TÂRGU").replace("TÎRGU", "TÂRGU")

    # Fix encoding issues
    name = cannonicalize_name(name, "", id=False)

    # Convert the blacklist to lower case for case-insensitive comparison
    blacklist = [
        "de",
        "cu",
        "din",
        "von",
        "cel",
        "al",
        "la",
        "pe",
        "și",
        "sau",
        "II",
        "III",
        "IV",
    ]

    # Function to capitalize a word if it's not in the blacklist
    def capitalize_word(match):
        word = match.group()
        blacklist_match = None
        for blacklisted_word in blacklist:
            if unidecode.unidecode(word.lower()) == unidecode.unidecode(
                blacklisted_word.lower()
            ):
                blacklist_match = blacklisted_word

        return blacklist_match if blacklist_match is not None else word.capitalize()

    # Use regular expression to find words and apply the capitalization function
    name = re.sub(r"\b\w+\b", capitalize_word, name)

    # Beautify the quotes
    if name.count('"') == 2:
        name = name.replace('"', "„", 1)
        name = name.replace('"', "”", 1)

    return name


def format_nume_advanced(nume, liceu=True):
    nume_initial = nume

    nume = (
        nume.replace("RIMNICU", "RÂMNICU")
        .replace("RÎMNICU", "RÂMNICU")
        .replace("Rîmnicu", "Râmnicu")
        .replace("Rimnicu", "Râmnicu")
    )
    nume = (
        nume.replace("TIRGU", "TÂRGU")
        .replace("TÎRGU", "TÂRGU")
        .replace("Tîrgu", "Târgu")
        .replace("Tirgu", "Târgu")
    )

    nume = format_name_basic(nume)
    # print("\nNume basic:", nume)
    nume_bun = gpt_liceu(nume.upper()) if liceu else gpt_scoala(nume.upper())
    # print("Nume GPT:", nume_bun)

    if not name_sanity_check(nume_bun, nume_initial):
        print(f"\nId still not equal: {id} vs {nume_bun}")
        print(nume_bun)

        print("\nUsing symbolic formatter...")
        nume_bun = format_name_basic(nume)

    if nume_bun.count('"') == 2:
        nume_bun = nume_bun.replace('"', "„", 1)
        nume_bun = nume_bun.replace('"', "”", 1)

    return nume_bun


def format_scoli_all():
    conn = sqlite3.connect(os.getenv("DB_FILE"))
    cur = conn.cursor()

    scoli = cur.execute(
        "SELECT id_scoala, nume_scoala, nume_afisat FROM SCOLI"
    ).fetchall()

    for id_scoala, nume_scoala, nume_afisat in tqdm(scoli):
        if nume_afisat is not None:
            continue

        liceu = cur.execute(
            "SELECT nume_afisat FROM LICEE WHERE id_liceu = ?",
            (id_scoala,),
        ).fetchone()

        if liceu is not None and liceu[0] is not None:
            nume_bun = liceu[0]
        else:
            nume_bun = format_nume_advanced(nume_scoala, id_scoala, liceu=False)

        cur.execute(
            f"UPDATE SCOLI SET nume_afisat = ? WHERE id_scoala = ?",
            (nume_bun, id_scoala),
        )
        conn.commit()


if __name__ == "__main__":
    format_scoli_all()
