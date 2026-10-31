import io
import hashlib
from typing import Tuple, Optional
from PIL import Image, ExifTags
from app.config import BHUBANESWAR_CENTER_LAT, BHUBANESWAR_CENTER_LON, ODISHA_GEO_FALLBACKS


def _convert_dms_to_decimal(dms, ref: str) -> float:
    """
    Converts (degrees, minutes, seconds) rational/float tuples to decimal degrees.
    """
    try:
        degrees = float(dms[0])
        minutes = float(dms[1])
        seconds = float(dms[2])
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ["S", "W"]:
            decimal = -decimal
        return round(decimal, 6)
    except Exception:
        return 0.0


def extract_gps_metadata(
    image_bytes: bytes,
    fallback_location_hint: Optional[str] = None
) -> Tuple[float, float, str, bool]:
    """
    Extracts GPS coordinates from image EXIF metadata.
    If no EXIF GPS data is present, automatically falls back to geo-bounded
    coordinates within the Bhubaneswar / Coastal Odisha emergency disaster corridor.
    
    Returns:
        (latitude, longitude, location_name, is_fallback)
    """
    lat: Optional[float] = None
    lon: Optional[float] = None
    location_name: Optional[str] = None
    is_fallback = False

    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            exif_data = img.getexif()
            if exif_data:
                gps_ifd = exif_data.get_ifd(0x8825)
                
                # Check for standard GPS tags
                # 1 = GPSLatitudeRef, 2 = GPSLatitude
                # 3 = GPSLongitudeRef, 4 = GPSLongitude
                lat_dms = gps_ifd.get(2)
                lat_ref = gps_ifd.get(1)
                lon_dms = gps_ifd.get(4)
                lon_ref = gps_ifd.get(3)

                if lat_dms and lat_ref and lon_dms and lon_ref:
                    extracted_lat = _convert_dms_to_decimal(lat_dms, lat_ref)
                    extracted_lon = _convert_dms_to_decimal(lon_dms, lon_ref)
                    if extracted_lat != 0.0 and extracted_lon != 0.0:
                        lat = extracted_lat
                        lon = extracted_lon
                        location_name = f"Field GPS Recorded Location ({lat:.4f}°N, {lon:.4f}°E)"
    except Exception:
        # Unable to parse EXIF or invalid image format
        pass

    # If GPS not found in EXIF, use automated geo-bounding fallback in Odisha
    if lat is None or lon is None:
        is_fallback = True
        # If user explicitly supplied a location hint, check if it matches a known fallback
        if fallback_location_hint:
            matched = next(
                (f for f in ODISHA_GEO_FALLBACKS if fallback_location_hint.lower() in f["name"].lower()),
                None
            )
            if matched:
                return matched["latitude"], matched["longitude"], matched["name"], is_fallback

        # Deterministic hashing of image content so same photo consistently maps to same coastal zone
        hash_digest = int(hashlib.sha256(image_bytes).hexdigest(), 16)
        fallback_index = hash_digest % len(ODISHA_GEO_FALLBACKS)
        chosen_fallback = ODISHA_GEO_FALLBACKS[fallback_index]

        # Subtle micro-jitter (+/- 0.003 deg ~ 300m) to simulate exact field street placement
        jitter_lat = ((hash_digest % 100) - 50) * 0.00005
        jitter_lon = (((hash_digest >> 8) % 100) - 50) * 0.00005

        lat = round(chosen_fallback["latitude"] + jitter_lat, 6)
        lon = round(chosen_fallback["longitude"] + jitter_lon, 6)
        location_name = chosen_fallback["name"]

    return lat, lon, location_name, is_fallback
