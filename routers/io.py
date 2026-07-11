"""/api/export/*, /api/import/*, /api/ai-context/*."""

import json
import shutil
from datetime import date, datetime
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from sqlalchemy import Date, DateTime, select
from sqlalchemy.ext.asyncio import AsyncConnection

from database import DATA_PATH, DB_PATH, get_db
from models import assets, events, projects, settings, specs
from services.ai_context import (
    render_build_planning,
    render_specs_markdown,
    render_upgrade_planning,
)
from services.excel import build_workbook

router = APIRouter()

_NOT_IMPLEMENTED_IMPORT = "Excel import — implemented as an M1 follow-up"

# Table dump/restore order for JSON export/import. Insert order (top to
# bottom) is FK-safe; delete order for import is the reverse.
TABLES = [
    ("projects", projects),
    ("assets", assets),
    ("specs", specs),
    ("events", events),
    ("settings", settings),
]


def _json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


@router.get("/export/excel")
async def export_excel(conn: AsyncConnection = Depends(get_db)):
    workbook = await build_workbook(conn)
    buffer = BytesIO()
    workbook.save(buffer)
    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=assetforge_export.xlsx"},
    )


@router.get("/export/json")
async def export_json(conn: AsyncConnection = Depends(get_db)):
    dump = {}
    for name, table in TABLES:
        rows = (await conn.execute(select(table))).mappings().all()
        dump[name] = [dict(row) for row in rows]

    body = json.dumps(dump, default=_json_default, indent=2)
    return Response(
        content=body,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=assetforge_export.json"},
    )


@router.get("/export/specs-md")
async def export_specs_markdown(conn: AsyncConnection = Depends(get_db)):
    markdown = await render_specs_markdown(conn)
    return Response(content=markdown, media_type="text/markdown")


@router.get("/export/sqlite")
async def export_sqlite():
    raise HTTPException(status_code=501, detail="SQLite snapshot download — implemented in V1")


@router.post("/import/excel")
async def import_excel():
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED_IMPORT)


def _coerce_row(table, row: dict) -> dict:
    """Convert ISO date/datetime strings from JSON back into Python objects.

    SQLAlchemy's typed Date/DateTime columns reject plain strings on insert
    (unlike SQLite itself, which is dynamically typed).
    """
    coerced = dict(row)
    for column in table.columns:
        value = coerced.get(column.name)
        if not isinstance(value, str):
            continue
        if isinstance(column.type, DateTime):
            coerced[column.name] = datetime.fromisoformat(value)
        elif isinstance(column.type, Date):
            coerced[column.name] = date.fromisoformat(value)
    return coerced


def _backup_database() -> None:
    if not DB_PATH.exists():
        return
    backups_dir = DATA_PATH / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(DB_PATH, backups_dir / f"assetforge_{timestamp}.db")


@router.post("/import/json")
async def import_json(file: UploadFile = File(...), conn: AsyncConnection = Depends(get_db)):
    raw = await file.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}") from exc

    _backup_database()

    for _, table in reversed(TABLES):
        await conn.execute(table.delete())
    for name, table in TABLES:
        rows = payload.get(name) or []
        if rows:
            await conn.execute(table.insert(), [_coerce_row(table, row) for row in rows])
    await conn.commit()

    return {"imported": {name: len(payload.get(name) or []) for name, _ in TABLES}}


@router.get("/ai-context/specs")
async def ai_context_specs(conn: AsyncConnection = Depends(get_db)):
    markdown = await render_specs_markdown(conn)
    return Response(content=markdown, media_type="text/markdown")


@router.get("/ai-context/build/{project_type}/{project_key}")
async def ai_context_build(
    project_type: str, project_key: str, conn: AsyncConnection = Depends(get_db)
):
    markdown = await render_build_planning(conn, project_type, project_key)
    return Response(content=markdown, media_type="text/markdown")


@router.get("/ai-context/upgrade/{project_type}/{project_key}")
async def ai_context_upgrade(
    project_type: str, project_key: str, conn: AsyncConnection = Depends(get_db)
):
    markdown = await render_upgrade_planning(conn, project_type, project_key)
    return Response(content=markdown, media_type="text/markdown")


@router.get("/ai-context/homelab")
async def ai_context_homelab():
    raise HTTPException(status_code=501, detail="HomeLab profile — implemented in M2")


@router.get("/ai-context/purchasing")
async def ai_context_purchasing():
    raise HTTPException(status_code=501, detail="Purchasing/Warranty profile — implemented in M2")
