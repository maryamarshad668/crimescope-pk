import asyncio
from database.mongo import incidents

async def clear():
    result = await incidents.delete_many({})
    print(f"Deleted {result.deleted_count} documents")

asyncio.run(clear())