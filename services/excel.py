"""openpyxl workbook builder — export-only, 5-sheet tracker format.

Excel is an export format for shareability only; SQLite is authoritative
(see docs/architecture.md #1). Data is entered through the web UI.
Sheets: Projects, Assets, Specs, Events, Settings.
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


