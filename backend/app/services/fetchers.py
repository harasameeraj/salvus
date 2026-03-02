import httpx
import logging
from typing import List
from datetime import datetime
from ..schemas import SignalCreate

logger = logging.getLogger(__name__)

DEFAULT_LAT = 37.7749
DEFAULT_LNG = -122.4194

async def fetch_open_meteo(lat: float = DEFAULT_LAT, lng: float = DEFAULT_LNG) -> List[SignalCreate]:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"
    signals = []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                
                precip = current.get("precipitation", 0.0)
                wind = current.get("wind_speed_10m", 0.0)
                
                severity = "low"
                if precip > 20 or wind > 50: severity = "moderate"
                if precip > 50 or wind > 80: severity = "high"
                if precip > 100 or wind > 120: severity = "critical"

                signals.append(SignalCreate(
                    signal_id=f"meteo-{lat}-{lng}-{datetime.now().timestamp()}",
                    source_type="weather",
                    raw_content=str(data),
                    normalized_value=float(precip),
                    normalized_unit="mm",
                    location_lat=lat,
                    location_lng=lng,
                    location_name="Monitored Zone",
                    severity_hint=severity,
                    confidence=0.9
                ))
    except Exception as e:
        logger.error(f"Error fetching Open-Meteo: {e}")
    return signals

async def fetch_usgs_earthquake() -> List[SignalCreate]:
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
    signals = []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                features = data.get("features", [])
                for f in features:
                    props = f.get("properties", {})
                    geom = f.get("geometry", {})
                    coords = geom.get("coordinates", [0, 0])
                    mag = props.get("mag", 0.0)
                    
                    if not mag: continue
                        
                    severity = "low"
                    if mag > 5.0: severity = "moderate"
                    if mag > 6.0: severity = "high"
                    if mag > 7.0: severity = "critical"
                        
                    signals.append(SignalCreate(
                        signal_id=f"usgs-eq-{f.get('id', datetime.now().timestamp())}",
                        source_type="earthquake",
                        raw_content=str(f),
                        normalized_value=float(mag),
                        normalized_unit="magnitude",
                        location_lat=coords[1] if len(coords) > 1 else 0.0,
                        location_lng=coords[0] if len(coords) > 0 else 0.0,
                        location_name=props.get("place", "Unknown"),
                        severity_hint=severity,
                        confidence=0.95
                    ))
    except Exception as e:
        logger.error(f"Error fetching USGS: {e}")
    return signals

async def fetch_openaq(lat: float = DEFAULT_LAT, lng: float = DEFAULT_LNG, radius: int = 10000) -> List[SignalCreate]:
    url = f"https://api.openaq.org/v2/latest?coordinates={lat},{lng}&radius={radius}&limit=5"
    signals = []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                for result in results:
                    measurements = result.get("measurements", [])
                    for m in measurements:
                        if m.get("parameter") in ["pm25", "co", "aqi"]:
                            val = m.get("value", 0.0)
                            unit = m.get("unit", "")
                            
                            severity = "low"
                            if val > 100: severity = "moderate"
                            if val > 150: severity = "high"
                            if val > 200: severity = "critical"
                                
                            signals.append(SignalCreate(
                                signal_id=f"openaq-{result.get('location')}-{m.get('parameter')}-{datetime.now().timestamp()}",
                                source_type="airquality",
                                raw_content=str(m),
                                normalized_value=float(val),
                                normalized_unit=unit,
                                location_lat=lat,
                                location_lng=lng,
                                location_name=result.get("location", "Monitored Zone"),
                                severity_hint=severity,
                                confidence=0.85
                            ))
    except Exception as e:
        logger.error(f"Error fetching OpenAQ: {e}")
    return signals

async def fetch_all_signals() -> List[SignalCreate]:
    weather = await fetch_open_meteo()
    eq = await fetch_usgs_earthquake()
    aq = await fetch_openaq()
    return weather + eq + aq
