# 📊 Automated Macro-Financial Risk Intelligence System

## 🚀 Business Problem

Financial planning teams need automated monitoring of macroeconomic risk to support budgeting, scenario planning, and capital allocation decisions. 

This project simulates an enterprise-level FP&A macro risk intelligence system that automatically ingests real economic data, engineers financial indicators, classifies macro regimes, and generates executive-ready reports.

## Overview

This project is an automated macro-financial analytics pipeline built in Python.

It retrieves real economic data from the Federal Reserve (FRED API), processes multiple macroeconomic indicators, applies a rule-based risk scoring model, and generates executive-level reports in Excel and PDF format.

The solution was designed to simulate a Financial Planning & Analysis (FP&A) macroeconomic monitoring tool capable of supporting strategic decision-making through data-driven insights and automated reporting.

---

## Data Sources

- Federal Reserve Economic Data (FRED)
- Indicators used:
  - CPI (Inflation)
  - Unemployment Rate
  - Federal Funds Rate
  - 10-Year Treasury Yield

---

## Key Features

- API-based data ingestion
- Monthly standardization of macroeconomic indicators
- Feature engineering (MoM, YoY, Rolling averages)
- Composite Macro Financial Stress Index (MFSI)
- Regime-based risk classification
- Strategic macroeconomic interpretation
- SQLite database storage
- SQL-based executive queries
- Automated Excel report with conditional styling
- Automated PDF executive brief
- Short-term stress forecasting (3-month regression)
- Full pipeline execution with logging

---

## Visual Output

### Macro Financial Stress Index (Last 15 Years + Forecast)

![Macro Stress Index](reports/macro_stress_index_recent.png)

---

## Risk Engine Logic

The system assigns a macro risk score based on:

- Elevated inflation levels
- Rising unemployment momentum
- High policy interest rate environment
- Bond yield stress

A composite Macro Financial Stress Index (MFSI) is calculated using standardized macroeconomic variables.

The macro environment is then classified into risk regimes:

- VERY LOW
- LOW
- MODERATE
- ELEVATED
- CRITICAL

Each regime is mapped to a historical macroeconomic interpretation to support financial planning and scenario analysis.

---

## Outputs

- `reports/macro_us_report.xlsx`
- `reports/macro_us_executive_brief.pdf`
- `reports/macro_stress_index_full.png`
- `reports/macro_stress_index_recent.png`
- `data/processed/macro.db`
- `logs/automation.log`

---

## Business Application

This system simulates an automated macroeconomic monitoring tool that could support:

- Budget scenario planning
- Inflation monitoring
- Interest rate exposure analysis
- Capital expenditure review
- Strategic financial forecasting
- Risk-based portfolio allocation

By automating data collection, transformation, and reporting, the system reduces manual workload while improving analytical consistency and timeliness.

---

## How to Run

```bash
py run_pipeline.py
