from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class SignalCreate(BaseModel):
    signal_id: str
    source_type: str
    raw_content: str
    normalized_value: float
    normalized_unit: str
    location_lat: float
    location_lng: float
    location_name: str
    severity_hint: str
    confidence: float

class EmergencyReportCreate(BaseModel):
    user_id: str
    location_lat: float
    location_lng: float
    description: Optional[str] = None
    medium: Optional[str] = "internet"

class IncidentCreate(BaseModel):
    disaster_type: str
    location_name: str
    location_lat: float
    location_lng: float
    severity: str
    population_affected: int
    status: Optional[str] = "active"

class IncidentResponse(BaseModel):
    id: int
    disaster_type: str
    location_name: str
    severity: str
    status: str
    
    class Config:
        from_attributes = True

