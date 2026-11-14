# requester.py
# Job: visit one web address and give back the website's answer.
# Author: Chris Jossy Baptist

import requests

# How our tool introduces itself to websites
HEADERS = {"User-Agent": "PathBuster/1.0"}


def request(url):
    """Visit one URL and return the response.
    If the website does not answer, return None.

    allow_redirects=False means: if the site says "go to another page",
    we don't follow it. We want to SEE that redirect (status 301/302)."""
    try:
        return requests.get(url, headers=HEADERS, timeout=10, allow_redirects=False)
    except requests.RequestException:
        return None
