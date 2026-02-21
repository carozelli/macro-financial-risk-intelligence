import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

DATA_PATH = "../data/processed/macro_us_with_risk.csv"
OUT_PATH = "../data/processed"

def z_score(series):
    return (series - series.mean()) / series.std()

def classify_index(value):
    if value >= 2:
        return "CRITICAL"
    elif value >= 1:
        return "ELEVATED"
    elif value >= 0:
        return "MODERATE"
    elif value >= -1:
        return "LOW"
    else:
        return "VERY LOW"

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])

    # Create Z-scores
    df["z_cpi"] = z_score(df["us_cpi_yoy_pct"])
    df["z_unrate"] = z_score(df["us_unrate"])
    df["z_fedfunds"] = z_score(df["us_fedfunds"])
    df["z_10y"] = z_score(df["us_10y"])

    # Composite index
    df["macro_stress_index"] = (
        df["z_cpi"] +
        df["z_unrate"] +
        df["z_fedfunds"] +
        df["z_10y"]
    )

    # Remove rows where index cannot be calculated
    df = df.dropna(subset=["macro_stress_index"])

    df["stress_level"] = df["macro_stress_index"].apply(classify_index)

    def regime_strategy(level):
        mapping = {
            "VERY LOW": "Pro-Growth regime: Favor Equities, Tech, Small Caps",
            "LOW": "Stable regime: Maintain balanced equity exposure",
            "MODERATE": "Rising stress: Rotate into Quality sectors",
            "ELEVATED": "Tightening: Consider Utilities, Value",
            "CRITICAL": "Defensive: Increase Cash, Bonds, Gold"
        }
        return mapping.get(level, "No strategy")

    df["macro_strategy"] = df["stress_level"].apply(regime_strategy)

    top_high = df.sort_values("macro_stress_index", ascending=False).head(10)
    top_low = df.sort_values("macro_stress_index").head(10)

    top_high.to_csv("../data/processed/top_high_stress_periods.csv", index=False)
    top_low.to_csv("../data/processed/top_low_stress_periods.csv", index=False)

    print("✅ Top risk periods saved.")

    os.makedirs(OUT_PATH, exist_ok=True)
    df.to_csv(f"{OUT_PATH}/macro_us_with_index.csv", index=False)

    print("✅ Macro Financial Stress Index Created")
    print(df[["date", "macro_stress_index", "stress_level"]].tail())

# --- Forecast + Plot ---
forecast_periods = 3
window = 24

df = df.sort_values("date")

recent = df.tail(window).copy()
recent["t"] = np.arange(len(recent))

# Linear regression (trend)
slope, intercept = np.polyfit(recent["t"], recent["macro_stress_index"], 1)

future_t = np.arange(len(recent), len(recent) + forecast_periods)
forecast_values = intercept + slope * future_t

last_date = df["date"].max()
future_dates = pd.date_range(
    last_date + pd.offsets.MonthBegin(1),
    periods=forecast_periods,
    freq="MS"
)

forecast_df = pd.DataFrame({
    "date": future_dates,
    "macro_stress_index": forecast_values
})

# Save forecast to CSV (useful for PDF/Excel)
forecast_df.to_csv("../data/processed/macro_us_index_forecast.csv", index=False)

plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["macro_stress_index"], label="Historical")
plt.plot(
    forecast_df["date"],
    forecast_df["macro_stress_index"],
    linestyle="--",
    label="Forecast (3m)"
)
plt.legend()
plt.title("Macro Financial Stress Index (US) + Forecast")
plt.xlabel("Date")
plt.ylabel("Stress Index")
plt.tight_layout()
plt.savefig("../reports/macro_stress_index.png")

print("✅ Chart with forecast saved to reports/macro_stress_index.png")
# Linear regression
coeffs = np.polyfit(recent["t"], recent["macro_stress_index"], 1)
slope, intercept = coeffs

future_t = np.arange(len(recent), len(recent) + forecast_periods)
forecast_values = intercept + slope * future_t

last_date = df["date"].max()
future_dates = pd.date_range(
    last_date + pd.offsets.MonthBegin(1),
    periods=forecast_periods,
    freq="MS"
)

forecast_df = pd.DataFrame({
    "date": future_dates,
    "macro_stress_index": forecast_values
})

# Plot 1: Full history
plt.figure(figsize=(10, 5))
plt.plot(df["date"], df["macro_stress_index"], label="Historical")
plt.plot(forecast_df["date"], forecast_df["macro_stress_index"], linestyle="--", label="Forecast (3m)")
plt.legend()
plt.title("Macro Financial Stress Index (US) + Forecast (Full History)")
plt.xlabel("Date")
plt.ylabel("Stress Index")
plt.tight_layout()
plt.savefig("../reports/macro_stress_index_full.png")

# Plot 2: Recent zoom (last 15 years)
cutoff = df["date"].max() - pd.DateOffset(years=15)
recent_df = df[df["date"] >= cutoff]

plt.figure(figsize=(10, 5))
plt.plot(recent_df["date"], recent_df["macro_stress_index"], label="Historical (Last 15y)")
plt.plot(forecast_df["date"], forecast_df["macro_stress_index"], linestyle="--", marker="o", label="Forecast (3m)")
plt.legend()
plt.title("Macro Financial Stress Index (US) + Forecast (Last 15 Years)")
plt.xlabel("Date")
plt.ylabel("Stress Index")
plt.tight_layout()
plt.savefig("../reports/macro_stress_index_recent.png")

print("✅ Charts saved:")
print(" - reports/macro_stress_index_full.png")
print(" - reports/macro_stress_index_recent.png")
