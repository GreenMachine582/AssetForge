"""/api/assets — CRUD, filtering, and state transitions."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from database import get_db
from models import assets, events, specs
from schemas import AssetCreate, AssetOut, AssetUpdate, TransitionRequest
from services.state_machine import validate_transition

router = APIRouter()


def _parse_type_key(value: str) -> tuple[str, str | None]:
    """Split a `type:key` filter token. A bare token with no `:` (e.g.
    "HomeLab") means "any key of this type" — `key` comes back `None`."""
    project_type, sep, project_key = value.partition(":")
    return project_type, (project_key if sep else None)


async def filtered_assets(
    conn: AsyncConnection,
    q: str | None = None,
    project: list[str] | None = None,
    category: list[str] | None = None,
    state: list[str] | None = None,
    used_by: str | None = None,
    location_id: list[int] | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    is_consumable: bool | None = None,
    warranty_expiring: int | None = None,
    reallocated: bool | None = None,
):
    """Shared filter logic for GET /api/assets and GET /partials/assets-table."""
    query = select(assets).select_from(
        assets.outerjoin(specs, assets.c.part_uid == specs.c.part_uid)
    )

    conditions = []

    if q:
        like = f"%{q}%"
        conditions.append(
            or_(
                assets.c.name.ilike(like),
                assets.c.notes.ilike(like),
                specs.c.compat_notes.ilike(like),
            )
        )

    if project:
        project_conditions = []
        for token in project:
            project_type, project_key = _parse_type_key(token)
            if project_key is None:
                # Bare type (e.g. "HomeLab") — any key of this type.
                project_conditions.append(
                    or_(
                        assets.c.bought_for_type == project_type,
                        assets.c.used_by_type == project_type,
                    )
                )
            else:
                project_conditions.append(
                    or_(
                        and_(
                            assets.c.bought_for_type == project_type,
                            assets.c.bought_for_key == project_key,
                        ),
                        and_(
                            assets.c.used_by_type == project_type,
                            assets.c.used_by_key == project_key,
                        ),
                    )
                )
        conditions.append(or_(*project_conditions))

    if category:
        conditions.append(assets.c.category.in_(category))

    if state:
        conditions.append(assets.c.state.in_(state))

    if used_by:
        used_by_type, used_by_key = _parse_type_key(used_by)
        conditions.append(assets.c.used_by_type == used_by_type)
        if used_by_key is not None:
            conditions.append(assets.c.used_by_key == used_by_key)

    if location_id:
        conditions.append(assets.c.location_id.in_(location_id))

    if from_date:
        conditions.append(assets.c.purchase_date >= from_date)
    if to_date:
        conditions.append(assets.c.purchase_date <= to_date)

    if min_amount is not None:
        conditions.append(assets.c.amount >= min_amount)
    if max_amount is not None:
        conditions.append(assets.c.amount <= max_amount)

    if is_consumable is not None:
        conditions.append(assets.c.is_consumable == is_consumable)

    if warranty_expiring is not None:
        cutoff = date.today() + timedelta(days=warranty_expiring)
        conditions.append(assets.c.warranty_expiry.isnot(None))
        conditions.append(assets.c.warranty_expiry <= cutoff)

    if reallocated:
        conditions.append(
            select(events.c.id)
            .where(events.c.part_uid == assets.c.part_uid, events.c.event_type == "reallocated")
            .exists()
        )

    if conditions:
        query = query.where(and_(*conditions))

    rows = (await conn.execute(query)).mappings().all()
    return list(rows)


@router.get("", response_model=list[AssetOut])
async def list_assets(
    q: str | None = None,
    project: list[str] = Query(default=[]),
    category: list[str] = Query(default=[]),
    state: list[str] = Query(default=[]),
    used_by: str | None = None,
    location_id: list[int] = Query(default=[]),
    from_date: date | None = None,
    to_date: date | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    is_consumable: bool | None = None,
    warranty_expiring: int | None = None,
    reallocated: bool | None = None,
    conn: AsyncConnection = Depends(get_db),
):
    return await filtered_assets(
        conn,
        q=q,
        project=project,
        category=category,
        state=state,
        used_by=used_by,
        location_id=location_id,
        from_date=from_date,
        to_date=to_date,
        min_amount=min_amount,
        max_amount=max_amount,
        is_consumable=is_consumable,
        warranty_expiring=warranty_expiring,
        reallocated=reallocated,
    )


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
