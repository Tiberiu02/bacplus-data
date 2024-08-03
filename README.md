# Instalare (BAC+EN)

Asigură-te că ai Python 3 instalat. Deschide CMD în acest folder (sau teminalul pe Linux/Mac) și instalează dependințele python folosind comanda:

`pip install -r requirements.txt`

Asigură-te că ai Firefox instalat (dintr-un anumit motiv, Firefox este mult mai stabil decât Chrome). Descărcă ultima versiune de [gecko driver](https://github.com/mozilla/geckodriver/releases) și adăugă fișierul executabil (`"geckodriver.exe"` pe Windows) în acest folder.

# Descărcare date BAC

Pentru această etapă vei folosi programul `"crawler_bac.py"`. Acest program permite descărcarea automată a rezultatelor tuturor candidaților de pe site-ul http://static.bacalaureat.edu.ro/. Înainte de a putea rula programul vei avea nevoie de 2 lucruri:

- Linkul către prima pagină cu rezultatele tuturor candidaților (indiferent de ordine). Poți verifica că linkul este corect accesându-l într-o altă fereastră și verificând că te duce direct la prima pagină cu rezultate. Uneori site-ul încarcă rezultatele printr-o sub-fereastră (frame). În acest caz, va trebui să folosești linkul sub-ferestrei.
- Numărul de pagini de rezultate

Pentru a rula programul, folosește comanda:

`python crawler_bac.py [link_rezultate] [număr_pagini] [fișier_ieșire.csv]`

De exemplu:

`python crawler_bac.py http://bacalaureat.edu.ro/Pages/TaraRezultMedie.aspx 13053 data/bac/2023.csv`

Ar trebui să se deschidă o fereastră Firefox. Ai răbdare, va dura câteva ore. Poți urmări progresul în consolă.

# Descărcare date EN

Pentru această etapă vei folosi programul `"crawler_en.py"`. Acest program permite descărcarea automată a rezultatelor tuturor candidaților de pe site-ul http://static.admitere.edu.ro/. Spre deosebire de programul `crawler_bac.py`, acest program nu necesită simularea browserului.

Pentru a rula programul, folosește comanda:

`python crawler_en.py [an] [fișier_ieșire.json] [--repartizare]`

Stegulețul `--repartizare` este folosit pentru a descărca și repartizarea pe licee (trebuie folosit doar dacă aceasta este disponibilă).

De exemplu:

- `python crawler_en.py 2022 data\en\2022.json --repartizare`
- `python crawler_en.py 2023 data\en\2023.json`

# Inserare date in baza de date SQLite

Pentru a insera datele descărcate în baza de date, asigură-te că ai creat un fișier `.env` care conține variabila `DB_FILE`. Apoi folosește programele `db_insert_bac.py` sau `db_insert_en.py`, astfel:

- `python db_insert_bac.py [an] [fișier_intrare.csv]`
- `python db_insert_en.py [an] [fișier_intrare.json] [--repartizare]`

De exemplu:

- `python db_insert_bac.py 2023 data\bac\2023.csv`
- `python db_insert_en.py 2023 data\en\2023.json`
- `python db_insert_en.py 2022 data\en\2022.json --repartizare`

Pentru o lista mai completa de comenzi, vezi scripturile `insert_all_bac.bat` și `insert_all_en.bat`

# Inserare date in baza de date PostgreSQL

Pentru a insera datele descărcate în baza de date, asigură-te că ai creat un fișier `.env` care conține variabila `DATABASE_URL`. Apoi folosește programul `src/db_insert/bac.py`, astfel:

- `python src/db_insert/bac.py [an] [fișier_rezultate.xlsx] [fișier_schema.json]`

De exemplu:

- `python src/db_insert/bac.py 2023 data/bac/data.gov.ro/2023.xlsx src/db_insert/schema/bac/data.gov.ro.json`
- `python src/db_insert/bac.py 2022 data/bac/data.gov.ro/2022.xlsx src/db_insert/schema/bac/data.gov.ro.2.json`
- `python src/db_insert/bac.py 2021 data/bac/data.gov.ro/2021.xlsx src/db_insert/schema/bac/data.gov.ro.json`
- `python src/db_insert/bac.py 2020 data/bac/data.gov.ro/2020.xlsx src/db_insert/schema/bac/data.gov.ro.json`
- `python src/db_insert/bac.py 2019 data/bac/data.gov.ro/2019.xlsx src/db_insert/schema/bac/data.gov.ro.json`
- `python src/db_insert/bac.py 2018 data/bac/data.gov.ro/2018.xlsx src/db_insert/schema/bac/data.gov.ro.json`
