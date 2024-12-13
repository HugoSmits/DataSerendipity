from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

# Example dataset
DATA_FILE = "data.csv"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")  # Serve contact.html

@app.route("/services")
def services():
    return render_template("services.html")  # Serve contact.html

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")  # Serve contact.html

@app.route("/contact")
def contact():
    return render_template("contact.html")  # Serve contact.html

@app.route("/data")
def data():
    # Load and manipulate data
    df = pd.read_csv(DATA_FILE)
    result = df.groupby("Category").sum().reset_index()  # Example manipulation
    return jsonify(result.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
