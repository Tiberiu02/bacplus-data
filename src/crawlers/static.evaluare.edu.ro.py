import argparse
from dotenv import load_dotenv
from tqdm import tqdm
from urllib.request import urlopen
import json
import time
import json

coduri_judete = "AB,AG,AR,B,BC,BH,BN,BR,BT,BV,BZ,CJ,CL,CS,CT,CV,DB,DJ,GJ,GL,GR,HD,HR,IF,IL,IS,MH,MM,MS,NT,OT,PH,SB,SJ,SM,SV,TL,TM,TR,VL,VN,VS"
coduri_judete = coduri_judete.split(",")


load_dotenv()

URL_ADMITERE = (
    "http://static.admitere.edu.ro/%d/repartizare/%s/data/candidate.json?_=%d"
)
URL_REZULTATE = "http://static.evaluare.edu.ro/%d/rezultate/%s/data/candidate.json?_=%d"


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("year", type=int)
    parser.add_argument("output_path")
    parser.add_argument("--admitere", action="store_true")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.admitere:
        url = URL_ADMITERE
    else:
        url = URL_REZULTATE

    data = []

    for j_id in tqdm(coduri_judete, unit="judet", desc="Downloading judete"):
        url_j = url % (args.year, j_id, int(time.time() * 1000))
        j_data = json.loads(urlopen(url_j).read().decode("utf-8"))
        data += j_data

    open(args.output_path, "w", encoding="utf-8").write(json.dumps(data))
