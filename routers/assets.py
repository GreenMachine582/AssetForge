"""/api/assets — CRUD + state transitions."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from database import get_db
from models import assets, events
from schemas import AssetCreate, AssetOut, AssetUpdate, TransitionRequest
from services.state_machine import validate_transition

router = APIRouter()


@router.get("", response_model=list[AssetOut])
async def list_assets(conn: AsyncConnection = Depends(get_db)):
    rows = (await conn.execute(select(assets))).mappings().all()
    return list(rows)


@router.post("", response_model=AssetOut, status_code=201)
async def create_asset(payload: AssetCreate, conn: AsyncConnection = Depends(get_db)):
    await conn.execute(insert(assets).values(**payload.model_dump()))
    await conn.execute(
        insert(events).values(
            part_uid=payload.part_uid,
            event_type="purchased",
            to_project_type=payload.bought_for_type,
            to_project_key=payload.bought_for_key,
        )
    )
    await conn.commit()
    row = (
        await conn.execute(select(assets).where(assets.c.part_uid == payload.part_uid))
    ).mappings().first()
    return row


@router.get("/{uid}", response_model=AssetOut)
async def get_asset(uid: str, conn: AsyncConnection = Depends(get_db)):
    row = (await conn.execute(select(assets).where(assets.c.part_uid == uid))).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return row


@router.put("/{uid}", response_model=AssetOut)
async def update_asset(uid: str, payload: AssetUpdate, conn: AsyncConnection = Depends(get_db)):
    values = {k: v for k, v in payload.model_dump().items() if v is not None}
    if values:
        result = await conn.execute(
            update(assets).where(assets.c.part_uid == uid).values(**values)
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Asset not found")
        await conn.commit()
    row = (await conn.execute(select(assets).where(assets.c.part_uid == uid))).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return row


@router.post("/{uid}/transition", response_model=AssetOut)
async def transition_asset(
    uid: str, payload: TransitionRequest, conn: AsyncConnection = Depends(get_db)
):
    row = (await conn.execute(select(assets).where(assets.c.part_uid == uid))).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    try:
        validate_transition(row["state"], payload.new_state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    await conn.execute(
        update(assets).where(assets.c.part_uid == uid).values(state=payload.new_state)
    )
    await conn.execute(
        insert(events).values(
            part_uid=uid,
            event_type=payload.new_state if payload.new_state in ("installed", "removed") else "noted",
            notes=payload.notes,
        )
    )
    await conn.commit()
    updated = (
        await conn.execute(select(assets).where(assets.c.part_uid == uid))
    ).mappings().first()
    return updated
