from flask import Flask, render_template, request, redirect, url_for
from .combined_algorithm import run_algorithm  # Use relative import
import ast

app = Flask(__name__, template_folder='../templates')

def preprocess_results(results):
    amenity_columns = [
        "SCHOOL", "HOSPITAL", "TRANSPORT", "MARKET", "MALL"
    ]

    processed = []
    for row in results:
        # Parse image_url
        img_raw = row.get('image_url')
        try:
            parsed_imgs = ast.literal_eval(img_raw) if isinstance(img_raw, str) else img_raw
            row['image_url'] = parsed_imgs if isinstance(parsed_imgs, list) else []
        except (ValueError, SyntaxError):
            row['image_url'] = []

        # Parse description from stringified list
        if isinstance(row.get("description"), str):
            try:
                desc = eval(row["description"]) if row["description"].startswith("[") else [row["description"]]
                row["description"] = " ".join(desc).replace(" .", ".").replace(".dekat", ". Dekat")
            except Exception:
                pass

        # Format price as int
        if "price" in row and row["price"] not in [None, ""]:
            try:
                row["price"] = int(float(row["price"]))
            except:
                row["price"] = None

        # Extract amenities from binary columns
        row["amenities"] = [col for col in amenity_columns if row.get(col) == 1]

        # Remove unused fields
        row.pop("type", None)
        row.pop("address_city", None)

        processed.append(row)
    return processed

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_input = {
            "type": request.form["type"],
            "land_area": int(request.form["land_area"]),
            "building_area": int(request.form["building_area"]),
            "bedrooms": int(request.form["bedrooms"]),
            "bathrooms": int(request.form["bathrooms"]),
            "floors": int(request.form["floors"]),
            "SCHOOL": int(request.form.get("SCHOOL", 0)),
            "HOSPITAL": int(request.form.get("HOSPITAL", 0)),
            "TRANSPORT": int(request.form.get("TRANSPORT", 0)),
            "MARKET": int(request.form.get("MARKET", 0)),
            "MALL": int(request.form.get("MALL", 0)),
            "facilities": request.form.getlist("facilities"),
            "city": request.form["city"]
        }
        full_results, cbrs_results, best_persona, persona_score = run_algorithm(user_input)

        # Preprocess both result sets
        processed_full = preprocess_results(full_results)
        processed_cbrs = preprocess_results(cbrs_results)
        
        # Instead of redirecting, render the results template directly
        return render_template(
            "results_v2.html",
            full_results=processed_full,
            cbrs_results=processed_cbrs,
            prop_type=user_input["type"],
            city=user_input["city"],
            persona_name=best_persona,
            persona_score=persona_score
        )
    
    # For GET requests, just show the form
    return render_template("form_v2.html")

@app.route("/listing-map")
def listing_map():
    return render_template("listing_map.html")

if __name__ == "__main__":
    app.run(debug=True)