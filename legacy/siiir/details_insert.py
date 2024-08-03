import sqlite3
import os
import dotenv
import json
from tqdm import tqdm

dotenv.load_dotenv()


data = open("data.txt", "r").read().split("\n")

conn = sqlite3.connect(os.getenv("DB_FILE"))
cur = conn.cursor()

for row in tqdm(data):
    if len(row) > 0:
        query = json.loads(row)
        cur.execute(query[0], query[1])

conn.commit()
conn.close()
