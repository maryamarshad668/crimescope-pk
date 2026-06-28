import sys
sys.path.insert(0, ".")

from nlp.extractor import extract_info

test = {"title": "Two men killed in firing incident in Karachi", "source": "dawn", "scraped_at": "..."}
print(extract_info(test))

test2 = {"title": "Police arrest robbery suspect in Lahore", "source": "geo", "scraped_at": "..."}
print(extract_info(test2))

from nlp.geocoder import enrich_with_coords

result = extract_info(test)
result = enrich_with_coords(result)
print(result)
# Should show lat/lng for Karachi