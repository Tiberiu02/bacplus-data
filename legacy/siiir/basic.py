import requests
import sqlite3
import os
import dotenv

dotenv.load_dotenv()

# URL for collecting cookies
initial_url = "https://siiir.edu.ro/carto/#/retea"

# URL for the initial POST request
post_url = "https://siiir.edu.ro/carto/app/rest/genericData/find?filters=%7B%22CODE_filter_type%22:%22like%22%7D&page=1&size=1000000&sort=%7B%22NAME%22:%22asc%22%7D"

# Request payload
payload = {"key": "schoolnetwork_grid.key", "typeConfiguration": "grid"}

conn = sqlite3.connect(os.getenv("DB_FILE"))
cur = conn.cursor()

# cur.execute("DELETE FROM siiir")
# conn.commit()

# Create a session object
with requests.Session() as session:
    # Step 1: Visit initial URL to collect cookies
    session.get(initial_url)

    # Step 2: Send POST request to get the data
    response = session.post(post_url, json=payload)

    # Check if the POST request was successful
    if response.status_code == 200:
        # Iterate through rows and create objects
        # Sample row: {'ROW_NUM': 6846, 'ID_SCHOOL': 11437460, 'CODE': '3562103572', 'NAME': 'GRĂDINIȚA CU PROGRAM NORMAL ȘIPET', 'SHORT_NAME': 'GPN SIPET TORMAC', 'LOCALITY': 'ŞIPET', 'PARENT_LOCALITY': 'TORMAC', 'COUNTY': 'TIMIŞ', 'STATUT': 'Arondată', 'SCHOOL_TYPE': 'Unitate de învățământ', 'PROPERTY_FORM': 'Publică de interes naţional şi local'}
        for row in response.json().get("data").get("content"):
            cur.execute(
                "INSERT INTO siiir (cod, aux_id, denumire, denumire_scurta, localitate, localitate_superioara, judet, statut, tip_unitate, forma_proprietate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    row.get("CODE"),
                    row.get("ID_SCHOOL"),
                    row.get("NAME"),
                    row.get("SHORT_NAME"),
                    row.get("LOCALITY"),
                    row.get("PARENT_LOCALITY"),
                    row.get("COUNTY"),
                    row.get("STATUT"),
                    row.get("SCHOOL_TYPE"),
                    row.get("PROPERTY_FORM"),
                ),
            )
        conn.commit()
        conn.close()
    else:
        print(f"Failed to get download URL. Status code: {response.status_code}")
