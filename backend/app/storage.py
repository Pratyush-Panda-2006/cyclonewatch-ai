import json
import logging
import asyncio
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timezone

from app.config import DATA_FILE_PATH
from app.schemas import (
    IncidentRecord,
    SeverityLevel,
    GeoJsonFeatureCollection,
    GeoJsonFeature,
    GeoJsonGeometry,
    TriageStats,
)

logger = logging.getLogger("cyclonewatch.storage")


SEED_INCIDENTS: List[Dict[str, Any]] = [
    {
        "id": "inc-bbsr-001",
        "latitude": 20.2882,
        "longitude": 85.8456,
        "location_name": "Saheed Nagar Janpath Crossing, Bhubaneswar",
        "hazard_type": "Downed 33kV Live Distribution Line",
        "severity": "CRITICAL",
        "affected_infrastructure": ["Electrical Grid", "Road Transport", "Commercial Sector"],
        "hazard_summary": "High-voltage 33kV transmission conductor severed and partially submerged in 2 feet of street floodwater. Imminent electrocution hazard on major traffic junction.",
        "recommended_response": "De-energize feeder line 4B via remote SCADA immediately. Establish 60m exclusion perimeter and dispatch emergency line utility squad.",
        "required_personnel": ["TPCODL Line Crew", "Odisha Fire Services", "Traffic Police"],
        "timestamp": "2026-10-31T08:15:00Z",
        "image_filename": "seed_downed_33kv_line.jpg",
        "is_gps_fallback": False
    },
    {
        "id": "inc-bbsr-002",
        "latitude": 20.2520,
        "longitude": 85.7780,
        "location_name": "AIIMS - Khandagiri Hospital Arterial, Bhubaneswar",
        "hazard_type": "Hospital Route Flash Inundation",
        "severity": "CRITICAL",
        "affected_infrastructure": ["Emergency Healthcare Access", "Road Transport"],
        "hazard_summary": "Underpass connecting to AIIMS hospital completely flooded with rapid 4.2-foot water torrent. Multiple ambulances stranded on approach ramp.",
        "recommended_response": "Deploy high-capacity mobile dewatering pump trailers. Mobilize ODRAF Zodiac inflatable boats for patient transit transfer.",
        "required_personnel": ["ODRAF Rapid Rescue", "BMC Drainage Division", "Odisha Fire Services"],
        "timestamp": "2026-10-31T08:42:00Z",
        "image_filename": "seed_hospital_arterial_flood.jpg",
        "is_gps_fallback": False
    },
    {
        "id": "inc-bbsr-003",
        "latitude": 20.3542,
        "longitude": 85.8193,
        "location_name": "Patia InfoCity Main Boulevard, Bhubaneswar",
        "hazard_type": "Fallen Banyan Tree Blockage",
        "severity": "HIGH",
        "affected_infrastructure": ["Transport", "Optical Fiber Telecom"],
        "hazard_summary": "Extensive heritage tree uprooted across dual 3-lane boulevard, severing municipal power poles and fiber telemetry cables.",
        "recommended_response": "Deploy motorized chainsaw teams and 20-ton crane. Clear single westbound emergency lane within 45 minutes.",
        "required_personnel": ["Odisha Fire Services", "BMC Tree Squad", "Forest Division"],
        "timestamp": "2026-10-31T09:10:00Z",
        "image_filename": "seed_uprooted_tree_patia.jpg",
        "is_gps_fallback": False
    },
    {
        "id": "inc-bbsr-004",
        "latitude": 20.3015,
        "longitude": 85.8647,
        "location_name": "Rasulgarh NH16 Service Underpass, Bhubaneswar",
        "hazard_type": "Breached Stormwater Culvert",
        "severity": "MEDIUM",
        "affected_infrastructure": ["Storm Drainage Network", "Service Roadway"],
        "hazard_summary": "Structural masonry failure on primary drainage culvert causing localized 1.5-foot backflow onto national highway service lane.",
        "recommended_response": "Install temporary sandbag revetment along culvert crest. Restrict heavy commercial vehicle movement on affected shoulder.",
        "required_personnel": ["BMC Drainage Division", "NHAI Road Maintenance"],
        "timestamp": "2026-10-31T09:35:00Z",
        "image_filename": "seed_culvert_overflow.jpg",
        "is_gps_fallback": True
    },
    {
        "id": "inc-bbsr-005",
        "latitude": 20.2390,
        "longitude": 85.8340,
        "location_name": "Old Town Bindusagar Lake Embankment, Bhubaneswar",
        "hazard_type": "Structural Wall Collapse & Road Debris",
        "severity": "MEDIUM",
        "affected_infrastructure": ["Heritage Precinct", "Pedestrian Walkways"],
        "hazard_summary": "40-meter perimeter boundary wall collapsed inward due to saturated foundation and wind gusts. Roadway narrowed to single lane.",
        "recommended_response": "Clear masonry rubble with compact skid-steer loader. Inspect adjacent boundary walls for stability hazards.",
        "required_personnel": ["BMC Engineering Squad", "Civil Defence Volunteers"],
        "timestamp": "2026-10-31T10:00:00Z",
        "image_filename": "seed_wall_collapse_oldtown.jpg",
        "is_gps_fallback": True
    },
    {
        "id": "inc-bbsr-006",
        "latitude": 19.8135,
        "longitude": 85.8312,
        "location_name": "Puri Coastal Marine Drive Section, Odisha",
        "hazard_type": "Coastal Storm Surge Sand Inundation",
        "severity": "HIGH",
        "affected_infrastructure": ["Coastal Highway", "Protective Seawall Embankment"],
        "hazard_summary": "Tidal surge wave action has deposited 3 feet of sand and ocean debris across 200m of the coastal highway corridor. Vehicle access severed.",
        "recommended_response": "Barricade coastal stretch from civilian traffic. Deploy front-end loaders and earth-moving equipment once surge tide recedes.",
        "required_personnel": ["Works Department Odisha", "Odisha Police Coastal Unit", "ODRAF"],
        "timestamp": "2026-10-31T10:25:00Z",
        "image_filename": "seed_puri_surge_debris.jpg",
        "is_gps_fallback": False
    }
]


