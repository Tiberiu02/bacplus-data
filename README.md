# Instalare

Asigură-te că ai Python 3 instalat. Deschide CMD în acest folder (sau teminalul pe Linux/Mac) și instalează dependințele python folosind comanda:

`pip install -r requirements.txt`

Asigură-te că ai Firefox instalat. Descărcă ultima versiune de [gecko driver](https://github.com/mozilla/geckodriver/releases) și adăugă fișierul executabil (`"geckodriver.exe"` pe Windows) în acest folder.

# Descărcare date

Pentru această etapă vei folosi programul `"crawler.py"`. Acest program permite descărcarea automată a rezultatelor tuturor candidaților de pe site-ul http://static.bacalaureat.edu.ro/. Înainte de a putea rula programul vei avea nevoie de 2 lucruri:

* Linkul către prima pagină cu rezultatele tuturor candidaților (indiferent de ordine). Poți verifica că linkul este corect accesându-l într-o altă fereastră și verificând că te duce direct la prima pagină cu rezultate. Uneori site-ul încarcă rezultatele printr-o sub-fereastră (frame). În acest caz, va trebui să folosești linkul sub-ferestrei.
* Numărul de pagini de rezultate

Pentru a rula programul, vei folosi o comandă de genul:

`python crawler.py [link_rezultate] [număr_pagini] [fișier_ieșire]`

De exemplu:

`python crawler.py http://static.bacalaureat.edu.ro/2021/rapoarte/rezultate/alfabetic/index.html 13367 data/2021.csv`

Ar trebui să se deschidă o fereastră Firefox. Ai răbdare, va dura câteva ore. Poți urmări progresul în consolă.

# Compilare statistici 

Pentru această etapă vei folosi programul `"dataset.py"`. Pentru a compila statisticile, va trebui să rulezi o comandă de genul:

`python dataset.py [nume set de date] [fișier rezultate.txt] [meta file.txt]`

Spre exemplu:

`python dataset.py data/2019 data/2019.txt meta/meta-edu-initial.txt`

# Actualizare site (doar pentru admin)

Copiaza directorul rezultat la pasul precedent pe site în folderul `"assets/data/"`. Va fi nevoie să îl compresezi pentru a îl încărca.

Modifica vectorul `years` din `"assets/js/misc.js"`. **Ai grijă! O dată ce salvezi acest fișier, noile date vor deveni publice!** Poți face un mic test publicând datele la copia site-ului aflată în directorul `"/dev"`.

Intră pe câteva pagini (top licee, top județe) și adaugă un anunț privind noile date. Nu uita să îl ștergi după 2 săptămâni.

Actualizează numărul de candidați de pe pagina principală.
