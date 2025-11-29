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

    if not zip_code:
        return jsonify({"error": "Missing 'zip' query parameter"}), 400

    if not zip_code.isdigit() or len(zip_code) != 5:
        return jsonify({"error": "ZIP must be a 5-digit number"}), 400

    try:
        result = generate_tax_breaks(zip_code)
    except Exception as e:
        # For debugging logs on Render
        print("Error in generate_tax_breaks:", e)
        return jsonify({"error": "Server error while generating recommendations"}), 500

    profile = result["profile"]

    return jsonify({
        "zip": result["zip"],
        "city": profile["city"],
        "state": profile["state"],
        "area_label": profile.get("area_label"),
        "psychographics": profile["psychographics"],
        "census": profile["census"],
        "recommendations": result["recommendations"],
        "nonprofit_count": len(profile["nonprofits"]),
        # 🔥 send the actual nonprofit list to the frontend
        "nonprofits": profile["nonprofits"],
    })


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
