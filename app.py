from logic.recommendations import generate_tax_breaks


def main():
    zip_code = input("Enter a ZIP code: ").strip()

    result = generate_tax_breaks(zip_code)
    profile = result["profile"]
    recs = result["recommendations"]

    # -------------------------
    # PROFILE SECTION
    # -------------------------
    print(f"\n=== ZIP {zip_code} PROFILE ===")
    print("City/state:", profile["city"], profile["state"])
    print("Psychographics:", profile["psychographics"])
    print("\nCensus snapshot:", profile["census"])

    nonprofits = profile["nonprofits"]
    print(f"\n=== Local Nonprofits from IRS BMF for {zip_code} ({len(nonprofits)} found) ===")
    if not nonprofits:
        print("No IRS-listed nonprofits found for this ZIP in eo_ca.csv.")
    else:
        for org in nonprofits[:10]:
            print(f" - {org['name']} ({org['city']}, {org['state']}) | EIN: {org['ein']}")

    # -------------------------
    # RECOMMENDATION SECTION
    # -------------------------
    print(f"\n=== Tax Breaks Near You (3 ideas) ===")
    if not recs:
        print("No recommendations generated (no nonprofits or tags to work with).")
    else:
        for i, rec in enumerate(recs, start=1):
            print(f"\n{i}. {rec['title']}")
            print("   ", rec["description"])
            print("   Tax angle:", rec["tax_angle"])

    print("\n(General info only, not tax advice. Talk to a tax pro for your specific situation.)")


if __name__ == "__main__":
    main()
