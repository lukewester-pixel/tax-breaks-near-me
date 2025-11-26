import os
from typing import Optional, Tuple

import requests

# Read API key from environment
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY")


def get_census_by_zip(zip_code: str) -> dict:
    """
    Fetch Census ACS 5-year data for a ZIP code tabulation area (ZCTA).

    Returns a dict with safe numeric fields or an empty dict {} if:
      - the key is missing
      - the request fails
      - the ZIP has no Census data rows
    """
    if not CENSUS_API_KEY:
        # In production we don't want to crash the whole app because of a missing key.
        print("Warning: CENSUS_API_KEY is not set; returning empty census data.")
        return {}

    url = (
        "https://api.census.gov/data/2022/acs/acs5"
        "?get=NAME,B19013_001E,B01003_001E,B25003_002E,B25003_003E,B17001_002E"
        f"&for=zip%20code%20tabulation%20area:{zip_code}"
        f"&key={CENSUS_API_KEY}"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        # Any HTTP / parse error → just log and return empty
        print(f"Error fetching Census data for {zip_code}: {e}")
        return {}

    # Expect shape:
    # [
    #   ["NAME","B19013_001E","B01003_001E","B25003_002E","B25003_003E","B17001_002E","zip code tabulation area"],
    #   ["ZCTA5 92008","101897","27373","5727","6026","2319","92008"]
    # ]
    if not isinstance(data, list) or len(data) < 2:
        # No data rows for this ZIP (likely non-ZCTA or PO box)
        print(f"No Census rows returned for ZIP {zip_code}")
        return {}

    header = data[0]
    row = data[1]
    row_dict = dict(zip(header, row))

    def to_int(key: str) -> Optional[int]:
        val = row_dict.get(key)
        try:
            return int(val)
        except (TypeError, ValueError):
            return None

    median_income = to_int("B19013_001E")
    population = to_int("B01003_001E")
    owner_units = to_int("B25003_002E")
    renter_units = to_int("B25003_003E")
    below_poverty = to_int("B17001_002E")

    owner_ratio = None  # type: Optional[float]
    poverty_rate = None  # type: Optional[float]

    if owner_units is not None and renter_units is not None:
        total_units = owner_units + renter_units
        if total_units > 0:
            owner_ratio = float(owner_units) / float(total_units)

    if population is not None and below_poverty is not None and population > 0:
        poverty_rate = float(below_poverty) / float(population)

    # NOTE: we don't have median_age in this call; leave as None
    return {
        "zip": zip_code,
        "name": row_dict.get("NAME"),
        "median_household_income": median_income,
        "population": population,
        "median_age": None,
        "owner_units": owner_units,
        "renter_units": renter_units,
        "owner_ratio": owner_ratio,
        "below_poverty": below_poverty,
        "poverty_rate": poverty_rate,
    }


def get_city_state_from_zip(zip_code: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Use the Census geocoder to approximate city/state for a given ZIP.

    Returns (city, state) or (None, None) on failure.
    """
    url = (
        "https://geocoding.geo.census.gov/geocoder/geographies/address"
        f"?street=&city=&state=&zip={zip_code}"
        "&benchmark=Public_AR_Current&format=json"
    )

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Error fetching geocoder data for {zip_code}: {e}")
        return None, None

    try:
        result = data["result"]["addressMatches"]
        if not result:
            print(f"No geocoder matches for ZIP {zip_code}")
            return None, None

        first = result[0]
        comps = first.get("addressComponents", {})
        city = comps.get("city")
        state = comps.get("state")
        return city, state
    except Exception as e:
        print(f"Error parsing geocoder response for {zip_code}: {e}")
        return None, None
