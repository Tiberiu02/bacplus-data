import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()

misattributed_candidates = [
    # COLEGIUL NATIONAL "EMANUIL GOJDU" ORADEA, BIHOR
    (2024, "1551001"),
    # LICEUL TEORETIC "JEAN LOUIS CALDERON" TIMISOARA, TIMIS
    (2024, "1405243"),
    (2024, "1489598"),
    # Colegiul Național „Al. I. Cuza”, Focșani
    (2022, "1270866"),
    (2022, "1186424"),
]

if __name__ == "__main__":
    if os.getenv("DATABASE_URL") is None:
        print("Make sure to specify DATABASE_URL in .env file")
        exit(1)

    print(f"Connecting to database at '{os.getenv('DB_FILE')}'")

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    # Remove existing entries
    print(f"Updating {len(misattributed_candidates)} entries into database...")

    for year, cod_candidat in misattributed_candidates:
        cur.execute(
            f"select count(*) from bac where an = {year} and cod_candidat = '{cod_candidat}'"
        )
        cnt = cur.fetchone()[0]
        cur.execute(
            f"update bac set unitate_siiir = null, unitate_cod_judet = null, unitate_nume = null where an = {year} and cod_candidat = '{cod_candidat}'",
        )
        print(f"Updated {cnt} entries for {year} - {cod_candidat}")

    conn.commit()
    conn.close()
