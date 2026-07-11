"""/api/events."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncConnection

from database import get_db
from models import events
from schemas import EventCreate, EventOut

router = APIRouter()


@router.get("", response_model=list[EventOut])
async def list_events(part_uid: str | None = None, conn: AsyncConnection = Depends(get_db)):
    query = select(events)
    if part_uid:
        query = query.where(events.c.part_uid == part_uid)
    rows = (await conn.execute(query.order_by(events.c.date.desc()))).mappings().all()
    return list(rows)


@router.post("", response_model=EventOut, status_code=201)
async def create_event(payload: EventCreate, conn: AsyncConnection = Depends(get_db)):
    result = await conn.execute(insert(events).values(**payload.model_dump()))
    await conn.commit()
    row = (
        await conn.execute(select(events).where(events.c.id == result.inserted_primary_key[0]))
    ).mappings().first()
    return row


@router.get("/{event_id}", response_model=EventOut)
async def get_event(event_id: int, conn: AsyncConnection = Depends(get_db)):
    row = (await conn.execute(select(events).where(events.c.id == event_id))).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return row
