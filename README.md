# Description

[![Test python script](https://github.com/ExcelliumSA/SecurityTXT-Study/actions/workflows/test-script.yml/badge.svg?branch=main)](https://github.com/ExcelliumSA/SecurityTXT-Study/actions/workflows/test-script.yml)

This project contains the materials used for the following blog post about the usage the [security.txt](https://securitytxt.org/) file:

XXXX

# Scripts

> Script call chain: `generate-source.(sh|ps1) > generate-stats.py`.

> Requirements for the python (**>= 3.7**) script are installed via the command: `pip install -r requirements.txt`

*[generate-source.sh](generate-source.sh):*

Extract a list of LU domains from Certificate Transparency log using [crt.sh](https://crt.sh) data provider.

*[generate-source.ps1](generate-source.ps1):*

Same goal the [generate-source.sh](generate-source.sh) but using direct database access in order to extract more records. This script deal with limitations in terms of execution time allowed for a SQL query.

*[generate-stats.py](generate-stats.py):*

Check for the presence of the *security.txt* file on the differents domains.

# Data file

> File [test-source.txt](test-source.txt) is the same file than [source.txt](source.txt). However, it contains a subset of the domains because it is only used for the [GitHub action workflow](.github/workflows/test-script.yml). The GitHub action workflow is used to allow the dependency checker of GitHub to verify that upgrading a dependency do not break the python script.

*[source.txt](source.txt):*

Contains the list of all LU domains gathered.

# Images

File with filename `IMG*.png` are just images used for the blog post.

# IDE

[Visual Studio Code](https://code.visualstudio.com/) are used for all the scripts.

A workspace file as well as a python debug configuration file are provided.

# References

* https://tools.ietf.org/html/draft-foudil-securitytxt  
* https://securitytxt.org/ 
* https://community.turgensec.com/security-txt-progress-in-ethical-security-research/ 
* http://s3.amazonaws.com/alexa-static/top-1m.csv.zip 
* https://certificate.transparency.dev/ 
* https://www.randori.com/enumerating-subdomains-with-crt-sh/ 
* https://github.com/crtsh/certwatch_db/blob/master/sql/create_schema.sql  
* https://hub.docker.com/_/postgres 
* https://twitter.com/search?q=vulnerability%20contact%20me%20&src=typed_query 
