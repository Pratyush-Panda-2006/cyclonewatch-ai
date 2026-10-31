# ReliefSense / CycloneWatch AI Backend

An asynchronous, lightweight, open-source multimodal disaster triage and incident response backend engineered for coastal emergencies (specifically tuned for the Odisha / Bay of Bengal cyclone corridor).

---

## Key Features

- **Multimodal AI Disaster Triage:** Powered by **Gemma 4** (`gemma-4-26b-a4b-it`) via the `google-genai` SDK. Categorizes civic failures, calculates life-safety severity ratings (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), identifies affected infrastructure, and determines tactical responder dispatch (TPCODL, ODRAF, BMC Drainage, Odisha Fire Services).
- **Automated EXIF GPS Ingestion & Geo-Bounding:** Extracts high-precision GPS coordinates directly from field photo metadata. If EXIF metadata is stripped or unavailable, automatically falls back to geographically bounded hotspots across Bhubaneswar, Cuttack, and the coastal emergency corridor.
- **Dual Layer GeoJSON & In-Memory Persistence:** Fast in-memory state backed by persistent file storage (`data/incidents.json`), exposing both REST entities and GeoJSON FeatureCollections ready for Leaflet, Mapbox, or Deck.gl visualization.
- **CORS Enabled:** Full wildcard CORS configuration for seamless communication with web, mobile, and command center dashboards.

---

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application factory, CORS, routes
│   ├── config.py        # Environment variables & Odisha geo-bounding constants
│   ├── schemas.py       # Pydantic v2 data models & Enums
│   ├── services/
│   │   ├── __init__.py
│   │   ├── triage.py    # Gemma 4 multimodal inference client
│   │   └── exif.py      # GPS EXIF extractor utility with geo-fallback
│   └── storage.py       # Thread-safe in-memory & file-backed store
├── data/
│   ├── incidents.json   # Seed/persistent incident records
│   └── uploads/         # Uploaded field disaster photographs
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
└── README.md
```

---

## Quickstart

### 1. Requirements

- Python 3.11+
- Virtual environment (recommended)

### 2. Setup Virtual Environment & Install Dependencies

```bash
cd backend
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `.env` in the `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMMA_MODEL=gemma-4-26b-a4b-it
PORT=8000
HOST=0.0.0.0
```

> **Note:** If `GEMINI_API_KEY` is not provided, the backend seamlessly activates its State Emergency Operations Centre (SEOC) rule-based heuristics engine, allowing full offline testing without API access.

### 4. Run Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive OpenAPI Swagger UI is available at:
`http://localhost:8000/docs`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | System status, active model, and incident count |
| `GET` | `/api/health` | Health check probe |
| `POST` | `/api/triage` | Upload field photo, extract GPS EXIF, run Gemma 4 triage, and save incident |
| `GET` | `/api/incidents` | List paginated incidents (filters: `severity`, `hazard_type`) |
| `GET` | `/api/incidents/{id}` | Retrieve incident details |
| `GET` | `/api/incidents/geojson` | GeoJSON FeatureCollection for map layers |
| `GET` | `/api/stats` | SEOC triage analytics & dispatched personnel units |
| `POST` | `/api/incidents/manual` | Log incident directly without image upload |
| `DELETE`| `/api/incidents/{id}` | Delete incident record |
| `POST` | `/api/incidents/seed` | Reset incident database with coastal Odisha seed records |
