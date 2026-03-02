from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from .database import Base

class Signal(Base):
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(String, unique=True, index=True)
    source_type = Column(String)  # weather / earthquake / airquality / flood
    raw_content = Column(Text)
    normalized_value = Column(Float)
    normalized_unit = Column(String)  # mm / kph / magnitude / AQI
    location_lat = Column(Float)
    location_lng = Column(Float)
    location_name = Column(String)
    severity_hint = Column(String)    # low / moderate / high / critical
    confidence = Column(Float)
    is_verified = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class RiskScore(Base):
    __tablename__ = "risk_scores"
    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, index=True)
    predicted_disaster_type = Column(String)
    risk_score = Column(Integer) # 0 to 100
    severity_level = Column(String) # Low / Moderate / High / Critical
    predicted_time_window = Column(String)
    top_factors = Column(Text) # JSON or comma separated
    explanation_simple = Column(Text)
    explanation_detailed = Column(Text)
    explanation_technical = Column(Text)
    recommended_actions = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    disaster_type = Column(String)
    location_name = Column(String)
    location_lat = Column(Float)
    location_lng = Column(Float)
    severity = Column(String)
    status = Column(String, default="active") # active / closed
    population_affected = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String) # medical / fire / police / rescue
    status = Column(String, default="available") # available / deployed
    current_lat = Column(Float)
    current_lng = Column(Float)
    assigned_incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)

class EmergencyReport(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String) 
    location_lat = Column(Float)
    location_lng = Column(Float)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_verified = Column(Boolean, default=False)
    legitimacy_verdict = Column(String, nullable=True) # confirmed / probable / uncertain / likely false

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    user_id = Column(String)
    details = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    previous_hash = Column(String, nullable=True)
    hash = Column(String, nullable=True)
