import argparse
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


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("output_path")

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


def fetch_and_parse_page(j, i, payload, is_last_page):
    try:
        payload[PAYLOAD_PAGE_ATTRIBUTE] = i
        page = fetch_page(URL % j, payload)
        soup = BeautifulSoup(page, "html.parser")
        rows = extract_rows(soup)
        payload = extract_payload(soup)

        if (
            int(rows[0][0]) != (i - 1) * 20 + 1
            or len(rows) == 0
            or (len(rows) < 20 and not is_last_page)
        ):
            raise ValueError(
                f"Expected first row id {i - 1} * 20 + 1 = {(i - 1) * 20 + 1}, got {rows[0][0]}"
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
        print(
            f"Error fetching page {URL % j}?{PAYLOAD_PAGE_ATTRIBUTE}={i}. Retrying..."
        )
        # Sleep for a bit to avoid getting blocked
        time.sleep(5)
        return fetch_and_parse_page(j, i, payload, is_last_page)


args = parse_args()

num_pages = []
for j in tqdm(range(1, NUM_JUDETE + 1), desc="Fetching num. pages"):
    page = fetch_page(URL % j)
    soup = BeautifulSoup(page, "html.parser")
    num_pages.append(extract_num_pages(soup))

# print(num_pages)
bar = tqdm(total=sum(num_pages), desc="Downloading pages")

fout = open(args.output_path, "w", newline="", encoding="utf-8")
writer = csv.writer(fout)

for j in range(1, NUM_JUDETE + 1):
    page = fetch_page(URL % j)
    soup = BeautifulSoup(page, "html.parser")

    num_pages = extract_num_pages(soup)
    payload = extract_payload(soup)
    rows = extract_rows(soup)
    writer.writerows(rows)
    bar.update(1)

    for i in range(2, num_pages + 1):
        rows, payload = fetch_and_parse_page(j, i, payload, i == num_pages)
        writer.writerows(rows)
        bar.update(1)
