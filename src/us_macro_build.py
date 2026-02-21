import os
import pandas as pd

RAW_PATH = "../data/raw"
OUT_PATH = "../data/processed"

def read_series(name: str) -> pd.DataFrame:
    df = pd.read_csv(f"{RAW_PATH}/{name}.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df = df.rename(columns={"value": name})
    return df

def to_monthly(df: pd.DataFrame, col: str, how: str = "last") -> pd.DataFrame:
    # Convert to monthly frequency
    df = df.set_index("date")
    if how == "last":
        m = df[col].resample("MS").last()
    elif how == "mean":
        m = df[col].resample("MS").mean()
    else:
        raise ValueError("how must be 'last' or 'mean'")
    return m.reset_index()

def add_features(df: pd.DataFrame, col: str) -> pd.DataFrame:
    # MoM and YoY percentage change + rolling averages
    df[f"{col}_mom_pct"] = df[col].pct_change(1) * 100
    df[f"{col}_yoy_pct"] = df[col].pct_change(12) * 100
    df[f"{col}_roll3"] = df[col].rolling(3).mean()
    df[f"{col}_roll6"] = df[col].rolling(6).mean()
    return df

if __name__ == "__main__":
    os.makedirs(OUT_PATH, exist_ok=True)

    cpi = read_series("us_cpi")
    unrate = read_series("us_unrate")
    fed = read_series("us_fedfunds")
    dgs10 = read_series("us_10y")

    # Monthly standardization:
    # CPI, UNRATE, FEDFUNDS already monthly -> just align to month start
    cpi_m = to_monthly(cpi, "us_cpi", how="last")
    unrate_m = to_monthly(unrate, "us_unrate", how="last")
    fed_m = to_monthly(fed, "us_fedfunds", how="last")

    # DGS10 is daily -> use monthly mean (more stable) OR last (choose mean)
    dgs10_m = to_monthly(dgs10, "us_10y", how="mean")

    # Merge all on date
    df = cpi_m.merge(unrate_m, on="date", how="inner") \
              .merge(fed_m, on="date", how="inner") \
              .merge(dgs10_m, on="date", how="inner") \
              .sort_values("date")

    # Add feature columns
    for col in ["us_cpi", "us_unrate", "us_fedfunds", "us_10y"]:
        df = add_features(df, col)

    # Save processed
    out_file = f"{OUT_PATH}/macro_us_monthly.csv"
    df.to_csv(out_file, index=False)

    print("✅ Built dataset:", out_file)
    print("Rows:", len(df), "| Columns:", len(df.columns))
    print(df.tail(5))
