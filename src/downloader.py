import requests
import os
from pathlib import Path

BASE_JSON = "https://data.sec.gov/submissions/CIK{cik}.json"
HEADERS = {"User-Agent": "Uniqus ai RAG-Financial-QA (amalajohn2000@gmail.com)"}

CIKS = {
    "GOOGL": "0001652044",
    "MSFT": "0000789019",
    "NVDA": "0001045810",
}

YEARS = [2022, 2023, 2024]

def download_10k(cik, ticker, year, out_dir="data"):
    os.makedirs(out_dir, exist_ok=True)

    url = BASE_JSON.format(cik=cik.zfill(10))
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()

    # Look for 10-K in that year
    filings = data.get("filings", {}).get("recent", {})
    forms = filings.get("form", [])
    dates = filings.get("filingDate", [])
    accession = filings.get("accessionNumber", [])
    primdocs = filings.get("primaryDocument", [])

    found = False
    for form, date, acc, doc in zip(forms, dates, accession, primdocs):
        if form == "10-K" and date.startswith(str(year)):
            acc_no_dashes = acc.replace("-", "")
            url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no_dashes}/{doc}"
            out_path = Path(out_dir) / f"{ticker}_{year}.html"
            print(f"Downloading {ticker} {year} 10-K from {url}")
            r = requests.get(url, headers=HEADERS)
            with open(out_path, "wb") as f:
                f.write(r.content)
            found = True
            break

    if not found:
        print(f"No 10-K found for {ticker}, {year}")

if __name__ == "__main__":
    for ticker, cik in CIKS.items():
        for year in YEARS:
            download_10k(cik, ticker, year)
