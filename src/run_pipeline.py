import subprocess
import sys
import os
import logging
from pathlib import Path

# Absolute path to the src folder
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "automation.log",
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
    script_path = BASE_DIR / script

    logging.info(f"Running {script}")
    print(f"\n▶ Running {script}...")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)
        logging.info(result.stdout.strip())

    if result.stderr:
        print(result.stderr)
        logging.error(result.stderr.strip())

    if result.returncode != 0:
        print(f"❌ Error in {script}")
        logging.error(f"Pipeline failed at {script}")
        sys.exit(1)

    print(f"✅ Finished {script}")

if __name__ == "__main__":
    for s in scripts:
        run_script(s)

    print("\n🎯 FULL PIPELINE EXECUTED SUCCESSFULLY")
    logging.info("FULL PIPELINE EXECUTED SUCCESSFULLY")