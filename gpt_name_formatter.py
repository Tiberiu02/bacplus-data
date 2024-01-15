import sqlite3
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import urllib.parse
import time

from unidecode import unidecode
from judete import judete_dupa_cod
from tqdm import tqdm
import random

from unification import cannonicalize_name

load_dotenv()

from openai import OpenAI

client = OpenAI()


def format_name(name, gpt4=False):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo" if not gpt4 else "gpt-4-1106-preview",
        messages=[
            {
                "role": "user",
                "content": "Put the following names of Romanian high schools in the correct format, respecting the diacritics and the use of capital letters. Place a comma between the high school name and the county name, if the county name appears. If abbreviated words appear, do not expand them. Keep the exact form of the words. If some names  Don't remove words. Answer only with the correctly formatted name of the high school.",
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

    # print(response)
    return response.choices[0].message.content


conn = sqlite3.connect(os.getenv("DB_FILE"))
cur = conn.cursor()

licee = cur.execute("SELECT id_liceu, nume_liceu, nume_afisat FROM LICEE").fetchall()

max_licee = 5

for id_liceu, nume_liceu, nume_afisat in tqdm(licee):
    if nume_afisat is not None:
        continue

    cod_judet = id_liceu.split("_")[-1]
    judet = judete_dupa_cod[cod_judet]["nume_complet"]

    print("")
    print(nume_liceu)

    nume_liceu = nume_liceu.replace("RIMNICU", "RAMNICU").replace("RÎMNICU", "RÂMNICU")
    nume_liceu = nume_liceu.replace("TIRGU", "TARGU").replace("TÎRGU", "TÂRGU")

    id_liceu_fix = id_liceu.replace("RIMNICU", "RAMNICU")
    id_liceu_fix = id_liceu_fix.replace("TIRGU", "TARGU")

    nume_bun = format_name(nume_liceu)

    if (cannonicalize_name(nume_bun, cod_judet, id=True)) != id_liceu_fix:
        print(
            f"\nId not equal: {id_liceu_fix} vs {(cannonicalize_name(nume_bun, cod_judet, id=True))}"
        )
        print(nume_bun)

        print("\nTrying GPT-4...")
        nume_bun = format_name(nume_liceu, gpt4=True)

        if (cannonicalize_name(nume_bun, cod_judet, id=True)) != id_liceu_fix:
            print(
                f"\nId still not equal: {id_liceu_fix} vs {(cannonicalize_name(nume_bun, cod_judet, id=True))}"
            )
            print(nume_bun)
            continue

    if nume_bun.count('"') != nume_liceu.count('"'):
        print(f"\nDifferent number of quotes: {nume_liceu} vs {nume_bun}")
        continue

    if nume_bun.count('"') == 2:
        nume_bun = nume_bun.replace('"', "„", 1)
        nume_bun = nume_bun.replace('"', "”", 1)

    print(nume_bun)

    cur.execute(
        f"UPDATE LICEE SET nume_afisat = ? WHERE id_liceu = ?",
        (nume_bun, id_liceu),
    )
    conn.commit()

    max_licee -= 1
    if max_licee <= 0:
        break

# browser.quit()
