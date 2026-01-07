"""Quick test to verify generation works on a small scale."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

# Override config for quick test
os.environ["ORG_SIZE"] = "100"
os.environ["NUM_TEAMS"] = "5"
os.environ["PROJECT_COUNT"] = "10"
os.environ["TASK_MULTIPLIER"] = "5"
os.environ["DB_PATH"] = "output/test_asana.sqlite"

from src.main import main

if __name__ == "__main__":
    print("Running quick test generation...")
    print("This will create a small database for testing")
    print("=" * 60)
    main()