from motor.motor_asyncio import AsyncIOMotorClient
from difflib import SequenceMatcher
import os
from dotenv import load_dotenv
from nlp.embeddings import get_embedding

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["crimescope"]
incidents = db["incidents"]


def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


async def insert_incident(article):
    title = article["title"]

    existing = await incidents.find_one({"title": title})
    if existing:
        return False, "exact_duplicate"

    location = article.get("location_name")
    crime_type = article.get("crime_type")

    if location and crime_type:
        candidates = await incidents.find({
            "location_name": location,
            "crime_type": crime_type
        }).to_list(50)

        for c in candidates:
            sim = similarity(title, c["title"])
            if sim > 0.7:
                await incidents.update_one(
                    {"_id": c["_id"]},
                    {
                        "$addToSet": {"confirmed_by": article.get("source")},
                        "$inc": {"source_count": 1}
                    }
                )
                return False, "merged"

    article["embedding"] = get_embedding(article["title"])
    article["confirmed_by"] = [article.get("source")]
    article["source_count"] = 1
    await incidents.insert_one(article)
    return True, "inserted"


async def get_all_incidents():
    cursor = incidents.find({}, {"embedding": 0})
    return await cursor.to_list(length=500)


async def get_by_city(city):
    cursor = incidents.find(
        {"location_name": {"$regex": city, "$options": "i"}},
        {"embedding": 0}
    )
    return await cursor.to_list(length=500)


async def get_stats():
    pipeline = [
        {"$group": {"_id": "$crime_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    cursor = incidents.aggregate(pipeline)
    return await cursor.to_list(length=100)