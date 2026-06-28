from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from database.mongo import get_all_incidents, get_by_city, get_stats
from datetime import datetime, timedelta
import httpx
import os
from dotenv import load_dotenv
from database.mongo import incidents as inc_collection
from collections import defaultdict
from nlp.embeddings import get_embedding, cosine_similarity
from database.mongo import incidents as inc_col

app = FastAPI(title="CrimeScope PK API")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"message": "CrimeScope PK API is running"}

@app.get("/incidents")
async def all_incidents():
    data = await get_all_incidents()
    for d in data:
        d["_id"] = str(d["_id"])
    return {"incidents": data, "count": len(data)}

@app.get("/incidents/range")
async def incidents_by_range(start: str = None, end: str = None):
    from database.mongo import incidents
    query = {}
    if start and end:
        query["scraped_at"] = {"$gte": start, "$lte": end}
    elif start:
        query["scraped_at"] = {"$gte": start}
    
    cursor = incidents.find(query)
    data = await cursor.to_list(length=1000)
    for d in data:
        d["_id"] = str(d["_id"])
    return {"incidents": data, "count": len(data)}

@app.get("/incidents/city/{city}")
async def by_city(city: str):
    data = await get_by_city(city)
    for d in data:
        d["_id"] = str(d["_id"])
    return {"incidents": data, "count": len(data)}

@app.get("/stats")
async def statistics():
    return await get_stats()

@app.get("/dashboard")
async def dashboard():
    data = await get_all_incidents()
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    def parse_date(d):
        # Use published_date if available, fall back to scraped_at
        date_str = d.get("published_date") or d.get("scraped_at", "")
        try:
            return datetime.fromisoformat(date_str[:10])
        except:
            return None

    this_week = [d for d in data if parse_date(d) and parse_date(d) >= week_ago]
    this_month = [d for d in data if parse_date(d) and parse_date(d) >= month_ago]

    city_counts = {}
    for d in data:
        city = d.get("location_name")
        if city:
            city_counts[city] = city_counts.get(city, 0) + 1

    crime_counts = {}
    for d in data:
        c = d.get("crime_type", "other")
        crime_counts[c] = crime_counts.get(c, 0) + 1

    source_counts = {}
    for d in data:
        s = d.get("source", "unknown")
        source_counts[s] = source_counts.get(s, 0) + 1

    top_city = max(city_counts, key=city_counts.get) if city_counts else "N/A"
    top_crime = max(crime_counts, key=crime_counts.get) if crime_counts else "N/A"
    top_source = max(source_counts, key=source_counts.get) if source_counts else "N/A"

    return {
        "total": len(data),
        "this_week": len(this_week),
        "this_month": len(this_month),
        "top_city": top_city,
        "top_crime": top_crime,
        "top_source": top_source,
        "city_counts": sorted(city_counts.items(), key=lambda x: -x[1])[:10],
        "crime_counts": sorted(crime_counts.items(), key=lambda x: -x[1]),
        "source_counts": sorted(source_counts.items(), key=lambda x: -x[1]),
    }

@app.get("/health")
async def health():
    return {"status": "ok"}



load_dotenv()

@app.post("/ai/analyze")
async def ai_analyze(payload: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/free",
                "messages": [
                    {"role": "system", "content": payload.get("system", "")},
                    {"role": "user", "content": payload.get("message", "")}
                ]
            },
            timeout=30.0
        )
        data = response.json()
        
        if "error" in data:
            return {"result": f"Error: {data['error']['message']}"}
        
        text = data["choices"][0]["message"]["content"]
        return {"result": text}
    
@app.get("/trends")
async def trends():
    

    data = await get_all_incidents()

    # Group by week + crime type
    weekly = defaultdict(lambda: defaultdict(int))
    for d in data:
        try:
            dt = datetime.fromisoformat(d.get("scraped_at", "")[:10])
            week = dt.strftime("%Y-W%W")
            crime = d.get("crime_type", "other")
            weekly[week][crime] += 1
        except:
            continue

    # Group by city
    city_crimes = defaultdict(lambda: defaultdict(int))
    for d in data:
        city = d.get("location_name")
        crime = d.get("crime_type", "other")
        if city:
            city_crimes[city][crime] += 1

    # Anomaly detection — compare last week vs 8-week average
    sorted_weeks = sorted(weekly.keys())
    alerts = []

    all_crimes = set(c for w in weekly.values() for c in w)
    for crime in all_crimes:
        week_counts = [weekly[w].get(crime, 0) for w in sorted_weeks]
        if len(week_counts) < 2:
            continue
        current = week_counts[-1]
        history = week_counts[:-1][-8:]
        if not history:
            continue
        avg = sum(history) / len(history)
        if avg > 0 and current > avg * 1.5 and current >= 3:
            pct = int((current - avg) / avg * 100)
            alerts.append({
                "crime": crime,
                "current": current,
                "average": round(avg, 1),
                "increase_pct": pct,
                "message": f"{crime.title()} reports this week ({current}) are {pct}% above the recent average ({round(avg,1)}/week)"
            })

    alerts.sort(key=lambda x: -x["increase_pct"])

    return {
        "weekly": {w: dict(c) for w, c in weekly.items()},
        "city_crimes": {c: dict(cr) for c, cr in list(city_crimes.items())[:10]},
        "alerts": alerts[:5]
    }
