from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

geolocator = Nominatim(user_agent="crimescope-pk")
_cache = {}

# City centers as fallback
CITY_CENTERS = {
    "karachi": (24.8607, 67.0011),
    "lahore": (31.5204, 74.3587),
    "islamabad": (33.6844, 73.0479),
    "rawalpindi": (33.5973, 73.0479),
    "peshawar": (34.0151, 71.5249),
    "quetta": (30.1798, 66.9750),
    "multan": (30.1575, 71.5249),
    "faisalabad": (31.4154, 73.0496),
    "hyderabad": (25.3960, 68.3578),
    "sialkot": (32.4945, 74.5229),
    "sargodha": (32.0836, 72.6711),
    "bahawalpur": (29.3956, 71.6836),
    "gujranwala": (32.1877, 74.1945),
    "abbottabad": (34.1463, 73.2117),
    "mardan": (34.1980, 72.0404),
    "sukkur": (27.7052, 68.8574),
    "larkana": (27.5570, 68.2247),
    "dera ghazi khan": (30.0489, 70.6399),
    "gujrat": (32.5736, 74.0789),
    "kasur": (31.1167, 74.4500),
    "sahiwal": (30.6682, 73.1167),
    "okara": (30.8138, 73.4534),
    "jhang": (31.2681, 72.3181),
    "sheikhupura": (31.7167, 73.9850),
    "nawabshah": (26.2442, 68.4100),
    "mirpur": (33.1450, 73.7508),
    "muzaffarabad": (34.3700, 73.4710),
    "gilgit": (35.9208, 74.3087),
    "dera ismail khan": (31.8314, 70.9019),
    "kohat": (33.5869, 71.4414),
    "bannu": (32.9889, 70.6054),
    "swat": (34.7731, 72.3600),
    "turbat": (25.9911, 63.0442),
    "gwadar": (25.1264, 62.3225),
    "jacobabad": (28.2769, 68.4514),
    "khuzdar": (27.8120, 66.6169),
    "chaman": (30.9200, 66.4500),
    "zhob": (31.3417, 69.4486),
    "mingora": (34.7731, 72.3600),
    "rahim yar khan": (28.4212, 70.2957),
}

def geocode_with_fallback(location_text, source_city=None):
    """
    Try multiple geocoding strategies, return (lat, lng, confidence)
    """
    if not location_text:
        # Level 3: city only fallback
        if source_city and source_city.lower() in CITY_CENTERS:
            lat, lng = CITY_CENTERS[source_city.lower()]
            return lat, lng, "low"
        return None, None, "unknown"

    cache_key = f"{location_text}|{source_city}"
    if cache_key in _cache:
        return _cache[cache_key]

    # Level 1 & 2: try exact location + city context
    queries = []
    if source_city:
        queries.append((f"{location_text}, {source_city}, Pakistan", "medium"))
    queries.append((f"{location_text}, Pakistan", "medium"))

    for query, confidence in queries:
        try:
            time.sleep(1)
            result = geolocator.geocode(query)
            if result:
                lat, lng = result.latitude, result.longitude
                if 23.5 <= lat <= 37.5 and 60.5 <= lng <= 77.5:
                    # Upgrade confidence if very specific result
                    if len(location_text.split()) >= 3:
                        confidence = "high"
                    _cache[cache_key] = (lat, lng, confidence)
                    return lat, lng, confidence
        except GeocoderTimedOut:
            continue

    # Level 3: fall back to city center
    city_key = (source_city or location_text or "").lower()
    if city_key in CITY_CENTERS:
        lat, lng = CITY_CENTERS[city_key]
        _cache[cache_key] = (lat, lng, "low")
        return lat, lng, "low"

    # Level 4: keep record, don't plot
    _cache[cache_key] = (None, None, "unknown")
    return None, None, "unknown"


def enrich_with_coords(article):
    location_text = article.get("location_name")
    source_city = article.get("source_city")

    lat, lng, confidence = geocode_with_fallback(location_text, source_city)

    return {
        **article,
        "lat": lat,
        "lng": lng,
        "location_confidence": confidence
    }