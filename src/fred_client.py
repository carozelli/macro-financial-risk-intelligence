import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")

def get_fred_series(series_id):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json"
    }

    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()

    data = r.json()["observations"]
    df = pd.DataFrame(data)[["date", "value"]]

    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df


if __name__ == "__main__":
    df = get_fred_series("CPIAUCSL")

    os.makedirs("../data/raw", exist_ok=True)
    df.to_csv("../data/raw/us_cpi.csv", index=False)

    print(df.tail())
    print("\nSaved to data/raw/us_cpi.csv")
