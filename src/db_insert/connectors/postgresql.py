import psycopg2
from tqdm import tqdm

CHUNK_SIZE = 5000


def pg_insert(data, table_name, db_url, filter, replacement_key=None):
    if db_url is None:
        print("Make sure to specify DATABASE_URL in .env file")
        exit(1)

    data_cols = list(data[0].keys())

    chunks = [data[i : i + CHUNK_SIZE] for i in range(0, len(data), CHUNK_SIZE)]

    print(f"Connecting to database...")

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    if replacement_key is None:
        # Remove existing entries and reinsert
        cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {filter}")
        cnt = cur.fetchone()[0]

        print(f"Deleting {cnt} entries from database...")

        cur.execute(f"DELETE FROM {table_name} WHERE {filter}")
        print(f"Inserting {len(data)} entries into database...")

        for chunk in tqdm(chunks):
            cur.execute(
                f"INSERT INTO {table_name}({','.join(data_cols)}) VALUES "
                + ",".join(
                    cur.mogrify(
                        "(" + ",".join(["%s"] * len(x)) + ")",
                        [x[col] for col in data_cols],
                    ).decode("utf-8")
                    for x in chunk
                )
            )
    else:
        # Update existing entries
        cur.execute(f"SELECT {replacement_key} FROM {table_name} WHERE {filter}")
        existing_keys = set([x[0] for x in cur.fetchall()])

        not_found = []

        print(f"Updating {len(data)} entries into database...")
        for chunk in tqdm(chunks):
            data_cols_chunk = [
                col for col in data_cols if any(col in x and x[col] is not None for x in chunk)
            ]

            for x in chunk:
                if x[replacement_key] not in existing_keys:
                    not_found.append(x[replacement_key])

            query = (
                f"update {table_name} set "
                + ",".join(f"{col} = u.{col}" for col in data_cols_chunk)
                + " from (values "
                + ",".join(
                    cur.mogrify(
                        "(" + ",".join(["%s"] * len(data_cols_chunk)) + ")",
                        [x[col] if col in x else None for col in data_cols_chunk],
                    ).decode("utf-8")
                    for x in chunk
                )
                + f") as u({','.join(data_cols_chunk)}) where {table_name}.{replacement_key} = u.{replacement_key} and {filter}"
            )

            cur.execute(
                query
                # f"update en set medie_adm = u.medie_adm, medie_abs = u.medie_abs, repartizat_id_liceu = u.repartizat_id_liceu, repartizat_specializare = u.repartizat_specializare from (values "
                # + ",".join(cur.mogrify("(%s,%s,%s,%s,%s)", x).decode("utf-8") for x in data)
                # + f") as u(COD_CANDIDAT,MEDIE_ABS,MEDIE_ADM,REPARTIZAT_ID_LICEU,REPARTIZAT_SPECIALIZARE) where en.AN = {args.year} and en.COD_CANDIDAT = u.COD_CANDIDAT",
            )

        if len(not_found) > 0:
            print(f"Not found {len(not_found)} entries:")
            print("\n".join(not_found))

    conn.commit()
    conn.close()
