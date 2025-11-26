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


# ---------------------------------------------------------------------------
# Optional Census geocoder integration
# ---------------------------------------------------------------------------

# We try to import a geocode_zip helper from census.py.
# This is wrapped in a try/except so that zip_utils.py never crashes
# even if census.py doesn't have it yet or something goes wrong.
try:
    from .census import geocode_zip  # type: ignore
except Exception:  # pragma: no cover - purely defensive
    geocode_zip = None  # type: ignore


def get_city_state(zip_code: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Resolve a ZIP code to (city, state_abbrev).

    Lookup order:
    1. Local mapping via lookup_city_state_locally
    2. Census geocoder via census.geocode_zip (if available)
    3. Fallback: (None, None)

    Parameters
    ----------
    zip_code: str
        5-digit ZIP as a string. Extra whitespace is stripped.

    Returns
    -------
    (city, state_abbrev): tuple[Optional[str], Optional[str]]
        - city: e.g. "Los Angeles"
        - state_abbrev: e.g. "CA"
        - If lookup fails, returns (None, None).
    """
    if not zip_code:
        return None, None

    z = zip_code.strip()

    # 1) Local lookup first (keeps your existing behavior)
    city, state = lookup_city_state_locally(z)
    if city or state:
        return city, state

    # 2) Try Census geocoder if available
    if geocode_zip is not None:
        try:
            geo = geocode_zip(z)
        except Exception:
            geo = None

        if isinstance(geo, dict):
            # Expect something like {"city": "Los Angeles", "state": "CA"}
            city_val = geo.get("city")
            state_val = geo.get("state")
            if city_val or state_val:
                return city_val, state_val

    # 3) Nothing found
    return None, None


def get_area_label(zip_code: str) -> str:
    """
    Convenience helper to return a human-friendly area label.

    Examples:
    - ("Los Angeles", "CA") -> "Los Angeles, CA"
    - ("Miami", None)       -> "Miami"
    - (None, None)          -> "Unknown area"

    You can pass this straight into your profile as profile["area_label"].
    """
    city, state = get_city_state(zip_code)

    if city and state:
        return f"{city}, {state}"
    if city:
        return city

    return "Unknown area"
