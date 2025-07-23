import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import re
import time
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

URL = "http://admitere.edu.ro/Pages/CandInJud.aspx?jud=%d&alfa=1"
PAYLOAD_PAGE_ATTRIBUTE = "ctl00$ContentPlaceHolderBody$DropDownList2"
NUM_JUDETE = 42

coduri_judete = "AB,AG,AR,B,BC,BH,BN,BR,BT,BV,BZ,CJ,CL,CS,CT,CV,DB,DJ,GJ,GL,GR,HD,HR,IF,IL,IS,MH,MM,MS,NT,OT,PH,SB,SJ,SM,SV,TL,TM,TR,VL,VN,VS"
coduri_judete = coduri_judete.split(",")

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("output_path")
    parser.add_argument("--num_workers", type=int, default=10)

    return parser.parse_args()


def extract_num_pages(soup):
    num_pages = max(int(n) for n in re.findall(r"pag. (\d+)", soup.get_text()))
    return num_pages


def extract_payload(soup):
    payload = {
        d["name"]: d["value"] for d in soup.find_all("input", {"type": "hidden"})
    }
    return payload


def extract_rows(soup):
    rows = soup.find_all("tr", class_=["tr1", "tr2"])

    # Prepare a list to hold the data
    data = [
        [cell.get_text(strip=True, separator="<br/>") for cell in row.find_all("td")]
        for row in rows
    ]

    return data


def fetch_page(url, payload=None):
    try:
        page = None
        while page is None or "Eroare" in page:
            if payload:
                page = requests.post(
                    url,
                    data=urlencode(payload),
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    verify=False,
                ).text
            else:
                page = requests.get(url).text
        return page
    except Exception as e:
        print(e)
        print(f"Error fetching page {url}. Retrying...")
        # Sleep for a bit to avoid getting blocked
        time.sleep(5)
        return fetch_page(url)


def fetch_and_parse_page(id_judet, target_page, prev_page, payload, is_last_page):
    try:
        if prev_page is None or payload is None:
            page = fetch_page(URL % id_judet)
            soup = BeautifulSoup(page, "html.parser")
            payload = extract_payload(soup)
            prev_page = 1
        
        if abs(prev_page - target_page) > 1:
            payload[PAYLOAD_PAGE_ATTRIBUTE] = target_page // 10 * 10
            page = fetch_page(URL % id_judet, payload)
            soup = BeautifulSoup(page, "html.parser")
            payload = extract_payload(soup)
            prev_page = target_page // 10 * 10

        if prev_page != target_page:
            payload[PAYLOAD_PAGE_ATTRIBUTE] = target_page
            page = fetch_page(URL % id_judet, payload)
            soup = BeautifulSoup(page, "html.parser")
            
        rows = extract_rows(soup)
        payload = extract_payload(soup)

        if (
            len(rows) == 0
            or (len(rows) < 20 and not is_last_page)
            or int(rows[0][0]) != (target_page - 1) * 20 + 1
        ):
            raise ValueError(
                f"Expected first row id {target_page - 1} * 20 + 1 = {(target_page - 1) * 20 + 1}, got {rows}"
            )

        for param in [
            "__VIEWSTATE",
            "__VIEWSTATEGENERATOR",
            "__EVENTVALIDATION",
        ]:
            if param not in payload:
                raise ValueError(f"Missing parameter {param} in payload: {payload}")

        return rows, payload
    except Exception as e:
        print(e)
        # Print traceback for debugging
        import traceback
        traceback.print_exc()
        print(
            f"Error fetching page {URL % id_judet} with {PAYLOAD_PAGE_ATTRIBUTE}={target_page}. Retrying..."
        )
        # Sleep for a bit to avoid getting blocked
        time.sleep(5)

        return fetch_and_parse_page(id_judet, target_page, None, None, is_last_page)


args = parse_args()

num_pages = [81, 184, 119, 791, 174, 158, 91, 70, 121, 172, 112, 205, 63, 65, 218, 47, 135, 178, 100, 152, 46, 96, 87, 54, 71, 246, 61, 133, 133, 135, 105, 227, 121, 64, 81, 250, 50, 214, 80, 103, 97, 111]
# for j in tqdm(range(1, NUM_JUDETE + 1), desc="Fetching num. pages"):
#     page = fetch_page(URL % j)
#     soup = BeautifulSoup(page, "html.parser")
#     payload = extract_payload(soup)
#     num_pages.append(extract_num_pages(soup))

print(num_pages)
bar = tqdm(total=sum(num_pages), desc="Downloading pages")

fout = open(args.output_path, "w", newline="", encoding="utf-8")
writer = csv.writer(fout)

# Write Header
writer.writerow(["crt","cod_candidat","judet","scoala","renuntare_lb_mat","madm","mev","mabs","lr","mate","lm","lm_nota","repartizat_liceu_nume","repartizat_specializare","repartizat_cod_judet"])

for j in range(1, NUM_JUDETE + 1):
    payload = None
    for i in range(1, num_pages[j - 1] + 1):
        rows, payload = fetch_and_parse_page(j, i, i - 1, payload, i == num_pages[j - 1])
        writer.writerows([row + [coduri_judete[j - 1], ] for row in rows])
        bar.update(1)
