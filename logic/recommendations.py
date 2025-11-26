from typing import List, Dict, Optional
from logic.profiling import learn_zip


def _find_org(nonprofits: List[Dict], keywords: List[str]) -> Optional[Dict]:
    """
    Simple helper to find the first nonprofit whose name contains
    any of the keywords.
    """
    lowered = [k.lower() for k in keywords]

    for org in nonprofits:
        name = (org.get("name") or "").lower()
        if any(word in name for word in lowered):
            return org

    return None


def generate_tax_breaks(zip_code: str) -> Dict:
    """
    Use:
      - IRS BMF nonprofits (exact ZIP)
      - Psychographic tags
      - Census info
    to generate 3 ZIP-personalized tax write-off ideas.
    """
    profile = learn_zip(zip_code)
    tags = profile["psychographics"]
    nonprofits = profile["nonprofits"]
    census = profile["census"]
    city = profile["city"]
    state = profile["state"]

    recs: List[Dict] = []

    def has(tag: str) -> bool:
        return tag in tags

    # ---------------------------------------------------
    # 1. EDUCATION nonprofit (boosters, academy, PTA, etc.)
    # ---------------------------------------------------
    edu_org = _find_org(
        nonprofits,
        ["school", "academy", "education", "pta", "band", "booster", "lancer"]
    )
    if edu_org:
        recs.append({
            "title": f"Support Local Education in {zip_code}",
            "description": (
                f"Consider supporting **{edu_org['name']}** in {edu_org['city']}, {edu_org['state']}. "
                "They support students, school programs, or youth enrichment—big priorities in communities "
                f"like {city or zip_code}."
            ),
            "tax_angle": (
                "Most school-focused 501(c)(3) organizations qualify for tax-deductible donations "
                "if you itemize deductions."
            ),
        })

    # ---------------------------------------------------
    # 2. FAITH COMMUNITY GIVE (if present)
    # ---------------------------------------------------
    faith_org = None
    if has("faith_community_present"):
        faith_org = _find_org(
            nonprofits,
            ["church", "catholic", "temple", "synagogue", "mosque", "ministries"]
        )

    if faith_org:
        recs.append({
            "title": "Give Through a Local Faith or Community Organization",
            "description": (
                f"**{faith_org['name']}** in {faith_org['city']}, {faith_org['state']} appears in your area's "
                "nonprofit list. Faith-based orgs often run food drives, youth programs, and aid funds."
            ),
            "tax_angle": (
                "Most qualifying faith-based organizations are automatically treated as 501(c)(3)s, "
                "making tithes and general donations tax-deductible when itemizing."
            ),
        })

    # ---------------------------------------------------
    # 3. ENVIRONMENTAL / ANIMAL nonprofit
    # ---------------------------------------------------
    env_org = None

    if has("animal_welfare_present"):
        env_org = _find_org(
            nonprofits,
            ["animal", "rescue", "humane", "spca"]
        )

    if env_org is None:
        env_org = _find_org(
            nonprofits,
            ["conservation", "ecolife", "habitat", "environment", "lagoon"]
        )

    if env_org:
        recs.append({
            "title": "Support Local Environmental or Animal Efforts",
            "description": (
                f"In areas like {city or zip_code}, nature and animal groups make a big impact. "
                f"**{env_org['name']}** in {env_org['city']}, {env_org['state']} is one local organization "
                "working in this space."
            ),
            "tax_angle": (
                "Donations to recognized environmental and animal 501(c)(3) groups are typically "
                "eligible for itemized charitable deductions."
            ),
        })

    # ---------------------------------------------------
    # FALLBACK (if we don't get 3)
    # ---------------------------------------------------
    if len(recs) < 3 and nonprofits:
        fallback = nonprofits[0]
        recs.append({
            "title": "Support a Local Nonprofit in Your ZIP",
            "description": (
                f"There are {len(nonprofits)} IRS-registered nonprofits in {zip_code}. "
                f"One example is **{fallback['name']}** in {fallback['city']}, {fallback['state']}."
            ),
            "tax_angle": (
                "Most donations to registered 501(c)(3) nonprofits qualify for tax deductions "
                "if you itemize and keep proper documentation."
            ),
        })

    # Keep only 3
    recs = recs[:3]

    return {
        "zip": zip_code,
        "profile": profile,
        "recommendations": recs,
    }