class IncidentStore:
    """
    Thread-safe in-memory incident cache backed by persistent JSON storage.
    Automatically initializes with seed incidents for the Odisha cyclone corridor.
    """

    def __init__(self, file_path: Path = DATA_FILE_PATH):
        self.file_path = file_path
        self._incidents: Dict[str, IncidentRecord] = {}
        self._lock = asyncio.Lock()
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Loads incidents from JSON file or populates seed records if file is empty."""
        try:
            if self.file_path.exists():
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        for item in data:
                            try:
                                record = IncidentRecord(**item)
                                self._incidents[record.id] = record
                            except Exception as ex:
                                logger.warning(f"Skipping malformed incident record: {ex}")
                        logger.info(f"Loaded {len(self._incidents)} incidents from {self.file_path}")
                        return

            # If file doesn't exist or is empty, seed defaults
            self._seed_defaults()
        except Exception as e:
            logger.error(f"Error reading {self.file_path}: {e}. Seeding default incidents.")
            self._seed_defaults()

    def _seed_defaults(self) -> None:
        self._incidents.clear()
        for item in SEED_INCIDENTS:
            record = IncidentRecord(**item)
            self._incidents[record.id] = record
        self._save_to_disk_sync()
        logger.info(f"Seeded {len(self._incidents)} default disaster incidents into {self.file_path}")

    def _save_to_disk_sync(self) -> None:
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            serializable = [rec.model_dump() for rec in self._incidents.values()]
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist incidents to disk: {e}")

    async def add_incident(self, record: IncidentRecord) -> IncidentRecord:
        async with self._lock:
            self._incidents[record.id] = record
            self._save_to_disk_sync()
        return record

    async def get_incident(self, incident_id: str) -> Optional[IncidentRecord]:
        return self._incidents.get(incident_id)

    async def list_incidents(
        self,
        severity: Optional[SeverityLevel] = None,
        hazard_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[IncidentRecord]:
        records = list(self._incidents.values())
        
        # Sort newest first
        records.sort(key=lambda r: r.timestamp, reverse=True)

        if severity:
            records = [r for r in records if r.severity == severity]
        if hazard_type:
            records = [r for r in records if hazard_type.lower() in r.hazard_type.lower()]

        return records[offset : offset + limit]

    async def delete_incident(self, incident_id: str) -> bool:
        async with self._lock:
            if incident_id in self._incidents:
                del self._incidents[incident_id]
                self._save_to_disk_sync()
                return True
            return False

    async def reset_seed_data(self) -> int:
        async with self._lock:
            self._seed_defaults()
            return len(self._incidents)

    async def to_geojson(self, severity: Optional[SeverityLevel] = None) -> GeoJsonFeatureCollection:
        records = await self.list_incidents(severity=severity, limit=500)
        features: List[GeoJsonFeature] = []

        for r in records:
            feature = GeoJsonFeature(
                type="Feature",
                geometry=GeoJsonGeometry(
                    type="Point",
                    coordinates=[r.longitude, r.latitude]
                ),
                properties={
                    "id": r.id,
                    "location_name": r.location_name,
                    "hazard_type": r.hazard_type,
                    "severity": r.severity.value,
                    "affected_infrastructure": r.affected_infrastructure,
                    "hazard_summary": r.hazard_summary,
                    "recommended_response": r.recommended_response,
                    "required_personnel": r.required_personnel,
                    "timestamp": r.timestamp,
                    "is_gps_fallback": r.is_gps_fallback,
                    "image_filename": r.image_filename
                }
            )
            features.append(feature)

        return GeoJsonFeatureCollection(type="FeatureCollection", features=features)

    async def get_stats(self) -> TriageStats:
        records = list(self._incidents.values())
        
        severity_counts: Dict[str, int] = {
            SeverityLevel.CRITICAL.value: 0,
            SeverityLevel.HIGH.value: 0,
            SeverityLevel.MEDIUM.value: 0,
            SeverityLevel.LOW.value: 0,
        }
        hazard_types: Dict[str, int] = {}
        personnel_counts: Dict[str, int] = {}
        infra_counts: Dict[str, int] = {}

        for r in records:
            sev_key = r.severity.value
            severity_counts[sev_key] = severity_counts.get(sev_key, 0) + 1

            hazard_types[r.hazard_type] = hazard_types.get(r.hazard_type, 0) + 1

            for p in r.required_personnel:
                personnel_counts[p] = personnel_counts.get(p, 0) + 1

            for inf in r.affected_infrastructure:
                infra_counts[inf] = infra_counts.get(inf, 0) + 1

        return TriageStats(
            total_incidents=len(records),
            severity_breakdown=severity_counts,
            hazard_types=hazard_types,
            top_personnel_units=dict(sorted(personnel_counts.items(), key=lambda x: x[1], reverse=True)[:6]),
            top_infrastructure_affected=dict(sorted(infra_counts.items(), key=lambda x: x[1], reverse=True)[:6])
        )


# Singleton store instance
store = IncidentStore()
