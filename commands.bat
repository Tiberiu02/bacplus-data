python src/db_insert/evaluare.py 2021 data/evaluare/data.gov.ro/2021.xlsx schema/en/data.gov.ro.json
python src/db_insert/evaluare.py 2021 data/evaluare/static.admitere.edu.ro/2021.json schema/en/static.admitere.edu.ro.json --update-existing

python src/db_insert/evaluare.py 2022 data/evaluare/data.gov.ro/2022.xlsx schema/en/data.gov.ro.json
python src/db_insert/evaluare.py 2022 data/evaluare/static.evaluare.edu.ro/2022.json schema/en/static.evaluare.edu.ro.json --update-existing
python src/db_insert/evaluare.py 2022 data/evaluare/static.admitere.edu.ro/2022.json schema/en/static.admitere.edu.ro.json --update-existing

python src/db_insert/evaluare.py 2023 data/evaluare/data.gov.ro/2023.xlsx schema/en/data.gov.ro.json
python src/db_insert/evaluare.py 2023 data/evaluare/static.evaluare.edu.ro/2023.json schema/en/static.evaluare.edu.ro.json --update-existing
python src/db_insert/evaluare.py 2023 data/evaluare/static.admitere.edu.ro/2023.json schema/en/static.admitere.edu.ro.json --update-existing

python src/db_insert/evaluare.py 2024 data/evaluare/static.evaluare.edu.ro/2024.json schema/en/static.evaluare.edu.ro.json
python src/db_insert/evaluare.py 2024 data/evaluare/static.admitere.edu.ro/2024.json schema/en/static.admitere.edu.ro.json --update-existing