import requests
from bs4 import BeautifulSoup
from datetime import date

BASE_URL = "https://www.timeform.com/horse-racing/racecards"
TODAY = date.today().strftime("%Y-%m-%d")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}

def get_race_urls():
    url = f"{BASE_URL}/{TODAY}"
    print(f"[INFO] Fetching: {url}")
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")

    links = soup.select(".racecard-list__item a")
    urls = []

    for link in links:
        href = link.get("href")
        if href and "/horse-racing/racecards/" in href:
            full_url = "https://www.timeform.com" + href
            urls.append(full_url)

    if not urls:
        print("[WARN] Primary selector returned nothing, using fallback <a> scan")
        for a in soup.find_all("a", href=True):
            href = a['href']
            if "/horse-racing/racecards/" in href:
                urls.append("https://www.timeform.com" + href)

    return list(set(urls))  # dedupe

def main():
    print("[INFO] Gathering race URLs...")
    urls = get_race_urls()
    print(f"[INFO] Found {len(urls)} races.")

    with open("today_urls.txt", "w") as f:
        for url in urls:
            f.write(url + "\n")

    print("[DONE] Saved to today_urls.txt")

if __name__ == "__main__":
    main()
