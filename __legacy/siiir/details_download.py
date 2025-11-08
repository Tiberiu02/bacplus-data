import requests
import sqlite3
import os
import dotenv
from tqdm import tqdm
from threading import Thread, Lock
from time import sleep
import json

dotenv.load_dotenv()

conn = sqlite3.connect(os.getenv("DB_FILE"))
cur = conn.cursor()
intitutions = cur.execute("SELECT aux_id FROM siiir").fetchall()

ix = 0
lock = Lock()

progress = tqdm(total=len(intitutions))

f_out = open("data.txt", "w")


def worker():
    global ix
    while ix < len(intitutions):
        with lock:
            c_ix = ix
            ix += 1
            progress.update(1)
        if c_ix >= len(intitutions):
            break
        institution = intitutions[c_ix]
        url = f"https://siiir.edu.ro/carto/app/rest/school/details/{institution[0]}"

        fails = 0
        success = False

        while not success and fails < 5:
            try:
                response = session.get(url)
                data = response.json()
                with lock:
                    query = (
                        "UPDATE siiir SET strada=?, nr_strada=?, cod_postal=?, website=?, telefon=?, cod_sirues=?, cod_fiscal=?, mod_operare=? WHERE aux_id=?",
                        (
                            data.get("street"),
                            data.get("streetNumber"),
                            data.get("postalCode"),
                            data.get("website"),
                            data.get("phoneNumber"),
                            data.get("siruesCode"),
                            data.get("fiscalCode"),
                            data.get("operatingMode"),
                            institution[0],
                        ),
                    )
                    f_out.write(json.dumps(query) + "\n")
                success = True
            except Exception as e:
                fails += 1
                print(f"Failed to get details for {institution[0]}. Retrying...")

        if not success:
            print(
                f"Failed to get details for {institution[0]} after 5 retries. Skipping..."
            )


# def sql_worker():
#     updates = 0
#     while ix < len(intitutions) or len(pending_sql) > 0:
#         print(f"Pending SQL: {len(pending_sql)}")
#         if len(pending_sql) > 0:
#             while len(pending_sql) > 0:
#                 all_sql = []
#                 with lock:
#                     all_sql = pending_sql.copy()
#                     pending_sql.clear()
#                 print(f"Executing {len(all_sql)} SQL statements")
#                 for sql, params in all_sql:
#                     cur.execute(sql, params)
#                     updates += 1
#                     if updates % 100 == 0:
#                         conn.commit()
#                 print(f"Updated {updates} rows")
#                 conn.commit()
#         else:
#             sleep(0.1)


# Create a session object
session = requests.Session()

# Step 1: Visit initial URL to collect cookies
session.get("https://siiir.edu.ro/carto/#/retea")

# Create threads
threads = [Thread(target=worker) for _ in range(10)]

# Start threads
for thread in threads:
    thread.start()

# sql_worker()

# Wait for threads to finish
for thread in threads:
    thread.join()


# Sample School data:
# {
#     "idSchool": 11448975,
#     "internalIdSchool": 11347139,
#     "idParentSchool": null,
#     "schoolSocialLinks": [],
#     "idSchoolYear": {
#         "orderBy": 106,
#         "isFutureYear": 0,
#         "isCurrentYear": 1,
#         "dateTo": 1725137999000,
#         "dateFrom": 1693515600000,
#         "description": "Anul școlar 2023-2024",
#         "code": "2023-2024",
#         "idSchoolYear": 26
#     },
#     "schoolYearDescription": "Anul școlar 2023-2024",
#     "code": "0261205195",
#     "siruesCode": null,
#     "longName": "ASOCIAȚIA CREȘTINĂ DE CARITATE SAMARITEANUL - GRADINITA SAMARITEANUL AGRIȘU MARE",
#     "shortName": "GRADINITA SAMARITEANUL AGRIȘU MARE",
#     "schoolType": "Unitate de învățământ",
#     "statut": "Cu personalitate juridică",
#     "isPj": true,
#     "fiscalCode": "4471299",
#     "operatingMode": "Program normal",
#     "propertyForm": "Privată",
#     "fundingForm": "Taxă",
#     "county": "ARAD",
#     "locality": "AGRIŞU MARE",
#     "street": "FN",
#     "streetNumber": "837",
#     "postalCode": "317360",
#     "phoneNumber": "0752951576",
#     "faxNumber": "0752951576",
#     "email": "gsamaritenulam@yahoo.com",
#     "schoolNumbers": {
#         "idSchool": 11448975,
#         "studyFormationsCount": 2,
#         "studentsCount": 31,
#         "personnelCount": 2
#     }
# }
