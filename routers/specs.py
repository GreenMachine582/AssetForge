"""/api/specs."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from database import get_db
from models import specs
from schemas import SpecOut, SpecUpdate

router = APIRouter()


@router.get("", response_model=list[SpecOut])
async def list_specs(conn: AsyncConnection = Depends(get_db)):
    rows = (await conn.execute(select(specs))).mappings().all()
    return list(rows)


@router.get("/{uid}", response_model=SpecOut)
async def get_spec(uid: str, conn: AsyncConnection = Depends(get_db)):
    row = (await conn.execute(select(specs).where(specs.c.part_uid == uid))).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Spec not found")
    return row


@router.put("/{uid}", response_model=SpecOut)
async def update_spec(uid: str, payload: SpecUpdate, conn: AsyncConnection = Depends(get_db)):
    values = {k: v for k, v in payload.model_dump().items() if v is not None}
    if values:
        result = await conn.execute(
            update(specs).where(specs.c.part_uid == uid).values(**values)
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Spec not found")
        await conn.commit()
    row = (await conn.execute(select(specs).where(specs.c.part_uid == uid))).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Spec not found")
    return row
