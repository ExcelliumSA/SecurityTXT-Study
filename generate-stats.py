import requests
import sqlite3
import concurrent.futures

"""
Python3 script to compute stats about usage of "security.txt" file
on a panel of Luxemburgish domain taken from Certificate Transparency log:
    See https://crt.sh

Dependencies:
    pip install requests

Shell used to build the source file: 
    See script named "generate-source.sh"
"""
# Constants
SOURCE_FILE = "source.txt"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
NON_WEB_SUB_DOMAIN = ["*", "autodiscover", "sip", "pop", "pop3", "imap", "smtp", "ftp", "lyncdiscover", "lyncweb"]
FILE_LOCATIONS = ["/.well-known/security.txt", "/security.txt"]
PROTOCOLS = ["https", "http"]
DB_FILE = "data.db"
NON_WEB_SUB_DOMAIN.sort()

# Disable TLS warning when validation is disabled when requests is used
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Utilities functions
def prepare_domains_list():
    prepared_list = []
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
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
        found = (response.status_code == 200 
            and "Content-Type" in response.headers 
            and response.headers["Content-Type"] == "text/plain" 
            and "Contact: mailto:" in response.text
            and "Expires: " in response.text)
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
    print("[+] Prepare the list of domains...")
    domains_list = prepare_domains_list()
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
        for row in curs.fetchall():
            print(f"{row[0]:<7}: {row[1]}")
