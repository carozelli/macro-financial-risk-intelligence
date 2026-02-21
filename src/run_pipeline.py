import subprocess
import sys
import os
import logging

os.makedirs("../logs", exist_ok=True)

logging.basicConfig(
    filename="../logs/automation.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

scripts = [
    "fred_multi.py",
    "us_macro_build.py",
    "us_risk_engine.py",
    "sql_store_and_query.py",
    "us_macro_index.py",
    "us_excel_report.py",
    "us_pdf_report.py"
]

def run_script(script):
    logging.info(f"Running {script}")
    print(f"\n▶ Running {script}...")

    result = subprocess.run([sys.executable, script], capture_output=True, text=True)

    if result.stdout:
        logging.info(result.stdout.strip())
    if result.stderr:
        logging.error(result.stderr.strip())

    if result.returncode != 0:
        print(f"❌ Error in {script}")
        logging.error(f"Pipeline failed at {script}")
        sys.exit(1)

if __name__ == "__main__":
    for s in scripts:
        run_script(s)

    print("\n🎯 FULL PIPELINE EXECUTED SUCCESSFULLY")
    logging.info("FULL PIPELINE EXECUTED SUCCESSFULLY")
