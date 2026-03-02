import os
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load env variables BEFORE any local module imports
load_dotenv()

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import engine, Base, get_db
from .scheduler import start_scheduler, scheduler
from .schemas import EmergencyReportCreate, IncidentCreate
from .services.communication import comm_service
from .models import Signal, Incident, RiskScore, EmergencyReport

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    start_scheduler()
    yield
    scheduler.shutdown()
    await engine.dispose()

app = FastAPI(title="CrisisSync AI Backend", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CrisisSync AI Backend Active"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/signals")
async def get_signals(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Signal).order_by(Signal.timestamp.desc()).limit(limit))
    return result.scalars().all()

@app.get("/api/incidents")
async def get_incidents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.status == "active").order_by(Incident.created_at.desc()))
    return result.scalars().all()

from .services.ai import generate_situation_summary, generate_operational_recommendation

@app.get("/api/scores")
async def get_scores(limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RiskScore).order_by(RiskScore.timestamp.desc()).limit(limit))
    return result.scalars().all()

@app.get("/api/dashboard-state")
async def get_dashboard_state(db: AsyncSession = Depends(get_db)):
    # 1. Gather global state (active incidents + latest score)
    result_incidents = await db.execute(select(Incident).where(Incident.status == "active"))
    incidents = result_incidents.scalars().all()
    
    result_scores = await db.execute(select(RiskScore).order_by(RiskScore.timestamp.desc()).limit(1))
    latest_score = result_scores.scalar_one_or_none()
    
    global_state = {
        "active_incidents_count": len(incidents),
        "incidents": [{"type": i.disaster_type, "severity": i.severity, "location": i.location_name} for i in incidents],
        "latest_risk": latest_score.risk_score if latest_score else 0
    }
    
    # Generate dynamic situation summary using Gemini
    summary = await generate_situation_summary(global_state)
    
    return {
        "executive_briefing": summary.executive_briefing,
        "technical_operations_report": summary.technical_operations_report
    }

@app.get("/api/incidents/{incident_id}/recommendation")
async def get_incident_recommendation(incident_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Incident).where(Incident.id == incident_id))
    incident = result.scalar_one_or_none()
    if not incident:
        return {"error": "Incident not found"}
        
    incident_data = {
        "type": incident.disaster_type,
        "location": incident.location_name,
        "severity": incident.severity,
        "population_affected": incident.population_affected
    }
    
    # Provide operational recommendation using Gemini
    recommendation = await generate_operational_recommendation(incident_data, {"available_units": 5})
    
    return recommendation.model_dump()

@app.post("/api/reports")
async def submit_report(report: EmergencyReportCreate, db: AsyncSession = Depends(get_db)):
    new_rep = EmergencyReport(**report.model_dump())
    db.add(new_rep)
    await db.commit()
    await db.refresh(new_rep)
    
    # SOS LOGIC: alert ONLY the first responder immediately
    sos_msg = f"URGENT SOS SIGNAL: A citizen needs help at [{new_rep.location_lat}, {new_rep.location_lng}]. Report: {new_rep.description}. Deploy to coordinates now."
    
    await comm_service.send_whatsapp_alert("responder", f"🚨 {sos_msg}")
    await comm_service.send_sms_alert("responder", sos_msg)
    await comm_service.place_voice_call("responder", f"Emergency Dispatch alert. A survival signal has been triggered by a help seeker. Location is synced to your dashboard. Description is as follows. {new_rep.description}. Respond immediately.")
    
    return {"status": "success", "report_id": new_rep.id}

@app.get("/api/reports")
async def get_reports(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmergencyReport).order_by(EmergencyReport.timestamp.desc()).limit(limit))
    return result.scalars().all()

async def sse_generator():
    while True:
        # Simplified SSE heartbeat. Real system connects to Redis pubsub or DB listener.
        yield {
            "event": "update",
            "data": "refresh"
        }
        await asyncio.sleep(5)

@app.get("/api/stream")
async def sse_stream(request: Request):
    return EventSourceResponse(sse_generator())

@app.post("/api/incidents")
async def create_incident(incident: IncidentCreate, db: AsyncSession = Depends(get_db)):
    db_incident = Incident(**incident.model_dump())
    db.add(db_incident)
    await db.commit()
    await db.refresh(db_incident)
    
    # PREVENTIVE ALERT LOGIC: Different tones for different personas
    if db_incident.severity.lower() in ["high", "critical"]:
        # Responder Tone: Operational/Action
        resp_msg = f"STRATEGIC UPDATE: A {db_incident.disaster_type} is developing in {db_incident.location_name}. Analyze risk heatmap and be ready for deployment."
        await comm_service.send_whatsapp_alert("responder", f"🛠 {resp_msg}")
        await comm_service.send_sms_alert("responder", resp_msg)
        
        # End User Tone: Safety/Evacuation
        user_msg = f"SAFETY ALERT: A {db_incident.disaster_type} is active in {db_incident.location_name}. Please move to safe high ground and follow local authority guidance. Stay safe."
        await comm_service.send_whatsapp_alert("reporter", f"🛡 {user_msg}")
        await comm_service.send_sms_alert("reporter", user_msg)
        
    if db_incident.severity.lower() == "critical":
        # Voice Tone: Action-oriented for Responders
        resp_voice = f"Operational alert. A critical {db_incident.disaster_type} has been detected in {db_incident.location_name}. Your dashboard is primed with risk analytics. Be ready to help and take action immediately."
        await comm_service.place_voice_call("responder", resp_voice)

        # Voice Tone: Safety/Emergency for Victims
        vict_voice = f"Life safety warning from CrisisSync AI. A {db_incident.disaster_type} is active in your immediate area. This is a critical alert. Be safe and evacuate to a secure location now. Help is being mobilized."
        await comm_service.place_voice_call("reporter", vict_voice)

    return db_incident
