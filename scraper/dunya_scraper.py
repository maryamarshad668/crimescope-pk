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
    "https://dunyanews.tv/index.php/en/Pakistan": None,
    "https://dunyanews.tv/index.php/en/Karachi": "Karachi",
    "https://dunyanews.tv/index.php/en/Lahore": "Lahore",
}

def is_crime_related(title):
    return any(kw.lower() in title.lower() for kw in CRIME_KEYWORDS)

def scrape_dunya():
    all_articles = []

    for url, source_city in SOURCE_CITIES.items():
        try:
            print(f"Scraping {url}...")
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            # Dunya: h2 inside div.cpage-image__text, date in span.time_span_section_white
            for div in soup.find_all("div", class_="cpage-image__text"):
                title_tag = div.find("h2")
                if not title_tag:
                    continue

                title = title_tag.text.strip()
                if not is_crime_related(title):
                    continue

                link_tag = div.find("a", href=True) or div.find_parent("a")
                url_link = ""
                if link_tag and link_tag.get("href"):
                    url_link = link_tag["href"]
                    if url_link.startswith("/"):
                        url_link = "https://dunyanews.tv" + url_link

                # Date is in span.time_span_section_white → "2026-06-25 23:23:10"
                date_tag = div.find("span", class_="time_span_section_white")
                published_date = None
                if date_tag:
                    published_date = date_tag.text.strip()[:10]

                all_articles.append({
                    "title": title,
                    "url": url_link,
                    "source": "dunya",
                    "source_city": source_city,
                    "published_date": published_date or datetime.now().strftime("%Y-%m-%d"),
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
    articles = scrape_dunya()
    print(f"\n✅ Found {len(articles)} crime articles from Dunya\n")
    for a in articles[:5]:
        print(f"  → {a['title']}")
        print(f"    {a['url']}\n")