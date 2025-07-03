import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import time
from dotenv import load_dotenv
from tqdm import tqdm
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv


load_dotenv()

URL = "http://evaluare.edu.ro/Evaluare/CandFromJudAlfa.aspx?Jud=%d&PageN=%d"


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("output_path")
    parser.add_argument("--num_workers", type=int, default=10)

    return parser.parse_args()


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


def fetch_and_parse_page(j_id, page_id):
    url = URL % (j_id, page_id)
    page = fetch_page(url)
    data = parse_results_page(page)

    if int(data[0][0]) != (page_id - 1) * 20 + 1:
        print(f"Error fetching page {page_id} for judet {j_id}. Retrying...")
        # Sleep for a bit to avoid getting blocked
        time.sleep(1)
        return fetch_and_parse_page(j_id, page_id)

    return data


if __name__ == "__main__":
    args = parse_args()

    num_pages = []
    for j_id in tqdm(range(1, 43), unit="judet", desc="Fetching number of pages"):
        url_j = URL % (j_id, 1)
        num_pages.append(fetch_num_pages(url_j))

    print("Pages per judet:", num_pages)

    fout = open(args.output_path, "w", newline="", encoding="utf-8")
    writer = csv.writer(fout)

    # Write header
    writer.writerow(["crt", "cod_candidat", "pozitie_ierarhie", "scoala", "lri", "lrc", "lrf", "mi", "mc", "mf", "limba_materna", "lmi", "lmc", "lmf", "medie"])

    progress = tqdm(total=sum(num_pages), unit="page", desc="Downloading pages")

    tasks = []
    with ThreadPoolExecutor(max_workers=args.num_workers) as executor:
        for j_id in range(1, 43):
            for page_id in range(1, num_pages[j_id - 1] + 1):
                tasks.append(executor.submit(fetch_and_parse_page, j_id, page_id))

        for future in as_completed(tasks):
            data = future.result()
            writer.writerows(data)
            progress.update(1)

    fout.close()
    progress.close()

    print(f"Downloaded {sum(num_pages)} pages.")
