import requests
from bs4 import BeautifulSoup
import json
from datetime import date

BASE_URL = "https://www.timeform.com/horse-racing/racecards"
TODAY = date.today().strftime("%Y-%m-%d")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
} 

RACE_URLS = []

def get_race_urls():
    url = f"{BASE_URL}/{TODAY}"
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = soup.select(".racecard-list__item a")
    for link in links:
        href = link.get("href")
        if href and href.startswith("/horse-racing/racecards/"):
            full_url = "https://www.timeform.com" + href
            RACE_URLS.append(full_url)
    return list(set(RACE_URLS))

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
    all_races = []
    print(f"[INFO] Found {len(urls)} races.")

    for url in urls:
        print(f"[SCRAPING] {url}")
        try:
            all_races.append(scrape_race(url))
        except Exception as e:
            print(f"[ERROR] Skipping {url} — {e}")

    with open("today.json", "w") as f:
        json.dump(all_races, f, indent=2)
    print("[DONE] Saved to today.json")

if __name__ == "__main__":
    main()
