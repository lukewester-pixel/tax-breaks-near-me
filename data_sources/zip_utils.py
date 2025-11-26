from typing import Optional, Tuple

# Minimal ZIP → (city, state) mapping to start.
# You can expand this over time or swap it for a more complete dataset.
ZIP_CITY_STATE = {
    "92008": ("Carlsbad", "CA"),
    "90210": ("Beverly Hills", "CA"),
    # Add more known ZIPs here as needed
}


def lookup_city_state_locally(zip_code: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Check our local ZIP -> (city, state) mapping.
    Returns (city, state) or (None, None) if we don't know this ZIP.
    """
    return ZIP_CITY_STATE.get(zip_code, (None, None))
