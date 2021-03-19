import requests
import sqlite3
import sys
import os
import concurrent.futures

"""
Python3 script to compute stats about usage of "security.txt" file on a panel of Luxemburgish domains.

Dependencies:
    pip install requests

Shell used to build the source file: 
    See script named "generate-source.sh"
"""
# Constants
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
NON_WEB_SUB_DOMAIN = ["*", "autodiscover", "sip", "pop", "pop3", "imap", "smtp", "ftp", "lyncdiscover", "lyncweb", "lync", "mx", "mx1", "mx2", "vpn"]
FILE_LOCATIONS = ["/.well-known/security.txt", "/security.txt"]
PROTOCOLS = ["https", "http"]
DB_FILE = "data.db"
NON_WEB_SUB_DOMAIN.sort()

# Disable TLS warning when validation is disabled when requests is used
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Utilities functions
def prepare_domains_list(source_file):
    prepared_list = []
    with open(source_file, "r", encoding="utf-8") as f:
        domains = f.read().splitlines()
    for domain in domains:
        value = domain.lower().strip("\n\r\t ")
        if len(value) == 0:
            continue
        if value.startswith("DNS:"):
            # DNS:app.xlm.com ==> app.xlm.com
            value = value[4:]
        parts = value.split(".")
        if parts[0] in NON_WEB_SUB_DOMAIN:
            # Convert non-web related domain to expected domain main site
            # sip.xlm.lu ==> www.xlm.lu
            parts[0] = "www"
            value = ".".join(parts)
        if "@" in value:
            # info@xlm.lu ==> www.xlm.lu
            value = f"www.{value.split('@')[1]}"
        if value not in prepared_list:
            prepared_list.append(value)
    return prepared_list

def test_request(url, session):
    found = False
    try:
        response = session.get(url, verify=False, timeout=5, allow_redirects=True)
        # Check only the presence of the field "Contact:" in order 
        # to support a maximum of versions of the standard        
        found = (response.status_code == 200 
            and "Content-Type" in response.headers 
            and response.headers["Content-Type"] == "text/plain" 
            and "Contact:" in response.text)
    except:
        found = False
    return found

def test_domain(domain):
    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})
        for location in FILE_LOCATIONS:
            for protocol in PROTOCOLS:
                url = f"{protocol}://{domain}{location}"
                if test_request(url, session):
                    return True
    return False

def worker(domain):
    print(f"\rTesting domain: {domain:<60}", end="", flush=True)
    with sqlite3.connect(DB_FILE) as connection:
        found = test_domain(domain)
        curs = connection.cursor()
        security_file_present = "ABSENT"
        if found:
            security_file_present = "PRESENT"
        curs.execute("INSERT INTO result (url,found) VALUES(?,?);",(domain, security_file_present))  

# Program entry point
if __name__ == "__main__":
    if len(sys.argv) != 2 or not os.path.isfile(sys.argv[1]):
        print("[!] Missing or invalid source file !")
        sys.exit(1)
    source_file = sys.argv[1]
    print("[+] Prepare the list of domains...")
    domains_list = prepare_domains_list(source_file)
    print(f"{len(domains_list)} domains selected.")
    print("[+] Initialize DB...")
    with sqlite3.connect(DB_FILE) as connection:
        curs = connection.cursor()
        curs.execute("CREATE TABLE IF NOT EXISTS result (id integer PRIMARY KEY, url text NOT NULL, found text NOT NULL);")
        curs.execute("DELETE FROM result;")
    print("[+] Process the list...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for d in domains_list:
            executor.submit(worker, domain=d)
    print(f"\n[+] {len(domains_list)} domains tested - Results: ")
    with sqlite3.connect(DB_FILE) as connection:
        curs = connection.cursor()
        curs.execute("SELECT found, COUNT(found) FROM result GROUP BY found;")
        present_count = 0
        absent_count = 0
        for row in curs.fetchall():
            if row[0] == "PRESENT":
                present_count = row[1]
            else:
                absent_count = row[1]
        present_percentage = round((present_count * 100) / len(domains_list), 2)
        absent_percentage = round((absent_count * 100) / len(domains_list), 2)
        print(f"ABSENT  : {absent_count:<5} ({absent_percentage}%)")
        print(f"PRESENT : {present_count:<5} ({present_percentage}%)")
