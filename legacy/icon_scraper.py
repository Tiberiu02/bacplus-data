import requests
import favicon
import sqlite3
import os
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

conn = sqlite3.connect(os.getenv("DB_FILE"))
cur = conn.cursor()


def scrape_icon(url, name):
    icons = favicon.get(url)

    for i, icon in enumerate(icons):
        filename = "data/icons/{}.{}".format(
            name if i == 0 else name + "_" + str(i), icon.format
        )
        response = requests.get(icon.url, stream=True)
        with open(filename, "wb") as image:
            for chunk in response.iter_content(1024):
                image.write(chunk)

    return True


licee = cur.execute(
    "SELECT id_liceu, website, rank FROM licee WHERE website is not null ORDER BY rank ASC"
).fetchall()

for i, (id_liceu, website, rank) in tqdm(list(enumerate(licee))):
    # if i < 1570:
    #     continue

    tqdm.write(id_liceu + " " + website)
    try:
        scrape_icon(website, id_liceu)
    except Exception as e:
        pass
