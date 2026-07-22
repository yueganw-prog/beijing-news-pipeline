# Cron entry point for Railway — invoked by their cron service
# Usage: python scripts/cron_entry.py
import subprocess, sys
subprocess.run([sys.executable, "scripts/run_pipeline.py"], check=True)
