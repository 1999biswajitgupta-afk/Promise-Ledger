"""Day 1 - Step 1: Talk to the BSE API and inspect the response."""

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
        print()
        print("Response body:")
        print(response.text[:2000])
        return

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("BSE did not return JSON.")
        print()
        print("Response body:")
        print(response.text[:2000])
        return

    print("Total rows:", data["Table1"][0]["ROWCNT"])
    print()

    print("Announcements:")
    print("-" * 80)

    for row in data["Table"]:
        print(json.dumps(row, indent=2))


if __name__ == "__main__":
    main()