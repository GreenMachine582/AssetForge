"""/api/export/*, /api/import/*, /api/ai-context/*."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncConnection

from database import get_db
from services.ai_context import render_specs_markdown

router = APIRouter()

_NOT_IMPLEMENTED_EXPORT = "Excel/JSON export — implemented as an M1 follow-up"
_NOT_IMPLEMENTED_IMPORT = "Excel/JSON import — implemented as an M1 follow-up"


@router.get("/export/excel")
async def export_excel():
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED_EXPORT)


@router.get("/export/json")
async def export_json():
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED_EXPORT)


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


@router.post("/import/json")
async def import_json():
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED_IMPORT)


@router.get("/ai-context/specs")
async def ai_context_specs(conn: AsyncConnection = Depends(get_db)):
    markdown = await render_specs_markdown(conn)
    return Response(content=markdown, media_type="text/markdown")


@router.get("/ai-context/build/{project_type}/{project_key}")
async def ai_context_build(project_type: str, project_key: str):
    raise HTTPException(status_code=501, detail="Build Planning profile — implemented as an M1 follow-up")


@router.get("/ai-context/upgrade/{project_type}/{project_key}")
async def ai_context_upgrade(project_type: str, project_key: str):
    raise HTTPException(status_code=501, detail="Upgrade Planning profile — implemented as an M1 follow-up")


@router.get("/ai-context/homelab")
async def ai_context_homelab():
    raise HTTPException(status_code=501, detail="HomeLab profile — implemented in M2")


@router.get("/ai-context/purchasing")
async def ai_context_purchasing():
    raise HTTPException(status_code=501, detail="Purchasing/Warranty profile — implemented in M2")
