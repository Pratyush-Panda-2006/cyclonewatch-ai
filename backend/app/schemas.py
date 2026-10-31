from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class GemmaTriageSchema(BaseModel):
    hazard_type: str = Field(description="Categorical hazard, e.g. Downed 33kV Line, Road Inundation, Fallen Tree Blockage, Structural Wall Collapse")
    severity: SeverityLevel = Field(description="Operational risk rating")
    affected_infrastructure: List[str] = Field(description="List of sectors affected, e.g. Electrical Grid, Transport, Drainage, Residential")
    hazard_summary: str = Field(description="2-3 precise sentences detailing visible hazards and threats")
    recommended_response: str = Field(description="Tactical Standard Operating Procedure for dispatch teams")
    required_personnel: List[str] = Field(description="Designated rescue units: e.g. TPCODL Line Crew, ODRAF, BMC Drainage, Fire & Emergency")


class IncidentRecord(BaseModel):
    id: str
    latitude: float
    longitude: float
    location_name: str
    hazard_type: str
    severity: SeverityLevel
    affected_infrastructure: List[str]
    hazard_summary: str
    recommended_response: str
    required_personnel: List[str]
    timestamp: str
    image_filename: Optional[str] = None
    is_gps_fallback: bool = False


class IncidentCreateManual(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    hazard_type: str
    severity: SeverityLevel
    affected_infrastructure: List[str]
    hazard_summary: str
    recommended_response: str
    required_personnel: List[str]


class GeoJsonGeometry(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]


class GeoJsonFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJsonGeometry
    properties: Dict[str, Any]


class GeoJsonFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJsonFeature]


class TriageStats(BaseModel):
    total_incidents: int
    severity_breakdown: Dict[str, int]
    hazard_types: Dict[str, int]
    top_personnel_units: Dict[str, int]
    top_infrastructure_affected: Dict[str, int]
