import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FRED_API_KEY")

SERIES = {
    "us_cpi": "CPIAUCSL",     # CPI (monthly)
    "us_unrate": "UNRATE",    # Unemployment rate (monthly)
    "us_fedfunds": "FEDFUNDS",# Fed funds rate (monthly)
    "us_10y": "DGS10",        # 10Y Treasury (daily)
}

def get_series(series_id: str) -> pd.DataFrame:
    if not API_KEY:
        raise RuntimeError("FRED_API_KEY Not found. Check your .env file in the root of the project.")

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {"series_id": series_id, "api_key": API_KEY, "file_type": "json"}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()

    obs = r.json()["observations"]
    df = pd.DataFrame(obs)[["date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"]).sort_values("date").reset_index(drop=True)
    return df

def save_raw(name: str, df: pd.DataFrame) -> None:
    os.makedirs("../data/raw", exist_ok=True)
    path = f"../data/raw/{name}.csv"
    df.to_csv(path, index=False)
    print(f"✅ Saved {name}: {path} (rows={len(df)})")

if __name__ == "__main__":
    for name, sid in SERIES.items():
        df = get_series(sid)
        save_raw(name, df)

    print("\nFRED multi download DONE ✅")
