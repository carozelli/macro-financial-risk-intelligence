import os
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

DATA_PATH = "../data/processed/macro_us_with_index.csv"
FORECAST_PATH = "../data/processed/macro_us_index_forecast.csv"
TOP_HIGH_PATH = "../data/processed/top_high_stress_periods.csv"
OUTPUT_FILE = "../reports/macro_us_executive_brief.pdf"
CHART_PATH = "../reports/macro_stress_index_recent.png"  # use the zoom chart

def trend_label(delta: float, threshold: float = 0.15) -> str:
    if delta > threshold:
        return "INCREASING"
    if delta < -threshold:
        return "DECREASING"
    return "STABLE"

def percentile_rank(series, value):
    # percent of values below current
    return (series < value).mean() * 100

def make_pdf():
    os.makedirs("../reports", exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["macro_stress_index"]).sort_values("date")

    latest = df.iloc[-1]
    last_index = float(latest["macro_stress_index"])
    stress_level = str(latest["stress_level"])
    macro_strategy = str(latest.get("macro_strategy", "N/A"))

    # Percentile
    pct = percentile_rank(df["macro_stress_index"], last_index)

    # Forecast
    forecast_trend = "N/A"
    forecast_delta = 0.0
    if os.path.exists(FORECAST_PATH):
        fc = pd.read_csv(FORECAST_PATH)
        fc["date"] = pd.to_datetime(fc["date"])
        if len(fc) >= 2:
            forecast_delta = float(fc["macro_stress_index"].iloc[-1] - fc["macro_stress_index"].iloc[0])
            forecast_trend = trend_label(forecast_delta)

    # Top high stress context (top 3)
    top3_text = []
    if os.path.exists(TOP_HIGH_PATH):
        top = pd.read_csv(TOP_HIGH_PATH)
        top["date"] = pd.to_datetime(top["date"])
        top = top.sort_values("macro_stress_index", ascending=False).head(3)
        for _, r in top.iterrows():
            top3_text.append(f"{r['date'].date()} (Index {float(r['macro_stress_index']):.2f})")

    # Build PDF
    c = canvas.Canvas(OUTPUT_FILE, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, height - 2 * cm, "MACROECONOMIC RISK BRIEF (US)")

    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, height - 3 * cm, f"Report Date: {pd.to_datetime(latest['date']).date()}")
    c.drawString(2 * cm, height - 3.7 * cm, f"Macro Stress Index: {last_index:.2f}")
    c.drawString(2 * cm, height - 4.4 * cm, f"Stress Level: {stress_level}")
    c.drawString(2 * cm, height - 5.1 * cm, f"Historical Percentile: {pct:.0f}th (higher = more stress)")
    c.drawString(2 * cm, height - 5.8 * cm, f"3-Month Forecast Trend: {forecast_trend} (Δ {forecast_delta:+.2f})")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, height - 7.2 * cm, "Regime-Based Strategy:")
    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, height - 7.9 * cm, f"- {macro_strategy}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, height - 9.2 * cm, "Historical Context (Top 3 Stress Months):")
    c.setFont("Helvetica", 11)
    y = height - 9.9 * cm
    if top3_text:
        for t in top3_text:
            c.drawString(2 * cm, y, f"- {t}")
            y -= 0.6 * cm
    else:
        c.drawString(2 * cm, y, "- N/A")

    # Chart
    if os.path.exists(CHART_PATH):
        c.drawImage(CHART_PATH, 2 * cm, 2.0 * cm, width=16 * cm, preserveAspectRatio=True)

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(2 * cm, 1.4 * cm, "Generated automatically via Python pipeline (FRED macro series + composite index).")

    c.showPage()
    c.save()

    print("✅ PDF upgraded with context & percentile:", OUTPUT_FILE)

if __name__ == "__main__":
    make_pdf()