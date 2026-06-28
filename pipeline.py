import asyncio
from scraper.dawn_scraper import scrape_dawn
from scraper.geo_scraper import scrape_geo
from scraper.ary_scraper import scrape_ary
from scraper.dunya_scraper import scrape_dunya
from scraper.tribune_scraper import scrape_tribune
from nlp.extractor import extract_info
from nlp.geocoder import enrich_with_coords
from database.mongo import insert_incident

async def run_pipeline():
    print("Scraping all sources...")
    articles = (
        scrape_dawn() +
        scrape_geo() +
        scrape_ary() +
        scrape_dunya() +
        scrape_tribune()
    )
    print(f"Found {len(articles)} raw articles across all sources")
    print("Extracting + geocoding...")
    saved = 0
    skipped = 0
    merged = 0
    for a in articles:
        info = extract_info(a)
        if info is None:
            print(f"  SKIPPED: {a['title']}")
            skipped += 1
            continue
        info = enrich_with_coords(info)
        result, reason = await insert_incident(info)
        if result:
            saved += 1
        elif reason == "merged":
            merged += 1
        else:
            skipped += 1

    print(f"Done — {saved} new, {merged} merged, {skipped} skipped")

if __name__ == "__main__":
    asyncio.run(run_pipeline())