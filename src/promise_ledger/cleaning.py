"""Clean text extracted from earnings-call transcript PDFs."""

import re
import unicodedata
from collections import Counter

# Characters our corpus produces that Unicode normalisation doesn't fix.
CHAR_FIXES = {
    "\u01af": "ff",  # 'Ư': TCS's font maps the ff ligature here ("diƯerent")
    "\uf0b7": "-",   # private-use bullet glyphs
    "\uf02d": "-",
    "\uf0d8": "-",
    "\u2022": "-",   # bullet •
    "\xad": "",      # invisible soft hyphen
    "\u2018": "'",   # curly quotes -> straight
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",   # dashes
    "\u2014": "-",
    "\u2011": "-",
}

PAGE_NUMBER_LINE = re.compile(r"^\s*(page\s*)?\d+\s*(of\s*\d+)?\s*$", re.IGNORECASE)
COVER_LETTER_SIGNS = ("dear sir", "bse limited", "national stock exchange")


def fix_characters(text: str) -> str:
    """Fix ligatures, odd glyphs and fancy punctuation."""
    text = unicodedata.normalize("NFKC", text)  # ﬁ -> fi, ﬀ -> ff, thin space -> space
    for bad, good in CHAR_FIXES.items():
        text = text.replace(bad, good)
    return text


def is_cover_letter(page: str) -> bool:
    """A letter to the stock exchanges, not part of the call itself."""
    low = page.lower()
    return sum(sign in low for sign in COVER_LETTER_SIGNS) >= 2

def line_pattern(line: str) -> str:
    """Treat lines that differ only in numbers as the same line."""
    return re.sub(r"\d+", "#", line.strip())


def find_boilerplate(pages: list[str], edge_lines: int = 3) -> set[str]:
    """Headers/footers: lines at the top or bottom of MOST pages."""
    if len(pages) < 4:
        return set()
    counts = Counter()
    for page in pages:
        lines = [line.strip() for line in page.splitlines() if line.strip()]
        counts.update({line_pattern(line) for line in lines[:edge_lines] + lines[-edge_lines:]})
    threshold = len(pages) * 0.5
    return {line for line, n in counts.items() if n >= threshold}


def clean_pages(pages: list[str]) -> tuple[str, int]:
    """Turn raw PDF pages into clean transcript text.

    Returns the cleaned text and how many cover-letter pages were dropped.
    """
    pages = [fix_characters(page) for page in pages]

    dropped = 0
    while pages and dropped < 2 and is_cover_letter(pages[0]):
        pages = pages[1:]
        dropped += 1

    boilerplate = find_boilerplate(pages)
    kept_lines = []
    for page in pages:
        for line in page.splitlines():
            stripped = line.strip()
            if not stripped or line_pattern(stripped) in boilerplate:
                continue
            if PAGE_NUMBER_LINE.match(stripped):
                continue
            kept_lines.append(re.sub(r"\s+", " ", stripped))

    return "\n".join(kept_lines), dropped