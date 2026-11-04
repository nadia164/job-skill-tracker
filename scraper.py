import requests
from bs4 import BeautifulSoup

TIMEOUT_SECONDS = 15
MIN_CHARS = 200
MAX_CHARS = 20000

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobSkillTracker/1.0)"}

BLOCKED_STATUS_CODES = (401, 403, 429, 999)

INVISIBLE_CHARACTERS = ["\u200b", "\u200c", "\u200d", "\ufeff", "\u00a0"]


class FetchError(Exception):
    pass


def clean_url(url):
    for character in INVISIBLE_CHARACTERS:
        url = url.replace(character, "")

    url = url.strip().strip("<>\"'").strip()

    if "://" not in url and "." in url:
        url = "https://" + url

    return url


def fetch_posting_text(url):
    url = clean_url(url)

    if not url.lower().startswith(("http://", "https://")):
        raise FetchError(
            f"Enter a full link starting with http:// or https:// (the app received: {url[:80]!r})"
        )

    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as error:
        raise FetchError("Couldn't reach this page. Check the link and your internet connection.") from error

    if response.status_code in BLOCKED_STATUS_CODES:
        raise FetchError("This site blocks automated access. Copy the posting text and paste it instead.")

    if response.status_code != 200:
        raise FetchError(f"The page returned an error (status {response.status_code}).")

    soup = BeautifulSoup(response.text, "html.parser")
    page_title = soup.title.get_text(strip=True) if soup.title else ""

    for tag in soup(["script", "style", "noscript", "svg", "nav", "header", "footer"]):
        tag.decompose()

    lines = [line.strip() for line in soup.get_text(separator="\n").splitlines()]
    text = "\n".join(line for line in lines if line)

    if len(text) < MIN_CHARS:
        raise FetchError(
            "Couldn't find the posting text on this page. It may need a login or load its content "
            "with JavaScript. Copy the posting text and paste it instead."
        )

    return page_title, text[:MAX_CHARS]