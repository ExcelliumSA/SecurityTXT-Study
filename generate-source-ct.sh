#!/bin/bash
# Parameters to use to get all the data
params=( "dNSName=.lu&match=LIKE" "CN=.lu&match=LIKE" )
# Download and extract a list of LU domains
# Extract useful information via JQ
# https://stedolan.github.io/jq/
rm source.txt 2>/dev/null
touch source.txt
for param in ${params[@]}; do
	url="https://crt.sh/?$param&output=json"
	echo "[+] Call: $url"
	wget -q -O domainsLU.json $url
	cat domainsLU.json | jq -r '.[] | select(.name_value|test(".*\\.lu$")) | .name_value' >> source.txt
	wc -l source.txt
	echo "[+] Let the server cool down to prevent to receive a HTTP 504."
	sleep 10 
done
# Remove duplicates
cat source.txt | sort -u > source.tmp
mv source.tmp source.txt
rm domainsLU.json
echo "[+] Extraction finished."
mv source.txt source-ct.txt
wc -l source-ct.txt