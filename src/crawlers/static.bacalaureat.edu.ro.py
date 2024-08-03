import argparse
import csv
import re
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from tqdm import tqdm
from py_mini_racer import MiniRacer


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("year", type=int, help="The year to fetch data for")
    parser.add_argument("output_path")

    return parser.parse_args()


URL = "http://static.bacalaureat.edu.ro/%d/rapoarte/rezultate/alfabetic/page_%d.html"

args = parse_args()
ctx = MiniRacer()


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


def parse_results_page(page, url):
    soup = BeautifulSoup(page, "html.parser")
    rows = soup.find_all("tr", class_=["tr1", "tr2"])

    # Initialize helper functions and page variables
    ctx.eval(
        """
        var LuatDePeBacalaureatEduRo = new Array();
        var LuatDePe_BacalaureatEduRo = new Array();
        var Luat_DePe_BacalaureatEduRo = new Array();
             
        var document = {};
        document.write = function(s) {
            document.output += s;
        }; 
        
        var window = {};
        window.location = {};
        window.location.href = """
        + f'"{url}"'
    )

    # Prepare a list to hold the data
    data = []

    # Extract data from each row
    for row in rows:
        row_data = []

        # This script sets the candidate data
        for script in row.findChildren("script", recursive=False):
            ctx.eval(script.get_text())

        for cell in row.find_all("td"):
            cell_text = cell.get_text(strip=True)
            # These scripts print the candidate data
            for script in cell.find_all("script"):
                ctx.eval("document.output = '';")
                ctx.eval(script.get_text())
                cell_text += ctx.eval("document.output")
            row_data.append(cell_text.replace("<br>", "").strip())

        data.append(row_data)

    data = [data[i] + data[i + 1] for i in range(0, len(data), 2)]

    return data


def fetch_and_parse_page(url, page_id):
    page = fetch_page(url)
    data = parse_results_page(page, url)

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

    # Write header
    writer.writerow(
        [
            "id",
            "cod_candidat",
            "ierarhie_judet",
            "ierarhie_national",
            "nume_unitate",
            "cod_judet",
            "promotie_anterioara",
            "forma_invatamant",
            "specializare",
            "lr_competente",
            "lr_init",
            "lr_cont",
            "lr_final",
            "limba_materna",
            "limba_moderna",
            "nota_limba_moderna",
            "disciplina_obligatorie",
            "disciplina_alegere",
            "competente_digitale",
            "medie",
            "rezultat",
            "lm_competente",
            "lm_init",
            "lm_cont",
            "lm_final",
            "do_init",
            "do_cont",
            "do_final",
            "da_init",
            "da_cont",
            "da_final",
        ]
    )

    progress = tqdm(total=num_pages, unit="page", desc="Downloading pages")

    for page_id in range(1, num_pages + 1):
        data = fetch_and_parse_page(URL % (args.year, page_id), page_id)
        writer.writerows(data)
        progress.update(1)

    fout.close()
    progress.close()

    print(f"Downloaded {num_pages} pages.")
