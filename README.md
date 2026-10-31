# CycloneWatch AI / ReliefSense

Open-source multimodal cyclone damage triage and first-responder dispatch engine using **Gemma 4** (`gemma-4-26b-a4b-it`) vision and real-time geospatial hazard mapping, designed for coastal emergencies in Odisha and the Bay of Bengal corridor.

---

## Repository Overview

- **`backend/`**: FastAPI asynchronous backend featuring:
  - Multimodal scene analysis via Google GenAI SDK and **Gemma 4** (`gemma-4-26b-a4b-it`).
  - GPS EXIF metadata extraction with automated coastal Odisha geo-bounding fallback.
  - In-memory cache synchronized with persistent `data/incidents.json`.
  - GeoJSON FeatureCollection stream for GIS mapping and command center dashboards.
- **`frontend/`**: Long scroll-choreographed operational command landing page and live field ingestion studio built with editorial aesthetics (Anton, Inter, Martian Mono), animated Doppler radar wind canvas, 22-contour isobar wave parallax, interactive card rail, and SEOC incident dossier.

---

## Quickstart

### 1. Backend

```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Frontend & Landing Page:** [http://localhost:8000/](http://localhost:8000/)
- **Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **GeoJSON Endpoint:** [http://localhost:8000/api/incidents/geojson](http://localhost:8000/api/incidents/geojson)
