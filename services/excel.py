"""openpyxl workbook builder / reader — 5-sheet tracker format.

Excel is an import/export compatibility layer only; SQLite is authoritative
(see docs/architecture.md #1). This is a fresh 5-sheet layout derived from
our own schema (Projects, Assets, Specs, Events, Settings) — there is no
legacy PC_Build_Tracker.xlsx in this repo to mirror instead.
"""

import json
from pathlib import Path

from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from models import assets, events, projects, settings, specs

SHEETS = [
    ("Projects", projects),
    ("Assets", assets),
    ("Specs", specs),
    ("Events", events),
    ("Settings", settings),
]


def _cell_value(value):
    if isinstance(value, dict):
        return json.dumps(value)
    return value


async def build_workbook(conn: AsyncConnection) -> Workbook:
    workbook = Workbook()
    workbook.remove(workbook.active)

    for sheet_name, table in SHEETS:
        sheet = workbook.create_sheet(sheet_name)
        columns = [column.name for column in table.columns]
        sheet.append(columns)

        rows = (await conn.execute(select(table))).mappings().all()
        for row in rows:
            sheet.append([_cell_value(row[column]) for column in columns])

    return workbook


def read_workbook(path: Path):
    raise NotImplementedError("Excel import — implemented as an M1 follow-up")
