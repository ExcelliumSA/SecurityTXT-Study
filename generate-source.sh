#!/bin/bash
# Download a list of LU domains
wget -q -O domainsLU.json "https://crt.sh/?q=.lu&output=json"
# Extract useful information via JQ
# https://stedolan.github.io/jq/
jq -r ".[].name_value" domainsLU.json | grep -v " " | sort -u > source.txt
wc -l source.txt