import psycopg2
from dotenv import load_dotenv
import os

from utils.gpt_name_formatter import cannonicalize_name, format_nume_advanced


load_dotenv()

if __name__ == "__main__":
    if os.getenv("DATABASE_URL") is None:
        print("Make sure to specify DATABASE_URL in .env file")
        exit(1)

    print(f"Connecting to database at '{os.getenv('DB_FILE')}'")

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    an = 2024
    table = "en"
    filter_cond = (
        f"an = {an} AND promotie_anterioara = False" if table == "bac" else f"an = {an}"
    )

    # Load existing entries
    cur.execute("SELECT cod_siiir, nume, cod_judet FROM institutii")
    existing = cur.fetchall()
    existing_dict = {row[0]: row for row in existing}

    print(f"Loaded {len(existing)} existing institutii")

    cur.execute(
        f"SELECT unitate_siiir, unitate_nume, unitate_cod_judet FROM {table} WHERE {filter_cond} GROUP BY unitate_siiir, unitate_nume, unitate_cod_judet"
    )
    institutii_en = cur.fetchall()

    print(f"Loaded {len(institutii_en)} institutii_en")

    found = 0
    differences = 0
    for siiir, nume, cod_judet in institutii_en:
        if siiir not in existing_dict:
            print(
                f"Missing school '{nume}' with SIIIR code {siiir} and county code {cod_judet}"
            )
            # cur.execute(
            #     "INSERT INTO siiir (cod_siiir, denumire_lunga_unitate, cod_judet) VALUES (%s, %s, %s)",
            #     (siiir, nume, cod_judet),
            # )
            # print(f"Inserted {nume} into siiir")
            # print()
        else:
            existing_name = existing_dict[siiir][1]
            existing_cod_judet = existing_dict[siiir][2]

            cname_new = (
                cannonicalize_name(nume, cod_judet, id=True)
                .replace("_", "")
                .replace("A", "I")
            )
            cname_old = (
                cannonicalize_name(existing_name, existing_cod_judet, id=True)
                .replace("_", "")
                .replace("A", "I")
            )
            if cname_new != cname_old:
                print(
                    f"Found different name '{nume}' for existing school '{existing_name}', SIIIR code {siiir}"
                )
                differences += 1

                new_name = format_nume_advanced(nume, liceu=False)
                print(f"Setting new name: {new_name}")
                print("")
                cur.execute(
                    "UPDATE institutii SET nume = %s WHERE cod_siiir = %s",
                    (new_name, siiir),
                )
                conn.commit()

                # if differences > 10:
                #     exit()
            found += 1

    print(f"Found {found} existing schools")
    print(f"Found {differences} differences")

    # conn.commit()
    conn.close()
