import argparse
import csv
import re
import time
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

URL = "https://www.bacalaureat.edu.ro/Pages/TaraRezultMedie.aspx"
PAYLOAD_PAGE_ATTRIBUTE = "ctl00$ContentPlaceHolderBody$DropDownList2"
ROWS_PER_PAGE = 10


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("output_path")

    return parser.parse_args()


def extract_num_pages(soup):
    num_pages = max(int(n) for n in re.findall(r"pag. (\d+)", soup.get_text()))
    return num_pages

def extract_avaialable_pages(soup):
    return [int(n) for n in re.findall(r"pag. (\d+)", soup.get_text())]


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

    # Join rows two by two
    data = [data[i] + data[i + 1] for i in range(0, len(data), 2)]

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
                    verify=True,
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


def fetch_and_parse_page(target_page, soup, is_last_page):
    try:
        if soup is None:
            page = fetch_page(URL)
            soup = BeautifulSoup(page, "html.parser")

        available_pages = extract_avaialable_pages(soup)
        closest_page = min(available_pages, key=lambda x: abs(x - target_page))

        payload = extract_payload(soup)
        payload[PAYLOAD_PAGE_ATTRIBUTE] = closest_page
        payload['__EVENTTARGET'] = PAYLOAD_PAGE_ATTRIBUTE
        new_page = fetch_page(URL, payload)
        new_soup = BeautifulSoup(new_page, "html.parser")

        for param in [
            "__VIEWSTATE",
            "__VIEWSTATEGENERATOR",
            "__EVENTVALIDATION",
        ]:
            if param not in payload:
                raise ValueError(f"Missing parameter {param} in payload: {payload}")

        if target_page != closest_page:
            print(
                f"Target page {target_page} not available, using closest page {closest_page}."
            )
            return fetch_and_parse_page(
                target_page, new_soup, is_last_page
            )
        else:
            rows = extract_rows(new_soup)
            payload = extract_payload(new_soup)

            if (
                int(rows[0][0]) != (target_page - 1) * ROWS_PER_PAGE + 1
                or len(rows) == 0
                or (len(rows) != ROWS_PER_PAGE and not is_last_page)
            ):
                raise ValueError(
                    f"Expected first row id {target_page - 1} * {ROWS_PER_PAGE} + 1 = {(target_page - 1) * ROWS_PER_PAGE + 1}, got {rows[0][0]}"
                )

            return rows, new_soup
    except Exception as e:
        print(e)
        # print(page)
        # Print traceback for debugging
        import traceback
        traceback.print_exc()

        print(
            f"Error fetching page {URL}?{PAYLOAD_PAGE_ATTRIBUTE}={target_page}. Retrying..."
        )
        # Sleep for a bit to avoid getting blocked
        time.sleep(5)
        return fetch_and_parse_page(target_page, None, is_last_page)


args = parse_args()

page = fetch_page(URL)
soup = BeautifulSoup(page, "html.parser")
num_pages = extract_num_pages(soup)

print(f"Total number of pages: {num_pages}")

fout = open(args.output_path, "a", newline="", encoding="utf-8")
writer = csv.writer(fout)

# payload = extract_payload(soup)
# rows = extract_rows(soup)
# writer.writerows(rows)
# bar.update(1)

for i in tqdm(range(2213, num_pages + 1), desc="Downloading pages"):
    rows, soup = fetch_and_parse_page(i, soup, i == num_pages)
    writer.writerows(rows)
