import requests

BASE_URL = "https://projects.propublica.org/nonprofits/api/v2"

def search_nonprofits_by_city(city: str, state: str, limit: int = 20) -> list[dict]:
    """
    Search nonprofits using city + state instead of ZIP.

    This is much more reliable than ZIP text search for ProPublica.
    We pass "City State" as a general query and then keep what's relevant.
    """
    if not city or not state:
        return []

    url = f"{BASE_URL}/search.json"
    params = {
        "q": f"{city} {state}",
    }

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    orgs = data.get("organizations", []) or []

    results = []
    for org in orgs[:limit]:
        results.append({
            "name": org.get("name"),
            "city": org.get("city"),
            "state": org.get("state"),
            "ein": org.get("ein"),
            "ntee_code": org.get("ntee_code"),
        })

    return results
