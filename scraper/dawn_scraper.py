import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time

CRIME_KEYWORDS = [
    "robbery", "murder", "killed", "arrested", "attack",
    "theft", "kidnapping", "assault", "firing", "dacoity",
    "stolen", "daaku", "loot", "crime", "police", "FIR",
    "shot", "dead", "body", "rape", "abduct", "missing"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

SOURCE_CITY_MAP = {
    "https://www.dawn.com/pakistan": None,
    "https://www.dawn.com/karachi": "Karachi",
    "https://www.dawn.com/lahore": "Lahore",
}

def is_crime_related(title):
    return any(kw.lower() in title.lower() for kw in CRIME_KEYWORDS)

def fetch_article_content(url):
    try:
        time.sleep(0.5)
        response = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        content = " ".join(p.get_text(" ", strip=True) for p in paragraphs[:10])
        return content
    except:
        return ""

def get_published_date(article):
    time_tag = article.find("span", class_="timestamp--time")
    if time_tag and time_tag.get("title"):
        return time_tag["title"][:10]  # "2026-06-25T13:16:34+05:00" → "2026-06-25"
    return None



def scrape_dawn():
    all_articles = []

    for url, source_city in SOURCE_CITY_MAP.items():
        try:
            print(f"Scraping {url}...")
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            for article in soup.find_all("article"):
                title_tag = article.find(["h2", "h3"])
                link_tag = article.find("a", href=True)

                if not title_tag:
                    continue

                title = title_tag.text.strip()

                if not is_crime_related(title):
                    continue

                url_link = link_tag["href"] if link_tag else ""
                if url_link.startswith("/"):
                    url_link = "https://www.dawn.com" + url_link

                content = fetch_article_content(url_link) if url_link else ""

                all_articles.append({
                    "title": title,
                    "url": url_link,
                    "source": "dawn",
                    "source_city": source_city,
                    "content": content,
                    "published_date": get_published_date(article), 
                    "scraped_at": datetime.now().isoformat()
                })

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    seen = set()
    unique = []
    for a in all_articles:
        if a["title"] not in seen:
            seen.add(a["title"])
            unique.append(a)

    return unique


if __name__ == "__main__":
    articles = scrape_dawn()
    print(f"\nFound {len(articles)} crime-related articles\n")
    for a in articles[:5]:
        print(f"  → {a['title']}")
        print(f"    {a['url']}\n")

    with open("dawn_results.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print("Saved to dawn_results.json")