import subprocess
import logging
import sys

# Configure logging to provide clean status updates
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_script(script_path):
    """
    Executes a Python script and handles errors.
    
    Args:
        script_path (str): The relative path to the script.
    """
    logging.info(f"--- Starting: {script_path} ---")
    try:
        result = subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
        logging.info(f"Successfully finished: {script_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred in {script_path}")
        logging.error(f"Output: {e.stderr}")
        sys.exit(1)

def main():
    # Define the sequence of operations
    # 1. Ingest Raw Data -> 2. Clean Data -> 3. Load into SQLite -> 4. Run Analytics/Recommender
    pipeline_sequence = [
        "scripts/live_nav_fetch.py",
        "scripts/data_ingestion.py",
        "scripts/data_cleaning.py",
        "scripts/db_loader.py",
        "scripts/load_extra_tables.py",
        "scripts/recommended.py"
    ]
    
    for script in pipeline_sequence:
        run_script(script)
    
    logging.info("All pipeline processes completed successfully")

if __name__ == "__main__":
    main()