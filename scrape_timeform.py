import requests
from bs4 import BeautifulSoup
import json
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

    # Dump the raw HTML so we can debug from GitHub
    with open("racecards_debug.html", "w") as f:
        f.write(soup.prettify())

    # Try primary selector
    links = soup.select(".racecard-list__item a")
    urls = []

    for link in links:
        href = link.get("href")
        if href and "/horse-racing/racecards/" in href:
            full_url = "https://www.timeform.com" + href
            urls.append(full_url)

    # Fallback: scan all <a> tags for matching pattern
    if not urls:
        print("[WARN] Primary selector returned nothing, using fallback <a> scan")
        for a in soup.find_all("a", href=True):
            href = a['href']
            if "/horse-racing/racecards/" in href:
                urls.append("https://www.timeform.com" + href)

    return list(set(urls))  # dedupe

def scrape_race(url):
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    header = {
        "track": soup.select_one(".card-header__location").text.strip() if soup.select_one(".card-header__location") else "",
        "time": soup.select_one(".card-header__time").text.strip() if soup.select_one(".card-header__time") else "",
        "title": soup.select_one(".card-header__title").text.strip() if soup.select_one(".card-header__title") else "",
        "url": url,
    }

    runners = []
    for runner in soup.select(".runner"):
        name = runner.select_one(".runner-name")
        jockey = runner.select_one(".jockey")
        trainer = runner.select_one(".trainer")
        form = runner.select_one(".form-figures")
        odds = runner.select_one(".odds")
        weight = runner.select_one(".weight")

        runners.append({
            "horse": name.text.strip() if name else "",
            "jockey": jockey.text.strip() if jockey else "",
            "trainer": trainer.text.strip() if trainer else "",
            "form": form.text.strip() if form else "",
            "odds": odds.text.strip() if odds else "",
            "weight": weight.text.strip() if weight else "",
        })

    return {"header": header, "runners": runners}

def main():
    print("[INFO] Gathering race URLs...")
    urls = get_race_urls()
    print(f"[INFO] Found {len(urls)} races.")

    all_races = []
    for url in urls:
        print(f"[SCRAPING] {url}")
        try:
            all_races.append(scrape_race(url))
        except Exception as e:
            print(f"[ERROR] Failed to scrape: {url} — {e}")

    with open("today.json", "w") as f:
        json.dump(all_races, f, indent=2)
    print("[DONE] Saved to today.json")

if __name__ == "__main__":
    main()
