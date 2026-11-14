# scanner.py
# Job: try every path on the website and show the ones that exist.
#      With recursion ON, it also looks inside every folder it finds.
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
    """Try one path.
    Return a result like {"path": "/admin", "line": "...", "is_folder": True},
    or None if it's not interesting."""
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
    is_folder = False

    # For redirects, show where the site sends us
    if status in (301, 302, 307, 308):
        location = response.headers.get("Location", "")
        line += f" [--> {location}]"

        # /admin  -->  /admin/   means "/admin" is a FOLDER
        if location.endswith(path + "/"):
            is_folder = True

    return {"path": path, "line": line, "is_folder": is_folder}


def scan_folder(url, folder, paths, threads, good_codes, not_found):
    """Try every path inside ONE folder.
    folder is "" for the top of the website, or something like "/admin"."""
    found = []

    def check(path):
        return check_path(url, folder + path, good_codes, not_found)

    # A "thread pool" is a group of workers.
    # pool.map gives each worker a path to check, so many paths
    # are checked at the same time instead of one by one.
    with ThreadPoolExecutor(max_workers=threads) as pool:
        for result in pool.map(check, paths):
            if result is not None:
                print(result["line"])
                found.append(result)

    return found


def scan(url, paths, threads, good_codes, not_found, max_depth):
    """Scan the website, level by level.

    Level 1: the top of the site         -> finds /admin
    Level 2: inside the folders found    -> finds /admin/backup
    Level 3: inside those folders        -> finds /admin/backup/old
    ...until max_depth is reached."""
    all_results = []
    already_scanned = []
    folders_to_scan = [""]       # "" = the top of the website
    level = 1

    while folders_to_scan and level <= max_depth:
        next_folders = []

        for folder in folders_to_scan:
            if folder in already_scanned:
                continue
            already_scanned.append(folder)

            if folder != "":
                print(f"\n--- Level {level}: scanning inside {folder}/ ---")

            found = scan_folder(url, folder, paths, threads, good_codes, not_found)
            all_results += found

            # Remember the new folders, to scan inside them next
            for result in found:
                if result["is_folder"]:
                    next_folders.append(result["path"])

        folders_to_scan = next_folders
        level += 1

    # Just the text lines, for printing and saving
    return [result["line"] for result in all_results]
