import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

CRIME_KEYWORDS = [
    "robbery", "murder", "killed", "arrested", "attack", "blast",
    "theft", "kidnapping", "assault", "firing", "shot", "dead",
    "rape", "abduct", "missing", "remand", "sentenced", "acid",
    "bomb", "explosion", "dacoity", "torture", "violence", "crime"
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

SOURCE_CITY_MAP = {
    "https://www.geo.tv/category/pakistan": None,
    "https://www.geo.tv/category/latest-news": None,
}

def is_crime_related(title):
    return any(kw.lower() in title.lower() for kw in CRIME_KEYWORDS)

def fetch_article_content(url):
    try:
        time.sleep(0.5)
        response = requests.get(url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        return " ".join(p.get_text(" ", strip=True) for p in paragraphs[:10])
    except:
        return ""

def get_published_date(tag):
    # Try Geo's structure
    time_tag = tag.find("time")
    if time_tag:
        dt = time_tag.get("datetime") or time_tag.get("title") or time_tag.text.strip()
        if dt:
            return dt[:10]

    # Try parent container
    parent = tag.find_parent("article") or tag.find_parent("div")
    if parent:
        time_tag = parent.find("time")
        if time_tag:
            dt = time_tag.get("datetime") or time_tag.get("title") or ""
            if dt:
                return dt[:10]

    return None



def scrape_geo():
    all_articles = []
    for url, source_city in SOURCE_CITY_MAP.items():
        try:
            print(f"Scraping {url}...")
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup.find_all("h2"):
                title = tag.text.strip()
                if not title or not is_crime_related(title):
                    continue
                link_tag = tag.find("a") or tag.find_parent("a")
                url_link = ""
                if link_tag and link_tag.get("href"):
                    url_link = link_tag["href"]
                    if url_link.startswith("/"):
                        url_link = "https://www.geo.tv" + url_link
                content = fetch_article_content(url_link) if url_link else ""
                all_articles.append({
                    "title": title, "url": url_link,
                    "source": "geo", "source_city": source_city,
                    "content": content,
                    "published_date": get_published_date(tag),
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
    articles = scrape_geo()
    print(f"\nFound {len(articles)} crime articles from Geo\n")
    for a in articles[:5]:
        print(f"  → {a['title']}")