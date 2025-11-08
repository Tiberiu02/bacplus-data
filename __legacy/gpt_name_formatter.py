import re
import sqlite3
import os
from dotenv import load_dotenv

from tqdm import tqdm

from unification import cannonicalize_name

load_dotenv()

from openai import OpenAI

client = OpenAI()


def gpt_liceu(name, gpt4=False):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo" if not gpt4 else "gpt-4-1106-preview",
        messages=[
            {
                "role": "user",
                "content": "Put the following names of Romanian high schools in the correct format, respecting the diacritics and the use of capital letters. Place a comma between the high school name and the county name, if the county name appears. If abbreviated words appear, do not expand them. Keep the exact form of the words. Don't remove words. Answer only with the correctly formatted name of the high school.",
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
            {"role": "user", "content": name},
        ],
        temperature=0 if not gpt4 else 0.5,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    return response.choices[0].message.content


def gpt_scoala(name, gpt4=False):
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
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo" if not gpt4 else "gpt-4-1106-preview",
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


def name_sanity_check(name, id):
    cod_judet = id.split("_")[-1]

    id_nume = cannonicalize_name(name, cod_judet, id=True)

    # Merge 'A' and 'I' to allow for Î->Â fixes
    id_nume = id_nume.replace("A", "I")
    id = id.replace("A", "I")

    return id_nume == id


def format_name_basic(name):
    # Convert the blacklist to lower case for case-insensitive comparison
    blacklist = ["de", "cu", "din", "von", "cel", "al", "la", "pe", "si", "sau"]

    # Function to capitalize a word if it's not in the blacklist
    def capitalize_word(match):
        word = match.group()
        return word.lower() if word.lower() in blacklist else word.capitalize()

    # Use regular expression to find words and apply the capitalization function
    return re.sub(r"\b\w+\b", capitalize_word, name)


def format_nume_advanced(nume, id, liceu=True):
    nume = nume.replace("RIMNICU", "RAMNICU").replace("RÎMNICU", "RÂMNICU")
    nume = nume.replace("TIRGU", "TARGU").replace("TÎRGU", "TÂRGU")

    id = id.replace("RIMNICU", "RAMNICU")
    id = id.replace("TIRGU", "TARGU")

    nume = format_name_basic(nume)
    # print("\nNume basic:", nume)
    nume_bun = gpt_liceu(nume) if liceu else gpt_scoala(nume)
    # print("Nume GPT:", nume_bun)

    if not name_sanity_check(nume_bun, id):
        # print(f"\nId not equal: {id} vs {nume_bun}")
        print(nume_bun)

        # print("\nTrying GPT-4...")
        nume_bun = gpt_liceu(nume, gpt4=True) if liceu else gpt_scoala(nume, gpt4=True)

        if not name_sanity_check(nume_bun, id):
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
