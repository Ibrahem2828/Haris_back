import os
import tempfile
from pathlib import Path

db_path = Path(tempfile.gettempdir()) / f"test_haris_{os.getpid()}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
os.environ["SEED_ON_STARTUP"] = "true"

from app import crud  # noqa: E402
from app.database import SessionLocal, init_db  # noqa: E402

init_db()
db = SessionLocal()
try:
    crud.seed_defaults(db)
finally:
    db.close()
