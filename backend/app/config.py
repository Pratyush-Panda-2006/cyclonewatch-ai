import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE_PATH = DATA_DIR / "incidents.json"

# Load environment variables
load_dotenv(dotenv_path=BASE_DIR / ".env")

# AI inference settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_MODEL = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")

# Coastal Odisha Geo-bounding settings (Bhubaneswar and disaster corridor)
BHUBANESWAR_CENTER_LAT = 20.2961
BHUBANESWAR_CENTER_LON = 85.8245

# Realistic fallback locations across the coastal emergency corridor
ODISHA_GEO_FALLBACKS = [
    {
        "name": "Saheed Nagar, Bhubaneswar, Odisha",
        "latitude": 20.2882,
        "longitude": 85.8456,
        "description": "Commercial & arterial road junction"
    },
    {
        "name": "Patia InfoCity Corridor, Bhubaneswar, Odisha",
        "latitude": 20.3542,
        "longitude": 85.8193,
        "description": "Northern transit and educational corridor"
    },
    {
        "name": "Rasulgarh Square Overpass, Bhubaneswar, Odisha",
        "latitude": 20.3015,
        "longitude": 85.8647,
        "description": "High-density National Highway 16 junction"
    },
    {
        "name": "AIIMS - Khandagiri Connector, Bhubaneswar, Odisha",
        "latitude": 20.2520,
        "longitude": 85.7780,
        "description": "Critical emergency hospital artery"
    },
    {
        "name": "Old Town - Lingaraj Lake Periphery, Bhubaneswar, Odisha",
        "latitude": 20.2390,
        "longitude": 85.8340,
        "description": "Low-lying heritage drainage basin"
    },
    {
        "name": "Cuttack Ring Road Embankment, Mahanadi Basin, Odisha",
        "latitude": 20.4625,
        "longitude": 85.8830,
        "description": "Mahanadi river surge and flood embankment"
    },
    {
        "name": "Puri Coastal Grand Road Sector, Odisha",
        "latitude": 19.8135,
        "longitude": 85.8312,
        "description": "Vulnerable coastal storm-surge zone"
    }
]
