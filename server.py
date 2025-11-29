from dotenv import load_dotenv
load_dotenv()  # Load .env variables like CENSUS_API_KEY before anything else

from flask import Flask, request, jsonify, render_template
from logic.recommendations import generate_tax_breaks

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    # Render the HTML page with the ZIP form
    return render_template("index.html")


@app.route("/api/tax-breaks", methods=["GET"])
def api_tax_breaks():
    zip_code = request.args.get("zip", "").strip()

    # Any missing / non-numeric / wrong length ZIP → same error
    if not zip_code or not zip_code.isdigit() or len(zip_code) != 5:
        return jsonify({"error": "Enter a valid California ZIP."}), 400

    try:
        # This will call learn_zip -> get_census_by_zip, etc.
        result = generate_tax_breaks(zip_code)
    except Exception as e:
        # If anything blows up while building the profile, treat it as invalid ZIP
        print("Error in generate_tax_breaks:", e)
        return jsonify({"error": "Enter a valid California ZIP."}), 400

    profile = result.get("profile", {})

    # If Census came back empty for this ZIP, treat it as not a valid CA ZIP
    if not profile.get("census"):
        return jsonify({"error": "Enter a valid California ZIP."}), 400

    return jsonify({
        "zip": result["zip"],
        "city": profile["city"],
        "state": profile["state"],
        "area_label": profile.get("area_label"),
        "psychographics": profile["psychographics"],
        "census": profile["census"],
        "recommendations": result["recommendations"],
        "nonprofit_count": len(profile["nonprofits"]),
        "nonprofits": profile["nonprofits"],
    })


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
