from flask import Flask, render_template, jsonify
import pandas as pd
import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
import datetime
import os
import glob
import yfinance as yf

app = Flask(__name__)

# File to store the tickers
DATA_FILE = "aex_tickers.csv"
OUTPUT_DIRECTORY = "aex_data/"
LOG_FILE = "stock_download_log.csv"

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

            tickers = []
            for row in rows[1:]:  # Skip header row
                cells = row.find_all("td")
                if cells:
                    ticker = cells[0].text.strip()
                    tickers.append(ticker)

            # Format last fetched timestamp
            last_fetched = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y ")

            # Create DataFrame
            df = pd.DataFrame({"Ticker Symbol": tickers, "Last Updated": [last_fetched] * len(tickers)})
            
            # Remove any non-ticker rows
            df = df[df["Ticker Symbol"].str.match(r'^[A-Z0-9]+$', na=False)]

            df.to_csv(DATA_FILE, index=False)

            print(f"✅ AEX tickers updated successfully at {last_fetched}")

        else:
            print("⚠️ Second table not found.")
    else:
        print("❌ Failed to retrieve data from Wikipedia.")


def fetch_aex_stock_data(df):
    """Fetch historical stock data for AEX tickers and save to CSV."""
    aex_stocks = df["Ticker Symbol"].tolist()
    aex_exchange_symbol = ".AS"  # Amsterdam exchange suffix

    failed_stocks = []
    log_data = []

    # ✅ Ensure the directory exists before downloading files
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
        print(f"📂 Created directory: {OUTPUT_DIRECTORY}")

    for stock in aex_stocks:
        try:
            # Fetch historical data
            stock_data = yf.download(stock + aex_exchange_symbol, period='max')

            if not stock_data.empty:
                # Get available start and end dates
                start_date = stock_data.index.min().strftime('%Y-%m-%d')
                end_date = stock_data.index.max().strftime('%Y-%m-%d')

                # Save dataframe to CSV
                file_path = os.path.join(OUTPUT_DIRECTORY, f"{stock}_data_{start_date}_{end_date}.csv")
                stock_data.to_csv(file_path)

                # Log the download details
                log_data.append([stock, start_date, end_date, datetime.datetime.now().strftime('%H:%M:%S - %Y-%m-%d')])

                print(f"✅ Successfully downloaded and saved data for {stock}.")
            else:
                print(f"⚠️ Downloaded data for {stock} is empty.")
                failed_stocks.append(stock)
        except Exception as e:
            print(f"❌ Failed to download data for {stock}: {e}")
            failed_stocks.append(stock)

    # Save logs
    if log_data:
        log_df = pd.DataFrame(log_data, columns=["Ticker Symbol", "Start Date", "End Date", "Downloaded At"])
        log_df.to_csv(LOG_FILE, mode='a', header=True, index=False)

    if failed_stocks:
        print("⚠️ Failed to download data for the following stocks:", failed_stocks)

# Schedule both updates to run daily at 2 AM
schedule.every().day.at("02:00").do(fetch_aex_tickers)

schedule.every().day.at("02:00").do(fetch_aex_stock_data) 

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

@app.route("/games")
def games():
    return render_template("games.html")  # New Games Page

@app.route("/games/plinko")
def plinko():
    return render_template("plinko.html")  # Plinko subpage

@app.route("/contact")
def contact():
    return render_template("contact.html")  # Serve contact.html

#python -c "import app; app.fetch_aex_tickers()"
@app.route("/api/tickers")
def get_tickers():
    """Return tickers as JSON with correct column names."""
    if not os.path.exists(DATA_FILE):  
        fetch_aex_tickers()

    try:
        df = pd.read_csv(DATA_FILE)
        df = df.rename(columns={df.columns[0]: "Ticker Symbol", df.columns[1]: "Last Updated"})  # Ensure correct column names
        tickers_data = df.to_dict(orient="records")  # Convert table to JSON
        return jsonify(tickers_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#python -c "import app; app.fetch_aex_stock_data()"
#python -c "import app; df = app.pd.read_csv('aex_tickers.csv'); app.fetch_aex_stock_data(df)"
@app.route("/api/stock_data")
def get_stock_data():
    """Return stock data download logs as JSON."""
    try:
        # Ensure file exists before reading
        if not os.path.exists("stock_download_log.csv"):
            return jsonify({"error": "Stock download log file does not exist"}), 404

        # Read and return data
        df = pd.read_csv(LOG_FILE)

        # Ensure the CSV has the correct columns
        if df.empty or "Ticker Symbol" not in df.columns:
            return jsonify({"error": "No stock data found"}), 404

        stocks_data = df.to_dict(orient="records")
        return jsonify(stocks_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/stocks_from_data")
def get_stocks_from_data():
    """Return tickers listed in the Stock Data table."""
    try:
        # Get stock files (ensure filenames match ticker names)
        stock_files = [
            file.split("_data_")[0] for file in os.listdir(OUTPUT_DIRECTORY) if file.endswith(".csv")
        ]
        return jsonify(sorted(set(stock_files)))  # Unique tickers in sorted order

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/available_tickers")
def get_available_tickers():
    """Return only tickers that have actual data files."""
    available_tickers = set()

    if not os.path.exists(OUTPUT_DIRECTORY):
        return jsonify([])  # Return an empty list if directory does not exist

    csv_files = glob.glob(os.path.join(OUTPUT_DIRECTORY, "*_data_*.csv"))
    for file in csv_files:
        filename = os.path.basename(file)  # Get only filename (no path)
        ticker = filename.split("_data_")[0]  # Extract ticker symbol
        available_tickers.add(ticker)

    return jsonify(sorted(available_tickers))  # Ensure sorted unique list


@app.route("/api/stock_data/<ticker>")
def get_stock_data_by_ticker(ticker):
    """Load stock data and return valid JSON response."""
    matching_files = [
        file for file in os.listdir(OUTPUT_DIRECTORY) if file.startswith(f"{ticker}_data_")
    ]

    if not matching_files:
        return jsonify({"error": "No stock data found"}), 404

    latest_file = sorted(matching_files)[-1]

    try:
        df = pd.read_csv(os.path.join(OUTPUT_DIRECTORY, latest_file), skiprows=2)

        # ✅ Debugging Step: Print column names
        print("🔍 DataFrame Columns:", df.columns.tolist())

        # ✅ Ensure correct column names
        expected_columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
        df.columns = expected_columns

        # ✅ Fix Date Parsing
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")

        # ✅ Convert numeric columns
        for col in ["Close", "High", "Low", "Open", "Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # ✅ Drop rows with NaN values
        df = df.dropna()

        return jsonify(df.to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
