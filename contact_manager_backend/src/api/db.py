from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _build_postgres_url() -> str:
    """
    Prefer POSTGRES_URL if provided, otherwise construct from discrete env vars.
    """
    postgres_url = os.getenv("POSTGRES_URL", "").strip().strip('"').strip("'")
    if postgres_url:
        # Normalize for SQLAlchemy which expects postgresql+psycopg2
        if postgres_url.startswith("postgresql://") and "+psycopg2" not in postgres_url:
            return postgres_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return postgres_url

    user = os.getenv("POSTGRES_USER", "").strip().strip('"').strip("'")
    password = os.getenv("POSTGRES_PASSWORD", "").strip().strip('"').strip("'")
    db = os.getenv("POSTGRES_DB", "").strip().strip('"').strip("'")
    port = os.getenv("POSTGRES_PORT", "").strip().strip('"').strip("'")
    # host is embedded in POSTGRES_URL in this template; default to localhost
    host = "localhost"
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


_ENGINE = create_engine(
    _build_postgres_url(),
    pool_pre_ping=True,
)

_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE)


# PUBLIC_INTERFACE
def get_db() -> Session:
    """Yield a SQLAlchemy DB session for request-scoped dependency injection."""
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
