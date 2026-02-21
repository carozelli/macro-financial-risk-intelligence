import pandas as pd

DATA_PATH = "../data/processed/macro_us_with_risk.csv"

def generate_summary(latest_row):
    summary = f"""
MACROECONOMIC RISK BRIEF

Date: {latest_row['date']}
Risk Level: {latest_row['risk_level']}
Risk Score: {latest_row['risk_score']}

Key Alerts:
{latest_row['alerts']}

Strategic Considerations:
"""

    if latest_row["risk_level"] == "HIGH RISK":
        summary += """
- Consider tightening cost controls
- Review capital expenditure plans
- Evaluate hedging strategies
"""
    elif latest_row["risk_level"] == "MEDIUM RISK":
        summary += """
- Monitor inflation and employment trends closely
- Stress-test financial forecasts
"""
    else:
        summary += """
- Maintain current strategic positioning
- Continue monitoring bond and rate developments
"""

    return summary


if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    latest = df.sort_values("date").iloc[-1]

    summary = generate_summary(latest)

    print(summary)
