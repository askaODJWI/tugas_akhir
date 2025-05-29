from flask import Flask, render_template, request, redirect, url_for
from combined_algorithm_v13 import run_algorithm
import ast

app = Flask(__name__)
results_cache = {}  # Temporary cache for user session result

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
        results_from_algorithm = run_algorithm(user_input)
        
        processed_results = []
        for row in results_from_algorithm:
            img_raw = row.get('image_url')
            try:
                parsed_imgs = ast.literal_eval(img_raw) if isinstance(img_raw, str) else img_raw
                row['image_url'] = parsed_imgs if isinstance(parsed_imgs, list) else []
            except (ValueError, SyntaxError):
                row['image_url'] = []
            row.pop("type", None)
            row.pop("address_city", None)
            processed_results.append(row)

        # Save results and metadata in memory (or pass via redirect/session if needed)
        results_cache["results"] = processed_results
        results_cache["type"] = user_input["type"]
        results_cache["city"] = user_input["city"]

        return redirect(url_for("results"))

    return render_template("form_v2.html")

@app.route("/results")
def results():
    properties_data = results_cache.get("results", [])
    prop_type = results_cache.get("type", "property")
    city = results_cache.get("city", "your city")

    
    # print("Properties data for template:", properties_data)
    # if properties_data:
    #     print("First property image_url type:", type(properties_data[0].get('image_url')))
    #     print("First property facilities type:", type(properties_data[0].get('facilities')))
    #     print("First property best_persona_match:", properties_data[0].get('best_persona_match'))

    return render_template("results_v2.html", properties=properties_data, prop_type=prop_type, city=city)

@app.route("/listing-map")
def listing_map():
    return render_template("listing_map.html")

if __name__ == "__main__":
    app.run(debug=True)