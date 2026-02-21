import os
import sqlite3
import pandas as pd

CSV_PATH = "../data/processed/macro_us_with_risk.csv"
DB_PATH = "../data/processed/macro.db"

def main():
    os.makedirs("../data/processed", exist_ok=True)

    df = pd.read_csv(CSV_PATH)
    df["date"] = pd.to_datetime(df["date"])

    conn = sqlite3.connect(DB_PATH)

    df.to_sql("macro_us", conn, if_exists="replace", index=False)

    q_snapshot = """
    SELECT date, risk_level, risk_score, alerts,
           ROUND(us_cpi_yoy_pct,2) AS cpi_yoy_pct,
           ROUND(us_unrate,2) AS unrate,
           ROUND(us_fedfunds,2) AS fedfunds,
           ROUND(us_10y,2) AS us10y
    FROM macro_us
    ORDER BY date DESC
    LIMIT 1;
    """
    snap = pd.read_sql_query(q_snapshot, conn)

    q_last12 = """
    SELECT date,
           ROUND(us_cpi_yoy_pct,2) AS cpi_yoy_pct,
           ROUND(us_unrate,2) AS unrate,
           ROUND(us_fedfunds,2) AS fedfunds,
           ROUND(us_10y,2) AS us10y,
           risk_level,
           risk_score
    FROM macro_us
    ORDER BY date DESC
    LIMIT 12;
    """
    last12 = pd.read_sql_query(q_last12, conn)

    conn.close()

    snap.to_csv("../data/processed/sql_snapshot.csv", index=False)
    last12.to_csv("../data/processed/sql_last12.csv", index=False)

    print("✅ SQLite DB:", DB_PATH)
    print("✅ SQL outputs:")
    print(" - data/processed/sql_snapshot.csv")
    print(" - data/processed/sql_last12.csv")

if __name__ == "__main__":
    main()
