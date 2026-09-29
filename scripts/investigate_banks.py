"""Day 1 - Step 3: find out how banks label their call transcripts on BSE."""

import time
from collections import Counter

import requests

from download_transcripts import API_URL, FROM_DATE, HEADERS, TO_DATE

BANKS = {"HDFCBANK": "500180", "ICICIBANK": "532174", "AXISBANK": "532215"}


def fetch_all_announcements(session: requests.Session, bse_code: str) -> list[dict]:
    """Every announcement for one company, any category ("-1" = all)."""
    rows, page = [], 1
    while True:
        params = {
            "pageno": page,
            "strCat": "-1",
            "subcategory": "-1",
            "strPrevDate": FROM_DATE,
            "strToDate": TO_DATE,
            "strSearch": "P",
            "strscrip": bse_code,
            "strType": "C",
        }
        response = session.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        rows.extend(data["Table"])
        total = data["Table1"][0]["ROWCNT"] if data["Table1"] else 0
        if not data["Table"] or len(rows) >= total:
            return rows
        page += 1
        time.sleep(1)


def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    for symbol, code in BANKS.items():
        rows = fetch_all_announcements(session, code)
        print(f"\n===== {symbol}: {len(rows)} announcements in total =====")

        matches = [
            r for r in rows
            if "transcript" in f"{r['NEWSSUB']} {r['HEADLINE']}".lower()
        ]
        print(f"{len(matches)} mention 'transcript':")
        for r in matches:
            print(f"   {r['NEWS_DT'][:10]} | {r['CATEGORYNAME']} > {r['SUBCATNAME']}")
            print(f"      {(r['HEADLINE'] or '')[:100]}")

        top = Counter(r["SUBCATNAME"] for r in rows).most_common(8)
        print("Most common subcategories:", top)


if __name__ == "__main__":
    main()