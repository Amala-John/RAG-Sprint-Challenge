import requests
import time
from pathlib import Path
import re
from bs4 import BeautifulSoup

COMPANIES = {
    "GOOGL": "1652044",
    "MSFT": "789019",
    "NVDA": "1045810"
}

YEARS = ["2022", "2023", "2024"]

def download_10k_filing(cik, ticker, year, data_dir="data"):
    Path(data_dir).mkdir(exist_ok=True)
    
    filename = f"{ticker}_{year}.html"
    filepath = Path(data_dir) / filename
    if filepath.exists():
        print(f"📁 {filename} already exists, skipping...")
        return True
    
    search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={cik}&type=10-K&dateb={year}1231&count=10"
    
    headers = {
        'User-Agent': 'Financial-QA-System research-tool (contact@example.com)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate'
    }
    
    try:
        print(f"🔍 Searching for {ticker} 10-K filing for {year}...")
        response = requests.get(search_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        filing_link = None
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 4:
                doc_type = cells[0].get_text(strip=True)
                if doc_type == '10-K':
                    for link in cells[1].find_all('a', href=True):
                        if 'Documents' in link.get_text():
                            filing_link = 'https://www.sec.gov' + link['href']
                            break
                    if filing_link:
                        break
        
        if not filing_link:
            print(f"❌ No 10-K filing found for {ticker} in {year}")
            return False
        
        time.sleep(1.5)
        print(f"📄 Accessing filing documents...")
        doc_response = requests.get(filing_link, headers=headers, timeout=30)
        doc_response.raise_for_status()
        
        doc_soup = BeautifulSoup(doc_response.content, 'html.parser')
        
        doc_link = None
        for row in doc_soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 3:
                doc_name = cells[2].get_text(strip=True)
                if doc_name.endswith('.htm') and cells[3].get_text(strip=True) == '10-K':
                    link_elem = cells[2].find('a', href=True)
                    if link_elem:
                        doc_link = 'https://www.sec.gov' + link_elem['href']
                        break
        
        if not doc_link:
            for link in doc_soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.htm') and not href.endswith('_ex.htm'):
                    doc_link = 'https://www.sec.gov' + href
                    break
        
        if not doc_link:
            print(f"❌ No HTML document found for {ticker} {year}")
            return False
        
        # Download the actual 10-K HTML file
        time.sleep(1.5)
        print(f"⬇️  Downloading 10-K document...")
        filing_response = requests.get(doc_link, headers=headers, timeout=60)
        filing_response.raise_for_status()
        
        # Save the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(filing_response.text)
        
        print(f"✅ Downloaded {filename} ({len(filing_response.text):,} characters)")
        return True
        
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout downloading {ticker} {year}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"🌐 Network error downloading {ticker} {year}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error downloading {ticker} {year}: {e}")
        return False

def download_all_filings(data_dir="data"):
    """Download all required 10-K filings for the assignment"""
    print("🏦 Financial Q&A System: SEC 10-K Filing Downloader")
    print("📋 Companies: Google (GOOGL), Microsoft (MSFT), NVIDIA (NVDA)")
    print("📅 Years: 2022, 2023, 2024")
    print("=" * 60)
    
    success_count = 0
    total_count = len(COMPANIES) * len(YEARS)
    
    for ticker, cik in COMPANIES.items():
        company_name = {"GOOGL": "Google", "MSFT": "Microsoft", "NVDA": "NVIDIA"}[ticker]
        print(f"\n🏢 Processing {company_name} ({ticker}) - CIK: {cik}")
        
        for year in YEARS:
            if download_10k_filing(cik, ticker, year, data_dir):
                success_count += 1
            time.sleep(2)  # Be respectful to SEC servers
    
    print(f"\n" + "=" * 60)
    print(f"📊 Download Summary:")
    print(f"✅ Successfully downloaded: {success_count}/{total_count} filings")
    
    if success_count == total_count:
        print("🎉 All filings downloaded successfully!")
        print("▶️  You can now run: python src/main.py")
    elif success_count > 0:
        print("⚠️  Some filings failed to download. The system will work with available files.")
        print("▶️  You can still run: python src/main.py")
    else:
        print("❌ No filings were downloaded. Please check your internet connection and try again.")
    
    return success_count > 0

if __name__ == "__main__":
    success = download_all_filings()
    if success:
        print(f"\n🚀 Ready to run the Financial Q&A System!")
    else:
        print(f"\n🔧 Please fix download issues and try again.")
