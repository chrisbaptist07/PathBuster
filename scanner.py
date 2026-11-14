# scanner.py
# Job: try every path on the website and show the ones that exist.
# Author: Chris Jossy Baptist

import random
from concurrent.futures import ThreadPoolExecutor
from requester import request


def find_not_found_page(url):
    """Visit a page that surely does not exist, and remember the answer.

    Some websites answer "200 OK" for EVERY page, even missing ones.
    If we remember what that fake answer looks like (status + size),
    we can hide those fake results later."""
    fake_path = "/does-not-exist-" + str(random.randint(100000, 999999))
    response = request(url + fake_path)
    if response is None:
        return None

    status = response.status_code
    size = len(response.content)
    print(f"  A missing page gives: Status {status}, Size {size}")

    if status == 200:
        print("  Warning: this site says 200 OK even for missing pages!")
        print("  Results that look exactly like a missing page will be hidden.")

    return (status, size)


def check_path(url, path, good_codes, not_found):
    """Try one path. Return a result line, or None if it's not interesting."""
    response = request(url + path)
    if response is None:
        return None

    status = response.status_code
    size = len(response.content)

    if status not in good_codes:            # e.g. 404 = not there
        return None
    if (status, size) == not_found:          # looks like a fake "missing" page
        return None

    line = f"{path:<30} (Status: {status}) [Size: {size}]"

    # For redirects, show where the site sends us
    if status in (301, 302, 307, 308):
        line += f" [--> {response.headers.get('Location', '')}]"

    return line


def scan(url, paths, threads, good_codes, not_found):
    """Try all paths, several at the same time, and return the results."""
    results = []

    def check(path):
        return check_path(url, path, good_codes, not_found)

    # A "thread pool" is a group of workers.
    # pool.map gives each worker a path to check, so many paths
    # are checked at the same time instead of one by one.
    with ThreadPoolExecutor(max_workers=threads) as pool:
        for line in pool.map(check, paths):
            if line is not None:
                print(line)
                results.append(line)

    return results
