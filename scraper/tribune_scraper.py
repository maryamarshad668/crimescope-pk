import requests
from bs4 import BeautifulSoup
from datetime import datetime

CRIME_KEYWORDS = [
    "robbery", "murder", "killed", "arrested", "attack", "blast",
    "theft", "kidnapping", "assault", "firing", "shot", "dead",
    "rape", "abduct", "missing", "remand", "sentenced", "acid",
    "bomb", "explosion", "dacoity", "torture", "violence", "crime",
    "police", "FIR", "daaku", "loot", "body found", "recovered",
    "stabbed", "burned", "honour killing", "target killing"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

SOURCE_CITIES = {
    "https://tribune.com.pk/pakistan": None,
    "https://tribune.com.pk/karachi": "Karachi",
    "https://tribune.com.pk/lahore": "Lahore",
}

def is_crime_related(title):
    return any(kw.lower() in title.lower() for kw in CRIME_KEYWORDS)

def scrape_tribune():
    all_articles = []

    for url, source_city in SOURCE_CITIES.items():
        try:
            print(f"Scraping {url}...")
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            # Tribune: h2 inside div.sport-section1-right, wrapped in <a>
            for div in soup.find_all("div", class_="sport-section1-right"):
                title_tag = div.find("h2")
                if not title_tag:
                    continue

                title = title_tag.text.strip()
                if not is_crime_related(title):
                    continue

                link_tag = div.find("a", href=True)
                url_link = link_tag["href"] if link_tag else ""
                if url_link.startswith("/"):
                    url_link = "https://tribune.com.pk" + url_link

                # Tribune shows "Updated 9 hours ago" — use today as fallback
                published_date = datetime.now().strftime("%Y-%m-%d")
                author_div = div.find("div", class_="author-detail")
                if author_div:
                    text = author_div.text
                    # Sometimes shows actual date like "Jun 25, 2026"
                    import re
                    match = re.search(r'(\w+ \d+, \d{4})', text)
                    if match:
                        try:
                            published_date = datetime.strptime(
                                match.group(1), "%b %d, %Y"
                            ).strftime("%Y-%m-%d")
                        except:
                            pass

                all_articles.append({
                    "title": title,
                    "url": url_link,
                    "source": "tribune",
                    "source_city": source_city,
                    "published_date": published_date,
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
    articles = scrape_tribune()
    print(f"\n✅ Found {len(articles)} crime articles from Tribune\n")
    for a in articles[:5]:
        print(f"  → {a['title']}")
        print(f"    {a['url']}\n")