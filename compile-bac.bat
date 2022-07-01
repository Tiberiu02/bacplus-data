python dataset.py data/bac/2014 data/bac/2014.csv meta/meta-dgov.txt --data-dot-gov
python dataset.py data/bac/2015 data/bac/2015.csv meta/meta-dgov.txt --data-dot-gov
python dataset.py data/bac/2016 data/bac/2016.csv meta/meta-dgov.txt --data-dot-gov
python dataset.py data/bac/2017 data/bac/2017.csv meta/meta-dgov.txt --data-dot-gov
python dataset.py data/bac/2018 data/bac/2018.csv meta/meta-dgov.txt --data-dot-gov
python dataset.py data/bac/2019 data/bac/2019.csv meta/meta-edu-raport.txt         
python dataset.py data/bac/2020 data/bac/2020.csv meta/meta-edu-raport.txt         
python dataset.py data/bac/2021 data/bac/2021.csv meta/meta-edu-initial.txt        
python dataset.py data/bac/2022 data/bac/2022.csv meta/meta-edu-initial.txt        
cd data
cd bac
tar.exe -a -c -f 2014.zip 2014
tar.exe -a -c -f 2015.zip 2015
tar.exe -a -c -f 2016.zip 2016
tar.exe -a -c -f 2017.zip 2017
tar.exe -a -c -f 2018.zip 2018
tar.exe -a -c -f 2019.zip 2019
tar.exe -a -c -f 2020.zip 2020
tar.exe -a -c -f 2021.zip 2021
tar.exe -a -c -f 2022.zip 2022
tar.exe -a -c -f all.zip 2014.zip 2015.zip 2016.zip 2017.zip 2018.zip 2019.zip 2020.zip 2021.zip 2022.zip 2014 2015 2016 2017 2018 2019 2020 2021 2022
cd ..
cd ..