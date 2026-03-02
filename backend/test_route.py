import asyncio
from app.database import SessionLocal
from app.main import get_dashboard_state

async def test():
    async with SessionLocal() as db:
        try:
            res = await get_dashboard_state(db)
            print("SUCCESS:", res)
        except Exception as e:
            import traceback
            traceback.print_exc()

asyncio.run(test())
