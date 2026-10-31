import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.config import DEFAULT_MODEL, GEMINI_API_KEY, DATA_DIR
from app.schemas import (
    IncidentRecord,
    IncidentCreateManual,
    SeverityLevel,
    GeoJsonFeatureCollection,
    TriageStats,
    GemmaTriageSchema,
)
from app.services.exif import extract_gps_metadata
from app.services.triage import analyze_hazard_multimodal
from app.storage import store

# Setup uploads storage directory
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="CycloneWatch AI / ReliefSense Backend",
    description="Multimodal disaster triage and incident response engine for coastal emergencies powered by Gemma 4",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for all local and deployed frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads static folder if exists
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")


FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

@app.get("/api", tags=["System"])
async def root_status():
    """
    Root status and service metadata.
    """
    stats = await store.get_stats()
    return {
        "service": "CycloneWatch AI / ReliefSense Backend",
        "status": "operational",
        "emergency_theatre": "Odisha State Disaster Management Authority / SEOC Corridor",
        "model_target": DEFAULT_MODEL,
        "genai_configured": bool(GEMINI_API_KEY),
        "total_active_incidents": stats.total_incidents,
        "docs_url": "/docs",
        "api_endpoints": {
            "triage_upload": "POST /api/triage",
            "incidents_list": "GET /api/incidents",
            "geojson": "GET /api/incidents/geojson",
            "stats": "GET /api/stats"
        }
    }


@app.get("/api/health", tags=["System"])
async def health_check():
    """
    Health check endpoint for container orchestrators and monitoring probes.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": DEFAULT_MODEL,
        "data_store": "ready"
    }


@app.post(
    "/api/triage",
    response_model=IncidentRecord,
    status_code=status.HTTP_201_CREATED,
    tags=["Triage & Ingestion"],
    summary="Upload citizen/field photograph for EXIF extraction and Gemma 4 multimodal triage"
)
async def triage_incident_upload(
    file: UploadFile = File(..., description="Field disaster photograph (JPEG, PNG, WEBP)"),
    latitude: Optional[float] = Form(None, description="Optional manual GPS latitude override"),
    longitude: Optional[float] = Form(None, description="Optional manual GPS longitude override"),
    location_name: Optional[str] = Form(None, description="Optional landmark or road name hint"),
):
    """
    Accepts field disaster images, extracts GPS EXIF (or applies automated geo-bounding
    fallbacks around Bhubaneswar / coastal Odisha), runs Gemma 4 multimodal scene analysis,
    and returns the validated persisted incident record.
    """
    # 1. Read binary image content
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image file: {str(e)}")

    # 2. Extract or resolve GPS coordinates
    is_gps_fallback = False
    if latitude is not None and longitude is not None:
        rec_lat, rec_lon = round(latitude, 6), round(longitude, 6)
        rec_loc = location_name or f"Manual Coordinates ({rec_lat:.4f}°N, {rec_lon:.4f}°E)"
    else:
        extracted_lat, extracted_lon, extracted_loc, fallback_flag = extract_gps_metadata(
            image_bytes=image_bytes,
            fallback_location_hint=location_name
        )
        rec_lat = extracted_lat
        rec_lon = extracted_lon
        rec_loc = location_name or extracted_loc
        is_gps_fallback = fallback_flag

    # 3. Multimodal scene analysis via Gemma 4
    mime_type = file.content_type or "image/jpeg"
    triage_result: GemmaTriageSchema = await analyze_hazard_multimodal(
        image_bytes=image_bytes,
        mime_type=mime_type,
        location_context=rec_loc
    )

    # 4. Save photo artifact locally
    incident_uuid = f"inc-{uuid.uuid4().hex[:8]}"
    ext = Path(file.filename or "image.jpg").suffix or ".jpg"
    saved_filename = f"{incident_uuid}{ext}"
    try:
        file_save_path = UPLOADS_DIR / saved_filename
        with open(file_save_path, "wb") as f:
            f.write(image_bytes)
    except Exception:
        saved_filename = None

    # 5. Build structured record
    timestamp_str = datetime.now(timezone.utc).isoformat()
    incident_record = IncidentRecord(
        id=incident_uuid,
        latitude=rec_lat,
        longitude=rec_lon,
        location_name=rec_loc,
        hazard_type=triage_result.hazard_type,
        severity=triage_result.severity,
        affected_infrastructure=triage_result.affected_infrastructure,
        hazard_summary=triage_result.hazard_summary,
        recommended_response=triage_result.recommended_response,
        required_personnel=triage_result.required_personnel,
        timestamp=timestamp_str,
        image_filename=saved_filename,
        is_gps_fallback=is_gps_fallback
    )

    # 6. Persist to storage
    await store.add_incident(incident_record)
    return incident_record


@app.get("/api/incidents", response_model=List[IncidentRecord], tags=["Incidents"])
async def list_incidents(
    severity: Optional[SeverityLevel] = Query(None, description="Filter by severity level"),
    hazard_type: Optional[str] = Query(None, description="Filter by partial hazard type match"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Retrieve paginated list of logged disaster incidents.
    """
    return await store.list_incidents(
        severity=severity,
        hazard_type=hazard_type,
        limit=limit,
        offset=offset
    )


