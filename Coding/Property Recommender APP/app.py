from flask import Flask, render_template, request
import pandas as pd
from combined_algorithm import run_algorithm  # You’ll wrap your existing script logic into a function

app = Flask(__name__)

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
            "city": request.form["city"]
        }
        results = run_algorithm(user_input)
        return render_template("results.html", properties=results)

    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True)
