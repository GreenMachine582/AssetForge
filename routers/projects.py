"""/api/projects — identity is the composite (type, key), not key alone."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from database import get_db
from models import assets, projects
from schemas import ProjectCreate, ProjectOut

router = APIRouter()


@router.get("", response_model=list[ProjectOut])
async def list_projects(conn: AsyncConnection = Depends(get_db)):
    rows = (await conn.execute(select(projects))).mappings().all()
    return list(rows)


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(payload: ProjectCreate, conn: AsyncConnection = Depends(get_db)):
    await conn.execute(insert(projects).values(**payload.model_dump()))
    await conn.commit()
    row = (
        await conn.execute(
            select(projects).where(
                projects.c.type == payload.type, projects.c.key == payload.key
            )
        )
    ).mappings().first()
    return row


@router.get("/{project_type}/{project_key}", response_model=ProjectOut)
async def get_project(
    project_type: str, project_key: str, conn: AsyncConnection = Depends(get_db)
):
    row = (
        await conn.execute(
            select(projects).where(
                projects.c.type == project_type, projects.c.key == project_key
            )
        )
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return row


@router.put("/{project_type}/{project_key}", response_model=ProjectOut)
async def update_project(
    project_type: str,
    project_key: str,
    payload: ProjectCreate,
    conn: AsyncConnection = Depends(get_db),
):
    result = await conn.execute(
        update(projects)
        .where(projects.c.type == project_type, projects.c.key == project_key)
        .values(**payload.model_dump())
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    await conn.commit()
    row = (
        await conn.execute(
            select(projects).where(
                projects.c.type == payload.type, projects.c.key == payload.key
            )
        )
    ).mappings().first()
    return row


@router.get("/{project_type}/{project_key}/assets")
async def project_assets(
    project_type: str, project_key: str, conn: AsyncConnection = Depends(get_db)
):
    bought_for = (assets.c.bought_for_type == project_type) & (
        assets.c.bought_for_key == project_key
    )
    used_by = (assets.c.used_by_type == project_type) & (assets.c.used_by_key == project_key)
    rows = (await conn.execute(select(assets).where(bought_for | used_by))).mappings().all()
    return list(rows)
