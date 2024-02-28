import sqlite3
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import urllib.parse
from judete import judete_dupa_cod
from tqdm import tqdm
import time


load_dotenv()

conn = sqlite3.connect(os.getenv("DB_FILE"))
cur = conn.cursor()

institutii = cur.execute("SELECT id, nume, adresa, longlat FROM institutii").fetchall()

MAPS_URL = "https://www.google.com/maps?output=search&hl=ro&q="

chrome_options = Options()
chrome_options.add_extension("web-extensions/uBlock-Origin.crx")
browser = webdriver.Chrome(options=chrome_options)

consent = False

# !3m1!4b1!4m6!3m5!1s0x40b202033db033df:0x1cb72daf776fb289!8m2!3d44.4580628!4d26.080109!16s%2Fm%2F0cmcm8k


def try_get_longlat(query):
    try:
        global consent

        browser.get(MAPS_URL + urllib.parse.quote(query))

        if not consent:
            browser.execute_script(
                "document.querySelector(\"form[action='https://consent.google.com/save']\").submit()"
            )
            consent = True

        WebDriverWait(browser, 3).until(
            lambda driver: driver.execute_script(
                "return document.querySelector(\"[data-tooltip='Copiază adresa']\") != null"
            )
        )

        url = browser.current_url
        while not url.count("@") == 1:
            time.sleep(0.1)
            url = browser.current_url
        data = url.split("/data=")[1].split("?")[0]
        long, lat = data.split("!")[7:9]
        long = float(long[2:])
        lat = float(lat[2:])

        time.sleep(0.1)

        return long, lat

    except Exception as e:
        return None, None


for id, nume, adresa, ll in tqdm(institutii):
    if ll is not None:
        continue

    cod_judet = id.split("_")[-1]
    judet = judete_dupa_cod[cod_judet]["nume_complet"]

    try:
        long, lat = try_get_longlat(nume + " " + judet)

        if long is None:
            print(f" Getting by name failed for {id}, trying by address...")
            long, lat = try_get_longlat(adresa + " " + judet)
            if long is None:
                print("Failed by address too, skipping...")

        if long is not None:
            longlat = str(long) + "," + str(lat)
            cur.execute(
                f"UPDATE institutii SET longlat = ? WHERE id = ?",
                (longlat, id),
            )
            conn.commit()

    except Exception as e:
        pass

# browser.quit()
