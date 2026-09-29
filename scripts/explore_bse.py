"""Day 1 - Step 1: Talk to the BSE API, inspect the response, and download the PDF."""

import json

import requests


API_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"

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


params = {
    "pageno": 1,
    "strCat": "Company Update",
    "subcategory": "Earnings Call Transcript",
    "strPrevDate": "20260701",
    "strToDate": "20260731",
    "strSearch": "P",
    "strscrip": "532540",
    "strType": "C",
}


def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    print("Calling BSE API...")
    print()

    # 1. Call BSE announcement API
    response = session.get(
        API_URL,
        params=params,
        timeout=30,
    )

    print("Status code:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Final URL:")
    print(response.url)
    print()

    if response.status_code != 200:
        print("BSE rejected the request.")
        print(response.text[:2000])
        return

    # 2. Convert JSON response into Python objects
    data = response.json()

    print("Top-level keys:")
    print(data.keys())

    print("\nMetadata:")
    print(json.dumps(data["Table1"], indent=2))

    print("\nNumber of announcements:")
    print(len(data["Table"]))

    if not data["Table"]:
        print("No announcements found.")
        return

    # 3. Get the first announcement
    row = data["Table"][0]

    print("\nFirst announcement:")
    print(json.dumps(row, indent=2))

    # 4. Get the PDF filename
    print("\nAttachment name:")
    print(row["ATTACHMENTNAME"])

    # 5. Build the PDF URL
    pdf_url = (
        "https://www.bseindia.com/xml-data/corpfiling/AttachLive/"
        + row["ATTACHMENTNAME"]
    )

    print("\nPDF URL:")
    print(pdf_url)

    # 6. Download the PDF
    pdf_response = session.get(
        pdf_url,
        timeout=30,
    )

    print("\nPDF status code:", pdf_response.status_code)
    print("PDF content type:", pdf_response.headers.get("Content-Type"))
    print("PDF size:", len(pdf_response.content), "bytes")

    if pdf_response.status_code != 200:
        print("Failed to download PDF.")
    return

    with open("data/raw/TCS/transcript.pdf", "wb") as file:
        file.write(pdf_response.content)

    print("PDF saved successfully.")


if __name__ == "__main__":
    main()