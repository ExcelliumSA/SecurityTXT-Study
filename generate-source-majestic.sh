#!/bin/bash
echo "[+] Download Majestic CSV file and extract the data."
wget -q -O majestic_million.csv https://downloads.majestic.com/majestic_million.csv
awk -F ',' 'NR>=2 {print $7}' majestic_million.csv | grep -P '\.lu$' > source-majestic.txt
rm majestic_million.csv
echo "[+] Extraction finished."
wc -l source-majestic.txt