@app.get("/api/incidents/geojson", response_model=GeoJsonFeatureCollection, tags=["Incidents"])
async def get_incidents_geojson(
    severity: Optional[SeverityLevel] = Query(None, description="Filter GeoJSON by severity")
):
    """
    Export all incidents in GeoJSON FeatureCollection format for GIS mapping (Mapbox, Leaflet, Deck.gl).
    """
    return await store.to_geojson(severity=severity)


@app.get("/api/incidents/{incident_id}", response_model=IncidentRecord, tags=["Incidents"])
async def get_incident(incident_id: str):
    """
    Retrieve single incident details by unique ID.
    """
    record = await store.get_incident(incident_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return record


@app.post("/api/incidents/manual", response_model=IncidentRecord, status_code=status.HTTP_201_CREATED, tags=["Incidents"])
async def create_manual_incident(incident_data: IncidentCreateManual):
    """
    Manually log an incident directly (e.g. from Emergency Operations Centre telephone dispatches).
    """
    incident_uuid = f"inc-manual-{uuid.uuid4().hex[:8]}"
    lat = incident_data.latitude if incident_data.latitude is not None else 20.2961
    lon = incident_data.longitude if incident_data.longitude is not None else 85.8245
    loc_name = incident_data.location_name or "SEOC Telemetry Dispatch, Bhubaneswar"

    record = IncidentRecord(
        id=incident_uuid,
        latitude=round(lat, 6),
        longitude=round(lon, 6),
        location_name=loc_name,
        hazard_type=incident_data.hazard_type,
        severity=incident_data.severity,
        affected_infrastructure=incident_data.affected_infrastructure,
        hazard_summary=incident_data.hazard_summary,
        recommended_response=incident_data.recommended_response,
        required_personnel=incident_data.required_personnel,
        timestamp=datetime.now(timezone.utc).isoformat(),
        image_filename=None,
        is_gps_fallback=(incident_data.latitude is None or incident_data.longitude is None)
    )
    await store.add_incident(record)
    return record


@app.delete("/api/incidents/{incident_id}", tags=["Incidents"])
async def delete_incident(incident_id: str):
    """
    Delete an incident record.
    """
    deleted = await store.delete_incident(incident_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")
    return {"message": f"Incident '{incident_id}' deleted successfully."}


@app.get("/api/stats", response_model=TriageStats, tags=["SEOC Intelligence"])
async def get_triage_statistics():
    """
    Aggregated operational statistics and resource allocations for SEOC commanders.
    """
    return await store.get_stats()


@app.post("/api/incidents/seed", tags=["System"])
async def reset_seed_data():
    """
    Re-seed the storage with default disaster records from coastal Odisha.
    """
    count = await store.reset_seed_data()
    return {"message": "Incident database reset and populated with seed data.", "count": count}


# Mount frontend static directory if exists for seamless landing page experience
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

