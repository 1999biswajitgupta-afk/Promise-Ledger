"""Day 2 - Step 1: extract clean text from every downloaded PDF."""

import csv
from collections import Counter
from pathlib import Path

import pymupdf

from promise_ledger.cleaning import clean_pages

MANIFEST_PATH = Path("data/manifest.csv")
OUT_DIR = Path("data/processed")
OUT_MANIFEST = OUT_DIR / "extracted.csv"
MIN_TRANSCRIPT_CHARS = 5000  # link-only letters are ~1-3k characters


def main():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for row in rows:
        pdf_path = Path(row["local_path"])
        if not pdf_path.exists():
            continue

        with pymupdf.open(pdf_path) as doc:
            pages = [page.get_text() for page in doc]

        text, cover_pages = clean_pages(pages)
        doc_type = "transcript" if len(text) >= MIN_TRANSCRIPT_CHARS else "link_only"

        out_path = OUT_DIR / f"{pdf_path.stem}.txt"
        out_path.write_text(text, encoding="utf-8")

        results.append({
            "symbol": row["symbol"],
            "quarter": row["quarter"],
            "filed_date": row["filed_date"],
            "headline": row["headline"],
            "pdf_path": str(pdf_path),
            "text_path": str(out_path),
            "pages": len(pages),
            "cover_pages_dropped": cover_pages,
            "chars": len(text),
            "doc_type": doc_type,
        })
        print(f"{doc_type:10} {len(text):>7,} chars  {pdf_path.name}")

    with open(OUT_MANIFEST, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print("\n", Counter(r["doc_type"] for r in results))
    print(f"Saved {len(results)} text files + {OUT_MANIFEST}")


if __name__ == "__main__":
    main()