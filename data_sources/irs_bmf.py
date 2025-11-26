import csv
from typing import List, Dict

# Path to your downloaded IRS BMF file for California.
# Make sure eo_ca.csv is actually in the data_sources/ folder.
BMF_PATH = "data_sources/eo_ca.csv"


def load_bmf_rows(zip_code: str) -> List[Dict]:
    """
    Return all nonprofit orgs in the IRS BMF dataset that match the given ZIP.
    Assumes a single-state IRS BMF CSV (e.g., California only).
    """
    matches: List[Dict] = []

    try:
        # IRS CSV tends to use latin-1 encoding
        with open(BMF_PATH, "r", encoding="latin-1") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # ZIP column can have extra formats, normalize it
                possible_zip_cols = ["ZIP", "ZIP_CD", "ZIPCODE"]
                raw_zip = ""
                for col in possible_zip_cols:
                    if col in row and row[col]:
                        raw_zip = row[col]
                        break

                # Strip ZIP+4 (e.g., 92008-1234)
                org_zip = raw_zip.strip().split("-")[0]

                if org_zip == zip_code:
                    matches.append({
                        "name": (row.get("NAME") or "").title(),
                        "city": (row.get("CITY") or "").title(),
                        "state": row.get("STATE") or "",
                        "ein": row.get("EIN") or row.get("EIN_NUM") or "",
                        "subsection_code": row.get("SUBSECTION") or "",
                        "classification": row.get("NTEE_CD") or "",
                        "status": row.get("STATUS") or "",
                    })

    except FileNotFoundError:
        print(f"[IRS BMF] File not found at {BMF_PATH}. Did you put eo_ca.csv in data_sources/?")
    except Exception as e:
        print("[IRS BMF] Error reading IRS BMF file:", e)

    return matches
