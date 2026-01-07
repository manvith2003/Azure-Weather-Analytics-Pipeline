"""Test that basic setup works."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.config import config
from src.utils.database import Database

def test_config():
    print("✓ Config loaded successfully")
    print(f"  Organization size: {config.org_size}")
    print(f"  Date range: {config.start_date} to {config.end_date}")
    print(f"  API Key present: {'Yes' if config.anthropic_api_key else 'No'}")

def test_database():
    db = Database("output/test.sqlite")
    db.connect()
    print("✓ Database connection works")
    db.close()

if __name__ == "__main__":
    print("Testing setup...\n")
    test_config()
    test_database()
    print("\n✓ All tests passed!")