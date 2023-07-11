# Instalare (BAC+EN)

Asigură-te că ai Python 3 instalat. Deschide CMD în acest folder (sau teminalul pe Linux/Mac) și instalează dependințele python folosind comanda:

`pip install -r requirements.txt`

Asigură-te că ai Firefox instalat (dintr-un anumit motiv, Firefox este mult mai stabil decât Chrome). Descărcă ultima versiune de [gecko driver](https://github.com/mozilla/geckodriver/releases) și adăugă fișierul executabil (`"geckodriver.exe"` pe Windows) în acest folder.

# Descărcare date (BAC)

Pentru această etapă vei folosi programul `"crawler.py"`. Acest program permite descărcarea automată a rezultatelor tuturor candidaților de pe site-ul http://static.bacalaureat.edu.ro/. Înainte de a putea rula programul vei avea nevoie de 2 lucruri:

- Linkul către prima pagină cu rezultatele tuturor candidaților (indiferent de ordine). Poți verifica că linkul este corect accesându-l într-o altă fereastră și verificând că te duce direct la prima pagină cu rezultate. Uneori site-ul încarcă rezultatele printr-o sub-fereastră (frame). În acest caz, va trebui să folosești linkul sub-ferestrei.
- Numărul de pagini de rezultate

Pentru a rula programul, vei folosi o comandă de genul:

`python crawler.py [link_rezultate] [număr_pagini] [fișier_ieșire]`

De exemplu:

`python crawler.py http://bacalaureat.edu.ro/Pages/TaraRezultMedie.aspx 13053 data/bac/2023.csv`

Ar trebui să se deschidă o fereastră Firefox. Ai răbdare, va dura câteva ore. Poți urmări progresul în consolă.

# Compilare statistici (BAC)

Pentru această etapă vei folosi programul `"dataset.py"`. Pentru a compila statisticile, va trebui să rulezi o comandă de genul:

`python dataset.py [folder output] [fișier rezultate.csv] [meta file.txt] (--data-dot-gov)`

Fișierul meta se referă conține informații despre structura datelor și permite lucrul cu informații din diferite surse. Mai exact, există 3 surse posibile:

- Rezultate extrase de pe _bacalaureat.edu.ro_ imediat după publicare
- Rezultate extrase de pe _bacalaureat.edu.ro_ la ceva timp după publicare (acestea conțin două coloane în plus)
- Tabelele publicate pe _data.gov.ro_. Pentru această sursă va trebui să folosești flagul `"--data-dot-gov"`

Spre exemplu, acestea sunt comenzile cu care poți prelucra toate datele din folderul `"data/bac/"`:

| **An** | **Sursă date**              | **Commandă calculare statistici**                                                       |
| ------ | --------------------------- | --------------------------------------------------------------------------------------- |
| 2014   | data.gov.ro                 | `python dataset.py data/bac/2014 data/bac/2014.csv meta/schema-dgov.txt --data-dot-gov` |
| 2015   | data.gov.ro                 | `python dataset.py data/bac/2015 data/bac/2015.csv meta/schema-dgov.txt --data-dot-gov` |
| 2016   | data.gov.ro                 | `python dataset.py data/bac/2016 data/bac/2016.csv meta/schema-dgov.txt --data-dot-gov` |
| 2017   | data.gov.ro                 | `python dataset.py data/bac/2017 data/bac/2017.csv meta/schema-dgov.txt --data-dot-gov` |
| 2018   | data.gov.ro                 | `python dataset.py data/bac/2018 data/bac/2018.csv meta/schema-dgov.txt --data-dot-gov` |
| 2019   | bacalaureat.edu.ro (arhiva) | `python dataset.py data/bac/2019 data/bac/2019.csv meta/schema-edu-raport.txt`          |
| 2020   | bacalaureat.edu.ro (arhiva) | `python dataset.py data/bac/2020 data/bac/2020.csv meta/schema-edu-raport.txt`          |
| 2021   | bacalaureat.edu.ro          | `python dataset.py data/bac/2021 data/bac/2021.csv meta/schema-edu-initial.txt`         |
| 2022   | bacalaureat.edu.ro          | `python dataset.py data/bac/2022 data/bac/2022.csv meta/schema-edu-initial.txt`         |

# Descărcare date (EN)

Pentru această etapă vei folosi programul `"crawler_EN.py"`. Acest program permite descărcarea automată a rezultatelor tuturor candidaților de pe site-ul http://evaluare.edu.ro/.

Pentru a rula programul, vei folosi o comandă de genul:

```bash
Usage: python crawler_EN.py <year> <number of browser windows> <output file>
  crawls year <year> and puts output <output file> using the specified number of windows
```

De exemplu:

```bash
Usage: python crawler_EN.py 2022 2 data/en/2022.csv
```

Ar trebui să se deschidă una sau mai multe ferestre Firefox. Ai răbdare, va ceva timp 1-2h.

# Compilare statistici (EN)

Work in progress....

# Actualizare site (doar pentru admin) (BAC+EN)

Copiaza directorul rezultat la pasul precedent pe site în folderul `"assets/data/"`. Va fi nevoie să îl compresezi pentru a îl încărca.

Modifica vectorul `years` din `"assets/js/misc.js"`. **Ai grijă! O dată ce salvezi acest fișier, noile date vor deveni publice!** Poți face un mic test publicând datele la copia site-ului aflată în directorul `"/dev"`.

Intră pe câteva pagini (top licee, top județe) și adaugă un anunț privind noile date. Nu uita să îl ștergi după 2 săptămâni.

Actualizează numărul de candidați de pe pagina principală.

# Data modeling

MAIN

- year: int
- cod_candidat: string
- id_liceu: string
- id_judet: string
- promotie_anterioara: bool
- specializare: string

# Limba Romana

- lr_init: float?
- lr_cont: float?
- lr_final: float?

# Limba materna (optional)

- lm_init: float?
- lm_cont: float?
- lm_final: float?
- limba_moderna: string

# Disciplina obligatorie

- do: string
- do_init: float?
- do_cont: float?
- do_final: float?

# Disciplina la alegere

- da: string
- da_init: float?
- da_cont: float?
- da_final: float?

# Rezultat

- media: float?
- rezultat: "REUSIT" | "RESPINS" | "NEPREZENTAT" | "ELIMINAT"

LICEE

- id: string
- nume: string
