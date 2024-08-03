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


conn = sqlite3.connect(os.getenv("DB_FILE"))
cur = conn.cursor()

scoli = cur.execute("SELECT id_scoala, nume_scoala FROM SCOLI").fetchall()

for id_scoala, nume_scoala in scoli:
    print(nume_scoala)

# browser.quit()
