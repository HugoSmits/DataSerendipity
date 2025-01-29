from flask import Flask, render_template, jsonify
import pandas as pd
import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
import datetime
import os

app = Flask(__name__)

# File to store the tickers
DATA_FILE = "aex_tickers.csv"

def fetch_aex_tickers():
    """Fetch AEX tickers from Wikipedia and save to CSV."""
    url = "https://nl.wikipedia.org/wiki/AEX"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table", class_="wikitable sortable")

        if len(tables) >= 2:
            table = tables[1]
            rows = table.find_all("tr")

            tickers = [cell.text.strip() for row in rows[1:] for cell in row.find_all("td")]

            # Format last fetched timestamp as DD/MM/YYYY
            last_fetched = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y ")

            # Create DataFrame with two columns
            df = pd.DataFrame({"Ticker Symbol": tickers, "Last Updated": [last_fetched] * len(tickers)})

            df.to_csv(DATA_FILE, index=False)
            print(f"✅ AEX tickers updated successfully at {last_fetched}")
        else:
            print("⚠️ Second table not found.")
    else:
        print("❌ Failed to retrieve data from Wikipedia.")


# Schedule the function to run once a day
schedule.every().day.at("02:00").do(fetch_aex_tickers)  # Runs at 2 AM daily

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# Start scheduler in a separate thread
threading.Thread(target=run_scheduler, daemon=True).start()

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

@app.route("/api/tickers")
def get_tickers():
    """Return tickers as JSON with correct column names."""
    import os
    if not os.path.exists(DATA_FILE):  
        fetch_aex_tickers()

    try:
        df = pd.read_csv(DATA_FILE)
        df = df.rename(columns={df.columns[0]: "Ticker Symbol", df.columns[1]: "Last Updated"})  # Ensure correct column names
        tickers_data = df.to_dict(orient="records")  # Convert table to JSON
        return jsonify(tickers_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
