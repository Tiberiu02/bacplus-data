import re
import sqlite3
import argparse
import unidecode
from dotenv import load_dotenv
from tqdm import tqdm
import os
from judete import judete
from urllib.request import urlopen
import html
import html2text
import json
import openai
import re
import tiktoken
import unidecode
from PyPDF2 import PdfReader
import io
import time
import json


load_dotenv()

URL_REPARTIZARE = (
    "http://static.admitere.edu.ro/%d/repartizare/%s/data/candidate.json?_=%d"
)
URL_REZULTATE = "http://static.evaluare.edu.ro/%d/rezultate/%s/data/candidate.json?_=%d"


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("year", type=int)
    parser.add_argument("output_path")
    parser.add_argument("--repartizare", action="store_true")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.repartizare:
        url = URL_REPARTIZARE
    else:
        url = URL_REZULTATE

    data = []

    for j_id, j_name, j_fullname in tqdm(
        judete, unit="judet", desc="Downloading judete"
    ):
        url_j = url % (args.year, j_id, int(time.time() * 1000))
        j_data = json.loads(urlopen(url_j).read().decode("utf-8"))
        data += j_data

    open(args.output_path, "w", encoding="utf-8").write(json.dumps(data))
