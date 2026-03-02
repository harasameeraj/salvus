import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .database import engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from .services.fetchers import fetch_all_signals
from .services.ai import generate_risk_score
from .models import Signal, RiskScore

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def poll_and_process():
    logger.info("Starting 60s background polling...")
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
    
    async with SessionLocal() as db:
        try:
            # 1. Fetch Signals
            signals = await fetch_all_signals()
            if not signals:
                logger.warning("No signals fetched")
                return
            
            # Save to DB
            for s in signals:
                db_signal = Signal(**s.model_dump())
                db.add(db_signal)
            await db.commit()

            # 2. Convert mapped signals back to dicts to pass to Gemini
            signal_dicts = [s.model_dump() for s in signals]
            
            # 3. Call Gemini API (Call 1)
            prediction = await generate_risk_score(signal_dicts)
            
            # 4. Save Score to DB
            score_entry = RiskScore(
                location_name="Monitored Zone",
                predicted_disaster_type=prediction.predicted_disaster_type,
                risk_score=prediction.risk_score,
                severity_level=prediction.severity_level,
                predicted_time_window=prediction.predicted_time_window,
                top_factors=str(prediction.top_contributing_factors),
                explanation_simple=prediction.explanation_simple,
                explanation_detailed=prediction.explanation_technical,
                explanation_technical=prediction.explanation_technical,
                recommended_actions=str(prediction.recommended_immediate_actions)
            )
            db.add(score_entry)
            await db.commit()
            logger.info(f"Generated Risk Score: {prediction.risk_score} - {prediction.severity_level}")

        except Exception as e:
            logger.error(f"Error in polling loop: {e}")

def start_scheduler():
    scheduler.add_job(poll_and_process, 'interval', seconds=60)
    scheduler.start()
    logger.info("Scheduler started.")
