import pandas as pd
import os

DATA_PATH = "../data/processed/macro_us_monthly.csv"
OUT_PATH = "../data/processed"

def evaluate_risk(row):
    alerts = []
    score = 0

    # Inflation risk
    if row["us_cpi_yoy_pct"] > 4:
        alerts.append("High Inflation Risk")
        score += 2

    # Unemployment rising
    if row["us_unrate_mom_pct"] > 0.5:
        alerts.append("Rising Unemployment Risk")
        score += 1

    # Interest rate pressure
    if row["us_fedfunds"] > 4:
        alerts.append("High Interest Rate Environment")
        score += 2

    # Yield stress
    if row["us_10y"] > 4:
        alerts.append("Bond Yield Stress")
        score += 1

    return pd.Series([score, "; ".join(alerts)])

def classify_score(score):
    if score >= 5:
        return "HIGH RISK"
    elif score >= 3:
        return "MEDIUM RISK"
    else:
        return "LOW RISK"

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])

    # Apply risk logic
    df[["risk_score", "alerts"]] = df.apply(evaluate_risk, axis=1)
    df["risk_level"] = df["risk_score"].apply(classify_score)

    # Keep only latest month for executive summary
    latest = df.sort_values("date").iloc[-1]

    os.makedirs(OUT_PATH, exist_ok=True)
    df.to_csv(f"{OUT_PATH}/macro_us_with_risk.csv", index=False)

    print("✅ Risk Engine Applied")
    print("\nLatest Month:")
    print(latest[["date", "risk_score", "risk_level", "alerts"]])
