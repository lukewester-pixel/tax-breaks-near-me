from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")  # optional for now

missing = []
if not CENSUS_API_KEY:
    missing.append("CENSUS_API_KEY")

# We are not requiring GOOGLE_PLACES_API_KEY yet
if missing:
    raise ValueError(f"Missing environment variables: {', '.join(missing)}")
