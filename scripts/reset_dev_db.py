"""Reset development database. Run: python scripts/reset_dev_db.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from atlas_ultimate_crm.core.paths import get_database_path


def reset():
    db_path = get_database_path()
    if db_path.exists():
        db_path.unlink()
        print(f"Deleted: {db_path}")
    else:
        print(f"No database found at: {db_path}")
    print("Run 'alembic upgrade head' or start the app to recreate.")


if __name__ == "__main__":
    reset()
