from typing import Dict, List, Optional, Tuple

from data_sources.census import get_census_by_zip
from data_sources.irs_bmf import load_bmf_rows
from data_sources.zip_utils import get_city_state


def classify_psychographics(profile: Dict) -> List[str]:
    """
    Derive simple psychographic tags based on census traits and nonprofit names.
    """
    tags: List[str] = []
    census = profile["census"]
    nonprofits = profile["nonprofits"]

    income = census.get("median_household_income")
    median_age = census.get("median_age")
    owner_ratio = census.get("owner_ratio")
    poverty_rate = census.get("poverty_rate")

    # -----------------------------
    # INCOME TAGS
    # -----------------------------
    if income is not None:
        if income >= 150000:
            tags.append("very_affluent")
        elif income >= 90000:
            tags.append("upper_middle_income")
        elif income >= 55000:
            tags.append("middle_income")
        else:
            tags.append("lower_income")

    # -----------------------------
    # AGE TAGS
    # -----------------------------
    if median_age is not None:
        if median_age < 32:
            tags.append("younger_area")
        elif median_age > 50:
            tags.append("older_area")

    # -----------------------------
    # HOUSING TAGS
    # -----------------------------
    if owner_ratio is not None:
        if owner_ratio >= 0.65:
            tags.append("homeowner_heavy")
        elif owner_ratio <= 0.40:
            tags.append("renter_heavy")

    # -----------------------------
    # POVERTY TAGS
    # -----------------------------
    if poverty_rate is not None:
        if poverty_rate >= 0.20:
            tags.append("high_poverty")
        elif poverty_rate <= 0.08:
            tags.append("low_poverty")

    # -----------------------------
    # NONPROFIT NAME TAGS
    # -----------------------------
    names = " ".join([(n.get("name") or "") for n in nonprofits]).lower()

    faith_terms = [
        "church",
        "temple",
        "synagogue",
        "ministries",
        "mosque",
        "catholic",
        "lutheran",
        "baptist",
    ]
    if any(t in names for t in faith_terms):
        tags.append("faith_community_present")

    if "foundation" in names:
        tags.append("philanthropy_culture")

    education_terms = ["school", "academy", "education", "pta"]
    if any(t in names for t in education_terms):
        tags.append("education_present")

    animal_terms = ["animal", "humane", "rescue", "spca"]
    if any(t in names for t in animal_terms):
        tags.append("animal_welfare_present")

    return tags


def _fallback_city_state_from_nonprofits(
    nonprofits: List[Dict]
) -> Tuple[Optional[str], Optional[str]]:
    """
    If Census/geocoder doesn't give us a city/state, try to infer it from the
    nonprofits loaded from the IRS BMF CSV.

    We look for 'city' and 'state' keys on the nonprofit dicts.
    """
    if not nonprofits:
        return None, None

    cities = set(
        (n.get("city") or "").strip()
        for n in nonprofits
        if n.get("city")
    )
    states = set(
        (n.get("state") or "").strip()
        for n in nonprofits
        if n.get("state")
    )

    city = next(iter(cities)) if cities else None
    state = next(iter(states)) if states else None
    return city, state


def _build_area_label(city: Optional[str], state: Optional[str]) -> str:
    """
    Turn city/state into a human-friendly label.
    """
    if city and state:
        return f"{city}, {state}"
    if city:
        return city
    return "Unknown area"


def learn_zip(zip_code: str) -> Dict:
    """
    Build a ZIP profile.

    FLOW:
      ZIP → Census stats
      ZIP → (city, state) via Census/geocoder
      ZIP → IRS BMF nonprofits (exact ZIP)
      City/State fallback from nonprofit CSV if needed
      → Psychographic tags (from census + nonprofits)
    """
    # -----------------------------
    # CENSUS DATA
    # -----------------------------
    census_info = get_census_by_zip(zip_code)

    # -----------------------------
    # CITY / STATE (PRIMARY: CENSUS/GEOCODER)
    # -----------------------------
    city, state = get_city_state(zip_code)

    # -----------------------------
    # IRS NONPROFIT LOOKUP BY ZIP
    # -----------------------------
    nonprofits = load_bmf_rows(zip_code)

    # -----------------------------
    # CITY / STATE FALLBACK FROM NONPROFITS
    # -----------------------------
    if (city is None or state is None) and nonprofits:
        fallback_city, fallback_state = _fallback_city_state_from_nonprofits(nonprofits)
        # Only override missing pieces so we don't wipe good data
        if city is None and fallback_city:
            city = fallback_city
        if state is None and fallback_state:
            state = fallback_state

    # -----------------------------
    # BUILD PROFILE OBJECT
    # -----------------------------
    area_label = _build_area_label(city, state)

    base: Dict = {
        "zip": zip_code,
        "city": city,
        "state": state,
        "area_label": area_label,
        "census": census_info,
        "nonprofits": nonprofits,
    }

    # Psychographics derived from census + nonprofits
    base["psychographics"] = classify_psychographics(base)

    return base
