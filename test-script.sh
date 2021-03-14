#!/bin/bash
mv test-source.txt source.txt
python generate-stats.py > out.txt
absent=$(grep -c "ABSENT : 4" out.txt)
present=$(grep -c "PRESENT: 2" out.txt)
if [ "$absent" != "1" -o "$present" != "1" ]
then
    echo "[!] Test failed!"
    cat out.txt
    exit 1
else
    echo "[+] Test OK"
fi