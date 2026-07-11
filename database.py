"""Async SQLite engine, connection dependency, and schema/defaults bootstrap."""

import os
from pathlib import Path

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from models import metadata, settings

DATA_PATH = Path(os.environ.get("DATA_PATH", "./data"))
DB_PATH = DATA_PATH / "assetforge.db"

DATA_PATH.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}")

DEFAULT_SETTINGS = {
    "electricity_rate_aud": ("0.32", "$/kWh for power cost estimates"),
    "currency": ("AUD", "Display currency"),
    "warranty_alert_days": ("90", "Days before expiry to show warning"),
    "backup_on_import": ("true", "Auto-backup before any import"),
    "data_path": (str(DATA_PATH), "Overridden by DATA_PATH env var"),
}


async def create_all() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


async def seed_default_settings() -> None:
    async with engine.begin() as conn:
        existing = {row.key for row in (await conn.execute(select(settings.c.key))).all()}
        missing = [
            {"key": key, "value": value, "description": description}
            for key, (value, description) in DEFAULT_SETTINGS.items()
            if key not in existing
        ]
        if missing:
            await conn.execute(insert(settings), missing)


async def get_db() -> AsyncConnection:
    async with engine.connect() as conn:
        yield conn
