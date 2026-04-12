import os
from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DATA_PATH = PROJECT_ROOT / "data" / "processed" / "macro_us_with_index.csv"
FORECAST_PATH = PROJECT_ROOT / "data" / "processed" / "macro_us_index_forecast.csv"
TOP_HIGH_PATH = PROJECT_ROOT / "data" / "processed" / "top_high_stress_periods.csv"
OUTPUT_FILE = PROJECT_ROOT / "reports" / "macro_us_executive_brief.pdf"
CHART_PATH = PROJECT_ROOT / "reports" / "macro_stress_index_recent.png"


def trend_label(delta: float, threshold: float = 0.15) -> str:
    if delta > threshold:
        return "INCREASING"
    if delta < -threshold:
        return "DECREASING"
    return "STABLE"


def percentile_rank(series: pd.Series, value: float) -> float:
    return (series < value).mean() * 100


def build_executive_insight(stress_level: str, forecast_trend: str, macro_strategy: str) -> str:
    stress_level = str(stress_level).upper()
    forecast_trend = str(forecast_trend).upper()

    if stress_level in ["VERY LOW", "LOW"]:
        base = "Current macro-financial conditions remain stable, with low systemic stress."
    elif stress_level in ["MODERATE", "MEDIUM"]:
        base = "Current macro-financial conditions are moderately stressed, suggesting a more cautious planning environment."
    else:
        base = "Current macro-financial conditions indicate elevated stress, requiring closer monitoring and more defensive planning assumptions."

    if forecast_trend == "INCREASING":
        trend = "The short-term forecast suggests rising stress, which may pressure financing conditions and decision-making."
    elif forecast_trend == "DECREASING":
        trend = "The short-term forecast suggests easing stress, which may support a more constructive planning outlook."
    else:
        trend = "The short-term forecast remains broadly stable, suggesting no immediate change in the overall macro regime."

    strategy = f"The current regime-based strategy is: {macro_strategy}."

    return f"{base} {trend} {strategy}"


def draw_wrapped_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    line_height: float = 0.5 * cm,
    font_name: str = "Helvetica",
    font_size: int = 10,
) -> float:
    c.setFont(font_name, font_size)
    words = text.split()
    line = ""

    for word in words:
        test_line = f"{line} {word}".strip()
        if c.stringWidth(test_line, font_name, font_size) <= max_width:
            line = test_line
        else:
            c.drawString(x, y, line)
            y -= line_height
            line = word

    if line:
        c.drawString(x, y, line)
        y -= line_height

    return y


def make_pdf() -> None:
    os.makedirs(PROJECT_ROOT / "reports", exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["macro_stress_index"]).sort_values("date")

    latest = df.iloc[-1]
    latest_date = pd.to_datetime(latest["date"]).date()
    last_index = float(latest["macro_stress_index"])
    stress_level = str(latest["stress_level"])
    macro_strategy = str(latest.get("macro_strategy", "N/A"))

    pct = percentile_rank(df["macro_stress_index"], last_index)

    forecast_trend = "N/A"
    forecast_delta = 0.0
    if FORECAST_PATH.exists():
        fc = pd.read_csv(FORECAST_PATH)
        fc["date"] = pd.to_datetime(fc["date"])
        if len(fc) >= 2:
            forecast_delta = float(fc["macro_stress_index"].iloc[-1] - fc["macro_stress_index"].iloc[0])
            forecast_trend = trend_label(forecast_delta)

    executive_insight = build_executive_insight(stress_level, forecast_trend, macro_strategy)

    top3_text = []
    if TOP_HIGH_PATH.exists():
        top = pd.read_csv(TOP_HIGH_PATH)
        top["date"] = pd.to_datetime(top["date"])
        top = top.sort_values("macro_stress_index", ascending=False).head(3)
        for _, row in top.iterrows():
            top3_text.append(f"{row['date'].date()} (Index {float(row['macro_stress_index']):.2f})")

    c = canvas.Canvas(str(OUTPUT_FILE), pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, height - 2 * cm, "MACROECONOMIC RISK BRIEF (US)")

    c.setFont("Helvetica", 11)
    c.drawString(2 * cm, height - 3.0 * cm, f"Report Date: {latest_date}")
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
        for item in top3_text:
            c.drawString(2 * cm, y, f"- {item}")
            y -= 0.6 * cm
    else:
        c.drawString(2 * cm, y, "- N/A")
        y -= 0.6 * cm

    y -= 0.4 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Executive Insight:")
    y -= 0.7 * cm

    y = draw_wrapped_text(
        c,
        executive_insight,
        2 * cm,
        y,
        max_width=16 * cm,
        line_height=0.5 * cm,
        font_name="Helvetica",
        font_size=10,
    )

    if CHART_PATH.exists():
        c.drawImage(str(CHART_PATH), 2 * cm, 1.8 * cm, width=16 * cm, preserveAspectRatio=True)

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(
        2 * cm,
        1.2 * cm,
        "Generated automatically via Python pipeline (FRED macro series + composite index).",
    )

    c.showPage()
    c.save()

    print(f"✅ PDF upgraded with executive insight: {OUTPUT_FILE}")


if __name__ == "__main__":
    make_pdf()