@app.get("/source-reliability")
async def source_reliability():
    from database.mongo import incidents as inc_col
    
    pipeline = [
        {"$group": {
            "_id": "$source",
            "total": {"$sum": 1},
            "avg_sources": {"$avg": "$source_count"},
            "multi_confirmed": {"$sum": {"$cond": [{"$gt": ["$source_count", 1]}, 1, 0]}}
        }},
        {"$sort": {"total": -1}}
    ]
    cursor = inc_col.aggregate(pipeline)
    results = await cursor.to_list(20)
    
    scored = []
    for r in results:
        total = r["total"]
        confirmed = r["multi_confirmed"]
        reliability = round((confirmed / total * 40) + min(total / 5, 60), 1)
        scored.append({
            "source": r["_id"],
            "total_articles": total,
            "multi_confirmed": confirmed,
            "avg_sources": round(r["avg_sources"], 2),
            "reliability_score": reliability
        })
    
    return {"sources": scored}
@app.get("/similar")
async def similar_incidents(query: str, limit: int = 5):
   
    
    query_embedding = get_embedding(query)
    all_docs = await inc_col.find(
        {"embedding": {"$exists": True}},
        {"embedding": 1, "title": 1, "crime_type": 1, "location_name": 1, "source": 1}
    ).to_list(500)
    
    scored = []
    for doc in all_docs:
        sim = cosine_similarity(query_embedding, doc["embedding"])
        scored.append({
            "title": doc["title"],
            "crime_type": doc.get("crime_type"),
            "location": doc.get("location_name"),
            "source": doc.get("source"),
            "similarity": round(sim, 3)
        })
    
    scored.sort(key=lambda x: -x["similarity"])
    return {"results": scored[:limit]}
    
@app.get("/explain/alert/{crime_type}")
async def explain_alert(crime_type: str):
    from database.mongo import incidents as inc_col
    from collections import defaultdict

    data = await get_all_incidents()
    
    # Get weekly counts for this crime
    weekly = defaultdict(int)
    crime_incidents = []
    for d in data:
        if d.get("crime_type") != crime_type:
            continue
        try:
            dt = datetime.fromisoformat(d.get("scraped_at", "")[:10])
            week = dt.strftime("%Y-W%W")
            weekly[week] += 1
            crime_incidents.append(d)
        except:
            continue

    sorted_weeks = sorted(weekly.keys())
    if len(sorted_weeks) < 2:
        return {"error": "Not enough data"}

    current = weekly[sorted_weeks[-1]]
    history = [weekly[w] for w in sorted_weeks[:-1]][-8:]
    avg = sum(history) / len(history) if history else 0
    pct = int((current - avg) / avg * 100) if avg > 0 else 0

    # Get supporting articles
    recent = [d for d in crime_incidents if d.get("scraped_at", "")[:7] >= sorted_weeks[-1][:7]]

    return {
        "crime_type": crime_type,
        "current_week": current,
        "historical_average": round(avg, 1),
        "increase_pct": pct,
        "weekly_data": [{"week": w, "count": weekly[w]} for w in sorted_weeks],
        "supporting_articles": [
            {
                "title": d["title"],
                "source": d.get("source"),
                "location": d.get("location_name"),
                "url": d.get("url"),
                "confirmed_by": d.get("confirmed_by", []),
                "source_count": d.get("source_count", 1)
            }
            for d in recent[:10]
        ]
    }

@app.get("/pipeline-stats")
async def pipeline_stats():
    from database.mongo import incidents as inc_col
    
    total = await inc_col.count_documents({})
    with_coords = await inc_col.count_documents({"lat": {"$ne": None}})
    multi_source = await inc_col.count_documents({"source_count": {"$gt": 1}})
    with_weapons = await inc_col.count_documents({"weapons": {"$ne": []}})
    high_conf = await inc_col.count_documents({"location_confidence": "high"})
    medium_conf = await inc_col.count_documents({"location_confidence": "medium"})
    low_conf = await inc_col.count_documents({"location_confidence": "low"})
    
    sources = {}
    async for doc in inc_col.aggregate([
        {"$group": {"_id": "$source", "count": {"$sum": 1}}}
    ]):
        sources[doc["_id"]] = doc["count"]

    return {
        "total_incidents": total,
        "geocoded": with_coords,
        "geocoding_rate": round(with_coords / total * 100, 1) if total else 0,
        "multi_source_confirmed": multi_source,
        "dedup_rate": round(multi_source / total * 100, 1) if total else 0,
        "with_weapons": with_weapons,
        "confidence": {"high": high_conf, "medium": medium_conf, "low": low_conf},
        "by_source": sources
    }