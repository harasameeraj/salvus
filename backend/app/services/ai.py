import os
import json
import openai
from pydantic import BaseModel
from typing import List, Dict, Any

# Ensure we don't crash if API key is not present initially
api_key = os.environ.get("GEMINI_API_KEY", "")
client = openai.AsyncOpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/") if api_key else None
# Use a fast and efficient model
MODEL_ID = 'gemini-1.5-flash'

class RiskPredictionSchema(BaseModel):
    predicted_disaster_type: str
    risk_score: int
    severity_level: str
    predicted_time_window: str
    confidence_percentage: float
    top_contributing_factors: List[str]
    explanation_simple: str
    explanation_technical: str
    recommended_immediate_actions: List[str]

class CompoundDisasterSchema(BaseModel):
    compound_risk_exists: bool
    driving_factors_combination: List[str]
    risk_multiplier: float
    response_plan_changes: str

class PredictivePreAlertSchema(BaseModel):
    predicted_time_until_critical: str
    confidence: float
    dangerous_signals: List[str]
    trend_type: str # accelerating / slowing
    instant_alert_level: str # Watch / Warning / Emergency

class ReportLegitimacySchema(BaseModel):
    verdict: str # confirmed / probable / uncertain / likely false
    reasoning: str
    conflicting_reports_discarded: int
    discard_reason: str
    recommended_response_level: str
    sensor_status_expected: bool

class OperationalRecommendationSchema(BaseModel):
    primary_action: str
    supporting_actions: List[str]
    recommended_resources: List[str]
    recommended_route: str
    estimated_time_to_impact: str
    shelter_preparation: str
    secondary_threats: List[str]

class SituationMonitoringSchema(BaseModel):
    risk_level_changed: bool
    new_risk_level: str
    response_adequate: bool
    new_threats_emerged: bool
    resource_reallocation_needed: bool
    secondary_threat_status: str

class ScoreExplanationSchema(BaseModel):
    explanation_simple: str
    explanation_detailed: str
    explanation_technical: str

class SituationSummarySchema(BaseModel):
    technical_operations_report: str
    executive_briefing: str
    public_safety_statement: str

class ScenarioGuidanceSchema(BaseModel):
    scenario_name: str
    risk_description: str
    end_user_action_plan: List[str]
    resources_needed: List[str]

class PostIncidentAnalysisSchema(BaseModel):
    prediction_accuracy: str
    system_improvements: str
    calibration_suggestions: str
    action_report: str


async def _generate(prompt: str, schema: BaseModel) -> Any:
    if not client:
        # Stub response if no API key
        stub_data = {}
        for k, v in schema.model_fields.items():
            if str(v.annotation).startswith("typing.List") or str(v.annotation).startswith("list"):
                stub_data[k] = ["API Key Required"]
            elif v.annotation == bool:
                stub_data[k] = False
            elif v.annotation == int or v.annotation == float:
                stub_data[k] = 0
            else:
                stub_data[k] = "API Key Required"
        return schema(**stub_data)
        
    try:
        response = await client.beta.chat.completions.parse(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": "You are a crisis management AI. Analyze the incoming disaster signals and provide strictly formatted operational intelligence."},
                {"role": "user", "content": prompt}
            ],
            response_format=schema,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"OpenAI Generation Error (Rate Limit/Quota): {e}")
        # Return graceful stub if API is temporarily banned
        stub_data = {}
        for k, v in schema.model_fields.items():
            if str(v.annotation).startswith("typing.List") or str(v.annotation).startswith("list"):
                stub_data[k] = ["AI Rate Limited: Please standby."]
            elif v.annotation == bool:
                stub_data[k] = False
            elif v.annotation == int or v.annotation == float:
                stub_data[k] = 0
            else:
                stub_data[k] = "System Cohort Limit Reached: Regenerating shortly..."
        return schema(**stub_data)

# 1. Risk Prediction and Scoring
async def generate_risk_score(signals: List[dict]) -> RiskPredictionSchema:
    prompt = f"Analyze these disaster signals and predict risk. Signals: {json.dumps(signals)}"
    return await _generate(prompt, RiskPredictionSchema)

# 2. Compound Disaster Detection
async def detect_compound_disaster(active_signals: dict) -> CompoundDisasterSchema:
    prompt = f"Evaluate compound disaster risk from: {json.dumps(active_signals)}"
    return await _generate(prompt, CompoundDisasterSchema)

# 3. Predictive Pre-Alert
async def predict_pre_alert(signal_history: List[dict]) -> PredictivePreAlertSchema:
    prompt = f"Predict critical thresholds from 6hr history: {json.dumps(signal_history)}"
    return await _generate(prompt, PredictivePreAlertSchema)

# 4. Report Legitimacy Assessment
async def assess_report_legitimacy(reports: List[dict], env_data: dict) -> ReportLegitimacySchema:
    prompt = f"Assess crowd report legitimacy. Reports: {json.dumps(reports)} Env Data: {json.dumps(env_data)}"
    return await _generate(prompt, ReportLegitimacySchema)

# 5. Operational Recommendation for Responders
async def generate_operational_recommendation(incident: dict, resources: dict) -> OperationalRecommendationSchema:
    prompt = f"Provide responder operations plan. Incident: {json.dumps(incident)} Resources: {json.dumps(resources)}"
    return await _generate(prompt, OperationalRecommendationSchema)

# 6. Continuous Situation Monitoring
async def monitor_situation(incident: dict, active_signals: List[dict]) -> SituationMonitoringSchema:
    prompt = f"Analyze ongoing incident updates. Incident: {json.dumps(incident)} Signals: {json.dumps(active_signals)}"
    return await _generate(prompt, SituationMonitoringSchema)

# 7. Explainability for Every Score
async def generate_score_explanation(score_data: dict) -> ScoreExplanationSchema:
    prompt = f"Explain this risk score to user, operations, and engineer. Data: {json.dumps(score_data)}"
    return await _generate(prompt, ScoreExplanationSchema)

# 8. Situation Summary Report
async def generate_situation_summary(global_state: dict) -> SituationSummarySchema:
    prompt = f"Generate 3-tier reports for global state: {json.dumps(global_state)}"
    return await _generate(prompt, SituationSummarySchema)

# 9. Offline Scenario Pre-Generation
async def generate_offline_scenarios(region_data: dict) -> List[ScenarioGuidanceSchema]:
    # Hardcoded schema format for list handling
    prompt = f"Generate the top 3 most likely disaster scenarios and offline action guidance for: {json.dumps(region_data)}"
    
    # We create a dummy wrapper to extract the list easily with schema enforcement
    class Wrapper(BaseModel):
        scenarios: List[ScenarioGuidanceSchema]
    
    res = await _generate(prompt, Wrapper)
    return res.scenarios

# 10. Post-Incident Analysis
async def analyze_post_incident(incident_record: dict) -> PostIncidentAnalysisSchema:
    prompt = f"Generate post-action review for completed incident log: {json.dumps(incident_record)}"
    return await _generate(prompt, PostIncidentAnalysisSchema)
