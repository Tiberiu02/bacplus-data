import argparse
import csv
import re
import time
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from multiprocessing import Process, Queue, Value, Manager
import sys

URL = "https://www.bacalaureat.edu.ro/Pages/TaraRezultMedie.aspx"
PAYLOAD_PAGE_ATTRIBUTE = "ctl00$ContentPlaceHolderBody$DropDownList2"
ROWS_PER_PAGE = 10

DEBUG = False  # Set to True for debugging output, False for normal operation


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("output_path")
    parser.add_argument("--num_workers", type=int, default=10,
                        help="Number of worker threads to use for fetching pages")

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
                    verify=True
                ).text
            else:
                page = requests.get(url).text
        return page
    except Exception as e:
        if DEBUG:
            print(e)
            print(f"Error fetching page {url}. Retrying...")
        # Sleep for a bit to avoid getting blocked
        time.sleep(5)
        return fetch_page(url, None)


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
            if DEBUG:
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
                len(rows) == 0
                or (len(rows) != ROWS_PER_PAGE and not is_last_page)
            ):
                raise ValueError(
                    f"Expected {ROWS_PER_PAGE} rows, got {len(rows)}."
                )
            if (
                int(rows[0][0]) != (target_page - 1) * ROWS_PER_PAGE + 1
            ):
                raise ValueError(
                    f"Expected first row id {target_page - 1} * {ROWS_PER_PAGE} + 1 = {(target_page - 1) * ROWS_PER_PAGE + 1}, got {rows[0][0]}"
                )

            return rows, new_soup
    except Exception as e:
        if DEBUG:
            print(e)
            import traceback
            traceback.print_exc()
            print(
                f"Error fetching page {URL}?{PAYLOAD_PAGE_ATTRIBUTE}={target_page}. Retrying..."
            )
        # Sleep for a bit to avoid getting blocked
        time.sleep(1)
        return fetch_and_parse_page(target_page, None, is_last_page)



def worker(queue, num_pages, results, progress_counter):
    soup = None

    while not queue.empty():
        try:
            batch = queue.get_nowait()
        except:
            break

        for page_num in batch:
            rows, soup = fetch_and_parse_page(page_num, soup, page_num == num_pages)
            results[page_num] = rows
            progress_counter.value += 1

def main():
    args = parse_args()
    first_page_html = fetch_page(URL)
    soup = BeautifulSoup(first_page_html, "html.parser")
    num_pages = extract_num_pages(soup)

    bar = tqdm(total=num_pages, desc="Downloading pages", unit="pages")

    fout = open(args.output_path, "w", newline="", encoding="utf-8")
    writer = csv.writer(fout)

    header = [
        "id", "cod_candidat", "nume_unitate", "cod_judet", "promotie_anterioara", "forma_invatamant",
        "specializare", "lr_competente", "lr_init", "lr_cont", "lr_final", "limba_materna",
        "limba_moderna", "nota_limba_moderna", "disciplina_obligatorie", "disciplina_alegere",
        "competente_digitale", "medie", "rezultat", "lm_competente", "lm_init", "lm_cont",
        "lm_final", "do_init", "do_cont", "do_final", "da_init", "da_cont", "da_final"
    ]
    writer.writerow(header)

    # Write first page synchronously
    writer.writerows(extract_rows(soup))
    fout.flush()
    bar.update(1)

    # Create batches of 10 consecutive pages so than workers can go through consecutive pages
    # This is to avoid workers having to do two requests to reach a page that is quite far away
    batches = Queue()
    start_page = 2
    while start_page <= num_pages:
        # Each batch starts at a multiple of 10 which is always available in the dropdown
        end_page = (start_page + 10) // 10 * 10 - 1 # Round up to the next multiple of 10
        batches.put([i for i in range(start_page, min(end_page, num_pages) + 1)])
        start_page = end_page + 1
    progress_counter = Value('i', 0)  # Shared progress counter

    with Manager() as manager:
        results = manager.list([None] * (num_pages + 1))  # Shared list to store results

        procs = []
        for _ in range(args.num_workers):
            p = Process(target=worker, args=(batches, num_pages, results, progress_counter), daemon=False)
            p.start()
            procs.append(p)

        # Add intrerrupt handler to gracefully handle Ctrl+C
        def signal_handler(sig, frame):
            # Kill all threads
            bar.close()
            fout.close()
            batches.cancel_join_thread()
            for p in procs:
                p.kill()
                p.join()
            exit(0)
        import signal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Process results
        current_page = 2
        while current_page <= num_pages:
            if progress_counter.value > 0:
                with progress_counter.get_lock():
                    bar.update(progress_counter.value)
                    progress_counter.value = 0
            while current_page <= num_pages and results[current_page] is not None:
                writer.writerows(results[current_page])
                results[current_page] = None
                current_page += 1
                fout.flush()
            time.sleep(0.1)

        for p in procs:
            p.join()

    fout.close()
    print("\nScraping complete.")

if __name__ == "__main__":
    main()