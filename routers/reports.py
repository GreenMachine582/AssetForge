"""/api/dashboard, /api/statistics (real) + /api/reports/* (stubs)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncConnection

from database import get_db
from models import assets

router = APIRouter()


@router.get("/dashboard")
async def dashboard_data(conn: AsyncConnection = Depends(get_db)):
    total_spend = (await conn.execute(select(func.sum(assets.c.amount)))).scalar() or 0
    state_counts = dict(
        (await conn.execute(select(assets.c.state, func.count()).group_by(assets.c.state))).all()
    )
    return {"total_spend": total_spend, "state_counts": state_counts}


@router.get("/statistics")
async def statistics(conn: AsyncConnection = Depends(get_db)):
    total_assets = (await conn.execute(select(func.count()).select_from(assets))).scalar()
    return {"total_assets": total_assets}


@router.get("/reports/spend")
async def report_spend():
    raise HTTPException(status_code=501, detail="Spend breakdown report — implemented in M4")


@router.get("/reports/warranty")
async def report_warranty():
    raise HTTPException(status_code=501, detail="Warranty expiry report — implemented in M2")


@router.get("/reports/power")
async def report_power():
    raise HTTPException(status_code=501, detail="Power + cost report — implemented in M3")
