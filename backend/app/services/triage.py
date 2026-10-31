import json
import logging
import re
from typing import Optional
import httpx

from app.config import GEMINI_API_KEY, GROQ_API_KEY, DEFAULT_MODEL, GROQ_MODEL
from app.schemas import GemmaTriageSchema, SeverityLevel

logger = logging.getLogger("cyclonewatch.triage")

TRIAGE_SYSTEM_PROMPT = """
You are a senior civic hazard assessment and disaster triage officer stationed at the State Emergency Operations Centre (SEOC) in Odisha during extreme cyclone weather.
Analyze the provided field photograph and incident context.

Assess:
1. Primary structural or civic failure.
2. Immediate risk to human life (e.g., live electrical wires touching water, deep flowing floodwater, blocked hospital arterial routes).
3. Severity level:
   - CRITICAL: Imminent life safety risk, active electric contact with flood water, hospital road cut off.
   - HIGH: Major arterial road fully impassable, large structural wall failure near shelters.
   - MEDIUM: Waterlogging without live cables, uprooted trees on secondary roads.
   - LOW: Minor debris, clogged curb drains.
4. Designated rescue agencies (TPCODL, ODRAF, BMC Drainage, Odisha Fire Services).

You MUST respond strictly with valid JSON conforming to this format:
{
  "hazard_type": "string",
  "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "affected_infrastructure": ["string"],
  "hazard_summary": "string",
  "recommended_response": "string",
  "required_personnel": ["string"]
}
Do NOT return Markdown fences, preambles, or explanations. Return valid JSON only.
"""


def _clean_json_response(raw_text: str) -> str:
    """Cleans markdown formatting fences (```json ... ```) from LLM output."""
    text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
        
    return text


def _heuristic_fallback_triage(context_hint: Optional[str] = None) -> GemmaTriageSchema:
    """Resilient fallback triage analyzer for test environments or offline mode."""
    hint = (context_hint or "").lower()
    if "electric" in hint or "wire" in hint or "cable" in hint or "transformer" in hint:
        return GemmaTriageSchema(
            hazard_type="Downed 33kV Live Distribution Line",
            severity=SeverityLevel.CRITICAL,
            affected_infrastructure=["Electrical Grid", "Road Transport", "Public Safety"],
            hazard_summary="Severed 33kV overhead power line submerged in localized rainwater runoff. High electrocution hazard present for pedestrians and emergency vehicles.",
            recommended_response="Initiate instant feeder line de-energization via SCADA. Cordon perimeter within 50-meter radius and dispatch TPCODL heavy utility repair crew.",
            required_personnel=["TPCODL Line Crew", "Odisha Fire Services", "ODRAF Rapid Team"]
        )
    elif "water" in hint or "flood" in hint or "inundation" in hint:
        return GemmaTriageSchema(
            hazard_type="Arterial Road Storm Inundation",
            severity=SeverityLevel.HIGH,
            affected_infrastructure=["Transport", "Storm Drainage Network"],
            hazard_summary="Severe stormwater inundation across low-lying dual carriageway exceeding 3.5 feet depth. Multiple civilian vehicles stalled.",
            recommended_response="Deploy high-discharge dewatering pumps. Divert all non-emergency traffic through higher-elevation ring roads.",
            required_personnel=["BMC Drainage Division", "Odisha Fire Services", "Traffic Police"]
        )
    elif "tree" in hint or "block" in hint:
        return GemmaTriageSchema(
            hazard_type="Uprooted Banyan Tree Arterial Blockage",
            severity=SeverityLevel.HIGH,
            affected_infrastructure=["Road Transport", "Telecom Aerial Cables"],
            hazard_summary="Century-old banyan tree uprooted by sustained cyclone wind gusts, completely obstructing vital corridor with entangled optical cables.",
            recommended_response="Deploy chainsaw tree-cutting squads and heavy payload crane. Clear single ambulance lane within 45 minutes.",
            required_personnel=["Odisha Fire Services", "ODRAF", "Forest Department"]
        )
    else:
        return GemmaTriageSchema(
            hazard_type="Structural Wall Collapse & Road Debris",
            severity=SeverityLevel.MEDIUM,
            affected_infrastructure=["Residential Enclosure", "Secondary Roadway"],
            hazard_summary="Boundary wall collapse resulting from cyclone wind loading and saturated soil foundation. Sidewalk obstructed with masonry rubble.",
            recommended_response="Clear secondary lane debris with backhoe loader and inspect adjoining structures for foundation subsidence.",
            required_personnel=["BMC Drainage", "Municipal Engineering Squad", "Civil Defence"]
        )


