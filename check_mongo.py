import asyncio
from database.mongo import get_all_incidents

async def check():
    data = await get_all_incidents()
    print(f"Total incidents in DB: {len(data)}")
    for d in data[:3]:
        print(f"  → {d['title']} | {d['crime_type']} | {d['location_name']} | lat:{d['lat']}")

asyncio.run(check())