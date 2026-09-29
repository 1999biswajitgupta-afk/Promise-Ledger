"""Day 1 - Step 2: download earnings-call transcripts for all companies."""

import csv
import time
from datetime import datetime
from pathlib import Path

import requests

API_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
PDF_BASE_URL = "https://www.bseindia.com/xml-data/corpfiling/AttachLive/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.bseindia.com",
    "Referer": "https://www.bseindia.com/",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
}

FROM_DATE = "20251001"  # covers Q2 FY26 to Q1 FY27 = last 4 quarters
TO_DATE = "20260928"
RAW_DIR = Path("data/raw")
MANIFEST_PATH = Path("data/manifest.csv")


def quarter_label(filed: datetime) -> str:
    """Turn a filing date into the quarter the call was about.

    Indian financial year runs Apr-Mar. A call held in July discusses
    Apr-Jun, which is Q1 of the financial year ending next March.
    """
    month, year = filed.month, filed.year
    if 7 <= month <= 9:
        return f"Q1FY{(year + 1) % 100}"
    if month >= 10:
        return f"Q2FY{(year + 1) % 100}"
    if month <= 3:
        return f"Q3FY{year % 100}"
    return f"Q4FY{year % 100}"


def fetch_transcript_rows(session: requests.Session, bse_code: str) -> list[dict]:
    """Get every transcript announcement for one company, page by page."""
    rows = []
    page = 1
    while True:
        params = {
            "pageno": page,
            "strCat": "Company Update",
            "subcategory": "Earnings Call Transcript",
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


def download_pdf(session: requests.Session, attachment: str, path: Path) -> str:
    """Download one PDF. Skip it if we already have it."""
    if path.exists():
        return "skipped (already have it)"

    response = session.get(PDF_BASE_URL + attachment, timeout=60)
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        return "FAILED (not a PDF)"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)
    return f"downloaded ({len(response.content):,} bytes)"


def main():
    with open("config/companies.csv", encoding="utf-8") as f:
        companies = list(csv.DictReader(f))

    session = requests.Session()
    session.headers.update(HEADERS)
    manifest = []

    for company in companies:
        symbol = company["symbol"]
        print(f"\n{symbol} (BSE {company['bse_code']})")

        try:
            rows = fetch_transcript_rows(session, company["bse_code"])
        except requests.RequestException as error:
            print("   API call failed:", error)
            continue

        if not rows:
            print("   no transcripts found")
            continue
        print("   BSE name:", rows[0]["SLONGNAME"])

        for row in rows:
            filed = datetime.fromisoformat(row["NEWS_DT"][:19])
            quarter = quarter_label(filed)
            filename = f"{symbol}_{quarter}_{filed:%Y%m%d}.pdf"
            path = RAW_DIR / symbol / filename
            headline = (row["HEADLINE"] or "").strip()

            try:
                status = download_pdf(session, row["ATTACHMENTNAME"], path)
            except requests.RequestException as error:
                status = f"FAILED ({error})"

            print(f"   {quarter}  {filed:%Y-%m-%d}  {status}")
            print(f"      {headline[:90]}")

            manifest.append({
                "symbol": symbol,
                "quarter": quarter,
                "filed_date": f"{filed:%Y-%m-%d}",
                "headline": headline,
                "attachment": row["ATTACHMENTNAME"],
                "local_path": str(path),
                "status": status,
            })
            time.sleep(1)

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest[0].keys())
        writer.writeheader()
        writer.writerows(manifest)

    downloaded = sum(1 for m in manifest if m["status"].startswith("downloaded"))
    print(f"\nDone. {len(manifest)} transcripts found, {downloaded} newly downloaded.")
    print(f"Manifest saved to {MANIFEST_PATH}")


if __name__ == "__main__":
    main()