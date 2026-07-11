"""openpyxl workbook builder / reader — 5-sheet tracker format.

Excel is an import/export compatibility layer only; SQLite is authoritative
(see docs/architecture.md #1). Row-level parsing is implemented as an M1
follow-up, not part of the initial scaffold.
"""

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncConnection


async def build_workbook(conn: AsyncConnection):
    raise NotImplementedError("Excel export — implemented as an M1 follow-up")


def read_workbook(path: Path):
    raise NotImplementedError("Excel import — implemented as an M1 follow-up")
