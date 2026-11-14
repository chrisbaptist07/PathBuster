# wordlist.py
# Job: read the wordlist file and turn every word into a path to try.
# Author: Chris Jossy Baptist
#
# Example: if the wordlist has "admin" and you use -x php,html
# we will try:  /admin   /admin.php   /admin.html

import os
import sys


def load_wordlist(filename, extensions):
    """Return a list of paths like ["/admin", "/admin.php", ...]."""
    if not os.path.exists(filename):
        print(f"Wordlist not found: {filename}")
        sys.exit()

    # "php, .html" -> ["php", "html"]
    extension_list = []
    for ext in extensions.split(","):
        ext = ext.strip().lstrip(".")
        if ext != "":
            extension_list.append(ext)

    paths = []
    with open(filename) as file:
        for line in file:
            word = line.split("#")[0].strip()   # anything after # is a note
            word = word.strip("/")
            if word == "":
                continue

            new_paths = ["/" + word]
            for ext in extension_list:
                new_paths.append("/" + word + "." + ext)

            for path in new_paths:
                if path not in paths:           # no repeats
                    paths.append(path)

    return paths
