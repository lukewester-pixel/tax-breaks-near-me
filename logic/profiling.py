from data_sources.census import get_census_by_zip, get_city_state_from_zip
from data_sources.zip_utils import lookup_city_state_locally
from data_sources.irs_bmf import load_bmf_rows


def classify_psychographics(profile: dict) -> list[str]:
    tags = []
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

    faith_terms = ["church", "temple", "synagogue", "ministries", "mosque", "catholic", "lutheran", "baptist"]
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


def learn_zip(zip_code: str) -> dict:
    """
    FLOW:
      ZIP → Census stats
      ZIP → (city, state) via local map, then Census geocoder
      ZIP → IRS BMF nonprofits (exact ZIP)
    """
    # -----------------------------
    # CENSUS DATA
    # -----------------------------
    census_info = get_census_by_zip(zip_code)

    # -----------------------------
    # CITY / STATE RESOLUTION
    # -----------------------------
    city, state = lookup_city_state_locally(zip_code)

    if city is None or state is None:
        geo_city, geo_state = get_city_state_from_zip(zip_code)
        if geo_city and geo_state:
            city, state = geo_city, geo_state

    # -----------------------------
    # IRS NONPROFIT LOOKUP BY ZIP
    # -----------------------------
    nonprofits = load_bmf_rows(zip_code)

    # -----------------------------
    # BUILD PROFILE OBJECT
    # -----------------------------
    base = {
        "zip": zip_code,
        "city": city,
        "state": state,
        "census": census_info,
        "nonprofits": nonprofits,
    }

    # Psychographics derived from census + nonprofits
    base["psychographics"] = classify_psychographics(base)

    return base
