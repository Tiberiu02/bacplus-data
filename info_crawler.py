import sqlite3
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import urllib.parse
import time
from judete import judete_dupa_cod
from tqdm import tqdm
import random


load_dotenv()

conn = sqlite3.connect(os.getenv("DB_FILE"))
cur = conn.cursor()

licee = cur.execute("SELECT id_liceu, nume_liceu FROM LICEE").fetchall()

MAPS_URL = "https://www.google.com/maps?output=search&hl=ro&q="
# SEARCH_URL = "https://www.bing.com/search?q="

chrome_options = Options()
chrome_options.add_extension("web-extensions/uBlock-Origin.crx")
browser = webdriver.Chrome(options=chrome_options)

consent = False

for id_liceu, nume_liceu in tqdm(licee):
    address = None
    website = None
    facebook = None
    instagram = None
    wikipedia = None

    cod_judet = id_liceu.split("_")[-1]
    judet = judete_dupa_cod[cod_judet]["nume_complet"]

    try:
        browser.get(MAPS_URL + urllib.parse.quote(nume_liceu + " " + judet))

        if not consent:
            browser.execute_script(
                "document.querySelector(\"form[action='https://consent.google.com/save']\").submit()"
            )
            consent = True

        WebDriverWait(browser, 10).until(
            lambda driver: driver.execute_script(
                "return document.querySelector(\"[data-tooltip='Copiază adresa']\") != null"
            )
        )

        address = browser.execute_script(
            "return document.querySelector(\"[data-tooltip='Copiază adresa']\").innerText"
        )

        website = browser.execute_script(
            "let o = document.querySelector(\"[data-tooltip='Deschide site-ul']\"); return o ? o.getAttribute('href') : null"
        )

    except Exception as e:
        pass

    # browser.get(SEARCH_URL + urllib.parse.quote(nume_liceu + " " + judet))

    # WebDriverWait(browser, 10).until(
    #     lambda driver: driver.execute_script(
    #         "return document.readyState === 'complete'"
    #     )
    # )

    # facebook = browser.execute_script(
    #     "return [...document.querySelectorAll('a')].map(a => a.href).filter(h => h !='').filter(h => new URL(h).host == 'www.facebook.com')[0]"
    # )
    # instagram = browser.execute_script(
    #     "return [...document.querySelectorAll('a')].map(a => a.href).filter(h => h !='').filter(h => new URL(h).host == 'www.instagram.com')[0]"
    # )
    # wikipedia = browser.execute_script(
    #     "return [...document.querySelectorAll('a')].map(a => a.href).filter(h => h !='').filter(h => new URL(h).host == 'ro.wikipedia.org' || new URL(h).host == 'en.wikipedia.org')[0]"
    # )

    # print(id_liceu, facebook, instagram, wikipedia)

    for field, value in [
        ("address", address),
        ("website", website),
        ("facebook", facebook),
        ("instagram", instagram),
        ("wikipedia", wikipedia),
    ]:
        if value is not None:
            cur.execute(
                f"UPDATE LICEE SET {field} = ? WHERE id_liceu = ?",
                (value, id_liceu),
            )
    conn.commit()

# browser.quit()
