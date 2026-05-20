import os
import tempfile
from pathlib import Path

from pydantic import BaseModel


default_db_dir = Path(os.getenv("HARIS_DB_DIR", tempfile.gettempdir())) / "haris_backend"
default_db_dir.mkdir(parents=True, exist_ok=True)
default_database_url = f"sqlite:///{(default_db_dir / 'haris.db').as_posix()}"


class Settings(BaseModel):
    app_name: str = "Haris Backend"
    app_name_ar: str = "حارس"
    version: str = "1.0.0"
    database_url: str = os.getenv("DATABASE_URL", default_database_url)
    seed_on_startup: bool = os.getenv("SEED_ON_STARTUP", "true").lower() in {"1", "true", "yes"}


settings = Settings()
