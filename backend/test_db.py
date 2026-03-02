import asyncio
from app.database import SessionLocal
from app.models import Incident, EmergencyReport
from sqlalchemy.future import select

async def get_data():
    async with SessionLocal() as db:
        res1 = await db.execute(select(Incident))
        incs = res1.scalars().all()
        print("INCIDENTS:", [{"id": i.id, "lat": i.location_lat, "lng": i.location_lng} for i in incs])
        
        res2 = await db.execute(select(EmergencyReport))
        reps = res2.scalars().all()
        print("REPORTS:", [{"id": r.id, "lat": r.location_lat, "lng": r.location_lng} for r in reps])

asyncio.run(get_data())
