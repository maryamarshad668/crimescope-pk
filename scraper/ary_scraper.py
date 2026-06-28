import requests
from bs4 import BeautifulSoup
from datetime import datetime

CRIME_KEYWORDS = [
    "robbery", "murder", "killed", "arrested", "attack", "blast",
    "theft", "kidnapping", "assault", "firing", "shot", "dead",
    "rape", "abduct", "missing", "remand", "sentenced", "acid",
    "bomb", "explosion", "dacoity", "torture", "violence", "crime",
    "police", "FIR", "daaku", "loot", "body found", "recovered"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

SOURCE_CITIES = {
    "https://arynews.tv/category/pakistan/": None,
    "https://arynews.tv/category/karachi/": "Karachi",
    "https://arynews.tv/category/lahore/": "Lahore",
}

def is_crime_related(title):
    return any(kw.lower() in title.lower() for kw in CRIME_KEYWORDS)

def get_published_date(article):
    # ARY shows "Updated 38 mins ago" — not reliable for exact date
    # So we fall back to today's date
    return datetime.now().strftime("%Y-%m-%d")

def scrape_ary():
    all_articles = []

    for url, source_city in SOURCE_CITIES.items():
        try:
            print(f"Scraping {url}...")
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            for article in soup.find_all("article"):
                # ARY uses <h3> inside article
                title_tag = article.find("h3") or article.find("h2")
                link_tag = article.find("a", href=True)

                if not title_tag:
                    continue

                title = title_tag.text.strip()

                if not is_crime_related(title):
                    continue

                url_link = link_tag["href"] if link_tag else ""
                if url_link.startswith("/"):
                    url_link = "https://arynews.tv" + url_link

                all_articles.append({
                    "title": title,
                    "url": url_link,
                    "source": "ary",
                    "source_city": source_city,
                    "published_date": get_published_date(article),
                    "scraped_at": datetime.now().isoformat()
                })

        except Exception as e:
            print(f"Error scraping {url}: {e}")

    # Remove duplicates
    seen = set()
    unique = []
    for a in all_articles:
        if a["title"] not in seen:
            seen.add(a["title"])
            unique.append(a)

    return unique

if __name__ == "__main__":
    articles = scrape_ary()
    print(f"\n✅ Found {len(articles)} crime articles from ARY\n")
    for a in articles[:5]:
        print(f"  → {a['title']}")
        print(f"    {a['url']}\n")