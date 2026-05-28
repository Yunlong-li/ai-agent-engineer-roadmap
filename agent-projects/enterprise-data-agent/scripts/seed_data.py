from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.data_store import DB_PATH, reset_database


if __name__ == "__main__":
    reset_database()
    print(f"seeded database: {DB_PATH}")
