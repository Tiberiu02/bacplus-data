import argparse
import csv
import re
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("year", type=int, help="The year to fetch data for")
    parser.add_argument("output_path")

    return parser.parse_args()


URL = "http://static.bacalaureat.edu.ro/%d/rapoarte/rezultate/alfabetic/page_%d.html"

args = parse_args()


def fetch_page(url):
    try:
        page = None
        while page is None or "Eroare" in page:
            page = urlopen(url).read().decode("utf-8")
        return page
    except Exception as e:
        print(f"Error fetching page {url}. Retrying...")
        # Sleep for a bit to avoid getting blocked
        time.sleep(5)
        return fetch_page(url)


def fetch_num_pages(url):
    page = fetch_page(url)
    num_pages = int(re.findall(r"pag. (\d+)", page)[-1])
    return num_pages


def parse_results_page(page):
    soup = BeautifulSoup(page, "html.parser")
    rows = soup.find_all("tr", class_=["tr1", "tr2"])

    # Prepare a list to hold the data
    data = []

    # Extract data from each row
    for row in rows:
        cells = row.find_all("td")
        row_data = [cell.get_text(strip=True) for cell in cells]
        data.append(row_data)

    return data


def fetch_and_parse_page(url, page_id):
    page = fetch_page(url)
    data = parse_results_page(page)

    if int(data[0][0]) != (page_id - 1) * 10 + 1:
        print(f"Error fetching page {page_id} from {url}. Retrying...")
        # Sleep for a bit to avoid getting blocked
        time.sleep(1)
        return fetch_and_parse_page(url, page_id)

    return data


if __name__ == "__main__":
    args = parse_args()

    num_pages = fetch_num_pages(URL % (args.year, 1))

    print("Num. pages:", num_pages)

    fout = open(args.output_path, "w", newline="", encoding="utf-8")
    writer = csv.writer(fout)

    progress = tqdm(total=num_pages, unit="page", desc="Downloading pages")

    for page_id in range(1, num_pages + 1):
        data = fetch_and_parse_page(URL % (args.year, page_id), page_id)
        writer.writerows(data)
        progress.update(1)

    fout.close()
    progress.close()

    print(f"Downloaded {num_pages} pages.")
