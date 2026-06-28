import asyncio
from database.mongo import incidents

async def check():
    all_docs = await incidents.find({}).to_list(500)
    with_coords = [d for d in all_docs if d.get('lat')]
    no_coords = [d for d in all_docs if not d.get('lat')]
    print(f'Total: {len(all_docs)}')
    print(f'With coords: {len(with_coords)}')
    print(f'No coords: {len(no_coords)}')
    print()
    print('No-coord samples:')
    for d in no_coords[:8]:
        print(f"  loc={d.get('location_name')} | conf={d.get('location_confidence')} | {d['title'][:60]}")

asyncio.run(check())