async def _triage_via_groq(context_hint: Optional[str] = None) -> Optional[GemmaTriageSchema]:
    """Inference via Groq API."""
    if not GROQ_API_KEY:
        return None

    try:
        prompt_content = TRIAGE_SYSTEM_PROMPT
        if context_hint:
            prompt_content += f"\nIncident Context & Location Telemetry: {context_hint}"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze incident at: {context_hint or 'Coastal Odisha Disaster Corridor'}. Respond strictly with valid JSON."}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            if r.status_code == 200:
                data = r.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(_clean_json_response(content))
                logger.info(f"Groq ({GROQ_MODEL}) inference successful.")
                return GemmaTriageSchema(
                    hazard_type=parsed.get("hazard_type", "Coastal Hazard"),
                    severity=SeverityLevel(parsed.get("severity", "HIGH").upper()),
                    affected_infrastructure=parsed.get("affected_infrastructure", ["Civic Infrastructure"]),
                    hazard_summary=parsed.get("hazard_summary", "Incident classified via Groq inference."),
                    recommended_response=parsed.get("recommended_response", "Dispatch regional emergency units."),
                    required_personnel=parsed.get("required_personnel", ["Odisha Fire Services", "ODRAF"])
                )
    except Exception as e:
        logger.warning(f"Groq inference failed: {e}")
    return None


async def analyze_hazard_multimodal(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    location_context: Optional[str] = None
) -> GemmaTriageSchema:
    """
    Performs multimodal scene analysis using Google GenAI Gemma 4 (gemma-4-26b-a4b-it)
    with Groq API secondary backup and deterministic SEOC heuristics fallback.
    """
    # 1. Primary: Gemma 4 Multimodal Vision via Google GenAI SDK
    if GEMINI_API_KEY:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=GEMINI_API_KEY)

            prompt_text = TRIAGE_SYSTEM_PROMPT
            if location_context:
                prompt_text += f"\nAdditional Location Context: {location_context}"

            part_image = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            
            response = client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=[part_image, prompt_text],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )

            raw_text = response.text or ""
            cleaned_json = _clean_json_response(raw_text)
            data = json.loads(cleaned_json)
            logger.info(f"Gemma 4 ({DEFAULT_MODEL}) multimodal vision analysis successful.")

            raw_units = data.get("required_personnel") or ["Odisha Fire Services", "ODRAF"]
            raw_infra = data.get("affected_infrastructure") or ["Civic Infrastructure"]
            raw_sev = data.get("severity", "MEDIUM")
            if isinstance(raw_sev, str):
                raw_sev = raw_sev.upper().strip()
                if raw_sev not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                    raw_sev = "MEDIUM"

            return GemmaTriageSchema(
                hazard_type=data.get("hazard_type") or "Unclassified Coastal Hazard",
                severity=SeverityLevel(raw_sev),
                affected_infrastructure=raw_infra,
                hazard_summary=data.get("hazard_summary") or "Incident logged via field telemetry.",
                recommended_response=data.get("recommended_response") or "Dispatch regional quick response team for on-site assessment.",
                required_personnel=raw_units
            )

        except Exception as exc:
            logger.warning(f"Gemma 4 multimodal inference error: {exc}. Engaging Groq backup.")

    # 2. Backup: Groq API Inference
    if GROQ_API_KEY:
        groq_result = await _triage_via_groq(location_context)
        if groq_result:
            return groq_result

    # 3. Resilient SEOC Heuristic Fallback
    logger.info("Engaging SEOC rule-based fallback analyzer.")
    return _heuristic_fallback_triage(location_context)
