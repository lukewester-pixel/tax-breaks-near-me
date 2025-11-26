import requests
from typing import Optional, Tuple
from config import CENSUS_API_KEY


def get_census_by_zip(zip_code: str) -> dict:
    """
    Fetch extended Census ACS data for a ZIP code:
    - NAME
    - Median household income (B19013_001E)
    - Total population (B01003_001E)
    - Median age (B01002_001E)
    - Owner-occupied housing units (B25003_002E)
    - Renter-occupied housing units (B25003_003E)
    - People below poverty level (B17001_002E)
    """
    url = "https://api.census.gov/data/2022/acs/acs5"
    params = {
        "get": ",".join([
            "NAME",
            "B19013_001E",   # median household income
            "B01003_001E",   # total population
            "B01002_001E",   # median age
            "B25003_002E",   # owner-occupied units
            "B25003_003E",   # renter-occupied units
            "B17001_002E"    # below-poverty count
        ]),
        "for": f"zip code tabulation area:{zip_code}",
        "key": CENSUS_API_KEY,
    }

    resp = requests.get(url, params=params)

    if resp.status_code != 200:
        raise Exception(f"Census API error {resp.status_code}: {resp.text}")

    try:
        data = resp.json()
    except Exception as e:
        raise Exception(
            f"Failed to parse Census JSON. Raw response:\n{resp.text}"
        ) from e

    if len(data) < 2:
        raise ValueError(
            f"No Census data returned for ZIP {zip_code}. Raw response: {data}"
        )

    headers = data[0]
    values = data[1]
    row = dict(zip(headers, values))

    # Convert Census strings to integers safely
    def to_int(x):
        try:
            return int(x)
        except Exception:
            return None

    median_income = to_int(row.get("B19013_001E"))
    population = to_int(row.get("B01003_001E"))
    median_age = to_int(row.get("B01002_001E"))
    owner_units = to_int(row.get("B25003_002E"))
    renter_units = to_int(row.get("B25003_003E"))
    below_poverty = to_int(row.get("B17001_002E"))

    # Derived metrics
    total_units = None
    if owner_units is not None and renter_units is not None:
        total_units = owner_units + renter_units

    owner_ratio = None
    if total_units and total_units > 0 and owner_units is not None:
        owner_ratio = owner_units / total_units

    poverty_rate = None
    if population and population > 0 and below_poverty is not None:
        poverty_rate = below_poverty / population

    return {
        "zip": zip_code,
        "name": row.get("NAME"),
        "median_household_income": median_income,
        "population": population,
        "median_age": median_age,
        "owner_units": owner_units,
        "renter_units": renter_units,
        "owner_ratio": owner_ratio,       # float 0–1
        "below_poverty": below_poverty,
        "poverty_rate": poverty_rate,     # float 0–1
    }


def get_city_state_from_zip(zip_code: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Use Census Geocoding API to convert ZIP -> (city, state).

    Returns:
        (city, state) or (None, None) if lookup fails or the API errors.
    """
    url = "https://geocoding.geo.census.gov/geocoder/geographies/address"
    params = {
        "street": "",
        "city": "",
        "state": "",
        "zip": zip_code,
        "benchmark": "Public_AR_Current",
        "format": "json",
    }

    try:
        resp = requests.get(url, params=params)
        # If the API is unhappy (like the 400 you hit), just bail gracefully
        if resp.status_code != 200:
            return None, None

        data = resp.json()
        match = data["result"]["addressMatches"][0]
        zip_geo = match["geographies"]["ZIPCodes"][0]
        city = zip_geo.get("CITY")
        state = zip_geo.get("STATE")
        return city, state
    except Exception:
        # On *any* error (network, JSON, missing keys), fail soft
        return None, None
