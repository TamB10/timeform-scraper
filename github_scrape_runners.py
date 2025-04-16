import requests
from bs4 import BeautifulSoup
import json
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def scrape_race(url):
    print(f"[SCRAPING] {url}")
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
    print("[INFO] Reading URLs from today_urls.txt")
    try:
        with open("today_urls.txt", "r") as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("[ERROR] today_urls.txt not found.")
        return

    all_races = []
    for url in urls[:8]:  # Limit to 8 races
        try:
            race_data = scrape_race(url)
            all_races.append(race_data)
            time.sleep(8)  # Safe delay
        except Exception as e:
            print(f"[ERROR] Failed to scrape {url} — {e}")

    with open("runners.json", "w") as f:
        json.dump(all_races, f, indent=2)

    print("[DONE] runners.json saved.")

if __name__ == "__main__":
    main()
