# main.py
# Job: read the options you typed and run the scan step by step. Start here.
# Author: Chris Jossy Baptist
#
# Examples:
#   python main.py -u https://example.com
#   python main.py -u https://example.com -w wordlist.txt -t 20
#   python main.py -u https://example.com -x php,html
#   python main.py -u https://example.com -s 200,301 -o results.txt
#   python main.py -u https://example.com -r              (also scan inside folders)
#   python main.py -u https://example.com -r --depth 2    (only go 2 levels deep)

import argparse
import time
from wordlist import load_wordlist
from fingerprint import fingerprint
from scanner import find_not_found_page, scan


def get_options():
    """Read the options typed after 'python main.py'."""
    parser = argparse.ArgumentParser(description="PathBuster - find hidden folders and files on a website")
    parser.add_argument("-u", "--url", required=True, help="website to scan, e.g. https://example.com")
    parser.add_argument("-w", "--wordlist", default="wordlist.txt", help="file of words to try (default: wordlist.txt)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="how many requests at the same time (default: 10)")
    parser.add_argument("-x", "--extensions", default="", help="extensions to add to each word, e.g. php,html")
    parser.add_argument("-s", "--status", default="200,204,301,302,307,401,403", help="status codes to show")
    parser.add_argument("-o", "--output", help="save the results to this file")
    parser.add_argument("-r", "--recursive", action="store_true", help="also scan inside every folder found")
    parser.add_argument("--depth", type=int, default=3, help="how many levels deep to go with -r (default: 3)")
    return parser.parse_args()


def main():
    options = get_options()

    url = options.url.rstrip("/")
    if not url.startswith("http"):
        url = "https://" + url

    paths = load_wordlist(options.wordlist, options.extensions)
    good_codes = [int(code) for code in options.status.split(",")]

    # Without -r we only scan 1 level (the top of the website)
    if options.recursive:
        max_depth = options.depth
    else:
        max_depth = 1

    print("=" * 60)
    print(" PathBuster - by Chris Jossy Baptist")
    print("=" * 60)
    print(f" Target:     {url}")
    print(f" Wordlist:   {options.wordlist} ({len(paths)} paths)")
    print(f" Threads:    {options.threads}")
    print(f" Status:     {options.status}")
    if options.extensions:
        print(f" Extensions: {options.extensions}")
    if options.recursive:
        print(f" Recursive:  ON ({max_depth} levels deep)")
    print("=" * 60)

    # Step 1: what technology does the site use?
    print("\n[1] Fingerprinting the website ...")
    if not fingerprint(url):
        return

    # Step 2: what does a "page not found" look like on this site?
    print("\n[2] Checking what a missing page looks like ...")
    not_found = find_not_found_page(url)

    # Step 3: try every path
    print(f"\n[3] Trying {len(paths)} paths ...\n")
    start = time.time()
    results = scan(url, paths, options.threads, good_codes, not_found, max_depth)
    seconds = time.time() - start

    print(f"\nDone! Found {len(results)} paths in {seconds:.1f} seconds.")

    # Step 4: save the results (only if -o was used)
    if options.output:
        with open(options.output, "w") as file:
            file.write("\n".join(results) + "\n")
        print(f"Saved the results to {options.output}")


main()
