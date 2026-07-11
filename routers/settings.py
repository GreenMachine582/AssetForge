"""/api/settings."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from database import get_db
from models import settings
from schemas import SettingOut, SettingUpdate

router = APIRouter()


@router.get("", response_model=list[SettingOut])
async def list_settings(conn: AsyncConnection = Depends(get_db)):
    rows = (await conn.execute(select(settings))).mappings().all()
    return list(rows)


@router.put("/{key}", response_model=SettingOut)
async def update_setting(key: str, payload: SettingUpdate, conn: AsyncConnection = Depends(get_db)):
    result = await conn.execute(
        update(settings).where(settings.c.key == key).values(value=payload.value)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Setting not found")
    await conn.commit()
    row = (await conn.execute(select(settings).where(settings.c.key == key))).mappings().first()
    return row
