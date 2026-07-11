"""One-shot import from an existing PC_Build_Tracker.xlsx workbook.

CLI plumbing only — row-level parsing is implemented as an M1 follow-up
(see services/excel.py).
"""

import argparse
import asyncio
import os
from pathlib import Path

from database import create_all
from services.excel import read_workbook


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed AssetForge from an Excel tracker")
    parser.add_argument("--file", required=True, type=Path, help="Path to PC_Build_Tracker.xlsx")
    parser.add_argument("--db", type=Path, default=None, help="Override DB path")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be imported")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    if args.db is not None:
        os.environ["DATA_PATH"] = str(args.db.parent)

    await create_all()

    if args.dry_run:
        print(f"Dry run: would import {args.file}")
        return

    read_workbook(args.file)


if __name__ == "__main__":
    asyncio.run(main())
