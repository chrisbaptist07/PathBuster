# fingerprint.py
# Job: guess what technology a website is built with.
# Author: Chris Jossy Baptist
#
# We look for clues in 3 places:
#   1. headers  - extra info the server sends with every page
#   2. cookies  - small files the site saves in your browser
#   3. the page - the HTML of the homepage and of an error page

from requester import request

# Headers that often say which software the server runs
HEADERS_TO_SHOW = ["Server", "X-Powered-By", "X-Generator", "X-AspNet-Version", "Via"]

# If a cookie name contains this text, the site probably uses this technology
COOKIE_CLUES = {
    "PHPSESSID": "PHP",
    "JSESSIONID": "Java",
    "ASP.NET_SessionId": "ASP.NET",
    "laravel_session": "Laravel (PHP)",
    "csrftoken": "Django (Python)",
    "connect.sid": "Express (Node.js)",
    "wordpress": "WordPress",
    "_shopify": "Shopify",
}

# If the homepage HTML contains this text, the site probably uses this technology
PAGE_CLUES = {
    "wp-content": "WordPress",
    "cdn.shopify.com": "Shopify",
    "__NEXT_DATA__": "Next.js",
    "/_nuxt/": "Nuxt.js",
    "ng-version": "Angular",
    "data-reactroot": "React",
    "Drupal": "Drupal",
    "Joomla": "Joomla",
    "wixstatic.com": "Wix",
}

# Error pages often show the name of the server software
ERROR_PAGE_CLUES = {
    "Whitelabel Error Page": "Spring Boot (Java)",
    "Cannot GET": "Express (Node.js)",
    "<center>nginx": "nginx",
    "<address>Apache": "Apache",
    "Werkzeug": "Flask (Python)",
    "Page not found at /": "Django (Python), debug mode is ON",
    "Microsoft-IIS": "Microsoft IIS",
}


def find_clues(text, clues):
    """Return the technologies whose clue appears in the text."""
    found = []
    for clue, technology in clues.items():
        if clue.lower() in text.lower():
            found.append(technology)
    return found


def fingerprint(url):
    """Print what we can learn about the site.
    Return False if the site can't be reached."""
    home = request(url + "/")
    if home is None:
        print("  Could not reach the website.")
        return False

    error_page = request(url + "/this-page-does-not-exist-pathbuster")

    # 1. Headers
    for name in HEADERS_TO_SHOW:
        if name in home.headers:
            print(f"  {name}: {home.headers[name]}")

    # 2, 3. Cookies and page content
    technologies = []
    technologies += find_clues(home.headers.get("Set-Cookie", ""), COOKIE_CLUES)
    technologies += find_clues(home.text, PAGE_CLUES)
    if error_page is not None:
        technologies += find_clues(error_page.text, ERROR_PAGE_CLUES)

    if technologies:
        for technology in sorted(set(technologies)):
            print(f"  Technology: {technology}")
    else:
        print("  No technology clues found.")

    return True
