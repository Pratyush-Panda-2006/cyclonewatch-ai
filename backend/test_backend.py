import io
import asyncio
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.storage import store
from app.services.exif import extract_gps_metadata


def create_dummy_image(with_gps: bool = False) -> bytes:
    """Creates an in-memory sample image for testing."""
    img = Image.new("RGB", (200, 200), color=(30, 80, 160))
    buffer = io.BytesIO()
    
    if with_gps:
        # Construct EXIF with GPS tag (0x8825)
        # Lat: 20 deg 17 min 17.52 sec N (approx 20.2882)
        # Lon: 85 deg 50 min 44.16 sec E (approx 85.8456)
        exif = img.getexif()
        gps_ifd = exif.get_ifd(0x8825)
        gps_ifd[1] = "N"
        gps_ifd[2] = (20.0, 17.0, 17.52)
        gps_ifd[3] = "E"
        gps_ifd[4] = (85.0, 50.0, 44.16)
        img.save(buffer, format="JPEG", exif=exif)
    else:
        img.save(buffer, format="JPEG")

    return buffer.getvalue()


def test_exif_extraction():
    print("Testing EXIF extraction...")
    # Test with GPS
    img_with_gps = create_dummy_image(with_gps=True)
    lat, lon, loc, is_fallback = extract_gps_metadata(img_with_gps)
    assert not is_fallback, "Should have detected real GPS coordinates"
    assert round(lat, 2) == 20.29, f"Expected ~20.29, got {lat}"
    assert round(lon, 2) == 85.85, f"Expected ~85.85, got {lon}"
    print(f"  [PASS] GPS extracted: {lat}, {lon} ({loc})")

    # Test without GPS (fallback to Odisha geo-bounding)
    img_no_gps = create_dummy_image(with_gps=False)
    lat_fb, lon_fb, loc_fb, is_fb = extract_gps_metadata(img_no_gps)
    assert is_fb, "Should have activated fallback"
    assert 19.5 <= lat_fb <= 21.0, f"Latitude {lat_fb} out of Odisha bounds"
    assert 85.0 <= lon_fb <= 86.5, f"Longitude {lon_fb} out of Odisha bounds"
    print(f"  [PASS] Fallback triggered: {lat_fb}, {lon_fb} ({loc_fb})")


def test_api_endpoints():
    print("Testing FastAPI endpoints...")
    client = TestClient(app)

    # 1. Root & Health
    r_frontend = client.get("/")
    assert r_frontend.status_code == 200
    assert "CycloneWatch" in r_frontend.text
    print("  [PASS] GET / serves CycloneWatch AI frontend landing page")

    r_api = client.get("/api")
    assert r_api.status_code == 200
    assert r_api.json()["service"] == "CycloneWatch AI / ReliefSense Backend"
    print("  [PASS] GET /api returns operational metadata")


    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
    print("  [PASS] GET /api/health healthy")

    # 2. List Incidents
    r = client.get("/api/incidents")
    assert r.status_code == 200
    incidents = r.json()
    assert len(incidents) >= 6, "Expected at least 6 seed incidents"
    print(f"  [PASS] GET /api/incidents returned {len(incidents)} records")

    # 3. GeoJSON
    r = client.get("/api/incidents/geojson")
    assert r.status_code == 200
    geojson = r.json()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == len(incidents)
    print(f"  [PASS] GET /api/incidents/geojson returned {len(geojson['features'])} features")

    # 4. Stats
    r = client.get("/api/stats")
    assert r.status_code == 200
    stats = r.json()
    assert stats["total_incidents"] == len(incidents)
    assert "CRITICAL" in stats["severity_breakdown"]
    print("  [PASS] GET /api/stats verified")

    # 5. POST /api/triage with dummy image
    image_bytes = create_dummy_image(with_gps=False)
    files = {"file": ("flood_incident.jpg", image_bytes, "image/jpeg")}
    data = {"location_name": "Patia InfoCity"}
    r = client.post("/api/triage", files=files, data=data)
    assert r.status_code == 201, f"Triage upload failed: {r.text}"
    new_record = r.json()
    assert "id" in new_record
    assert new_record["severity"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    assert len(new_record["required_personnel"]) > 0
    print(f"  [PASS] POST /api/triage created record: {new_record['id']} ({new_record['hazard_type']} - {new_record['severity']})")

    # 6. GET /api/incidents/{id}
    r = client.get(f"/api/incidents/{new_record['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == new_record["id"]
    print(f"  [PASS] GET /api/incidents/{new_record['id']} verified")

    # 7. Manual Incident creation
    manual_data = {
        "hazard_type": "Fallen Telecommunication Mast",
        "severity": "HIGH",
        "affected_infrastructure": ["Telecom", "Power Distribution"],
        "hazard_summary": "100ft radio transmission mast collapsed across residential feeder road.",
        "recommended_response": "Cordon area and clear debris using heavy recovery crane.",
        "required_personnel": ["ODRAF", "Odisha Fire Services"]
    }
    r = client.post("/api/incidents/manual", json=manual_data)
    assert r.status_code == 201
    manual_record = r.json()
    print(f"  [PASS] POST /api/incidents/manual created record: {manual_record['id']}")

    print("\nALL BACKEND TESTS PASSED SUCCESSFULLY! :)")


if __name__ == "__main__":
    test_exif_extraction()
    test_api_endpoints()
