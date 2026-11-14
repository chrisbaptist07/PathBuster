# PathBuster

A simple Python tool that finds hidden folders and files on a website, like **gobuster**.

**Author:** Chris Jossy Baptist

## How it works

1. **Fingerprints the website.** It looks at headers, cookies and pages to guess the technology (WordPress, PHP, Node.js, nginx...).
2. **Checks what a missing page looks like.** Some websites answer "200 OK" even for pages that don't exist. The tool remembers that fake answer and hides results that look the same.
3. **Tries every word in the wordlist**, several at the same time (threads), e.g. `/admin`, `/backup.zip`, `/.env`.
4. **Shows the paths that exist** with their status code and size, and can save them to a file.
5. **Recursive mode (`-r`):** when it finds a folder like `/admin/`, it scans inside it too, level by level.

## Files

| File | What it does |
|---|---|
| `main.py` | Reads your options and runs everything. **Start here.** |
| `requester.py` | Visits one web address |
| `wordlist.py` | Reads the wordlist and adds extensions |
| `fingerprint.py` | Guesses the website's technology |
| `scanner.py` | Tries all paths using threads, and goes inside folders with `-r` |
| `wordlist.txt` | 121 common folder and file names |

## How to run

```
pip install -r requirements.txt
python main.py -u https://example.com
```

## Options

| Option | Meaning | Example |
|---|---|---|
| `-u` | Website to scan (required) | `-u https://example.com` |
| `-w` | Wordlist file (default: `wordlist.txt`) | `-w my_words.txt` |
| `-t` | Requests at the same time (default: 10) | `-t 20` |
| `-x` | Extensions to add to each word | `-x php,html` |
| `-s` | Status codes to show | `-s 200,301` |
| `-o` | Save results to a file | `-o results.txt` |
| `-r` | Also scan inside every folder found | `-r` |
| `--depth` | How many levels deep `-r` goes (default: 3) | `--depth 2` |

## Recursive scan example

```
python main.py -u https://example.com -r
```

```
/admin                         (Status: 301) [Size: 0] [--> /admin/]
/robots.txt                    (Status: 200) [Size: 2]

--- Level 2: scanning inside /admin/ ---
/admin/backup                  (Status: 301) [Size: 0] [--> /admin/backup/]
/admin/config.php              (Status: 200) [Size: 2]

--- Level 3: scanning inside /admin/backup/ ---
/admin/backup/site.zip         (Status: 200) [Size: 2]
```

The tool knows a path is a folder when the website redirects it to the same path with a `/` at the end (`/admin` → `/admin/`).

## Status codes

| Code | Meaning |
|---|---|
| 200 | Found |
| 301 / 302 | Redirect (often a folder) |
| 401 | Needs a login |
| 403 | Exists, but access is blocked |
| 404 | Not found (hidden by default) |

## Example output

```
[1] Fingerprinting the website ...
  Server: nginx
  Technology: WordPress

[2] Checking what a missing page looks like ...
  A missing page gives: Status 404, Size 335

[3] Trying 241 paths ...

/admin                         (Status: 301) [Size: 0] [--> /admin/]
/login.php                     (Status: 200) [Size: 9]
/backup.zip                    (Status: 200) [Size: 4]
/.env                          (Status: 200) [Size: 15]
/robots.txt                    (Status: 200) [Size: 14]

Done! Found 5 paths in 0.3 seconds.
```

> ⚠️ Only scan websites you own or have permission to test.
