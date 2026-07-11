"""GET /* Jinja2 page routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncConnection

from database import get_db
from models import assets

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/")
async def dashboard(request: Request, conn: AsyncConnection = Depends(get_db)):
    total_spend = (await conn.execute(select(func.sum(assets.c.amount)))).scalar() or 0

    state_counts_rows = (
        await conn.execute(select(assets.c.state, func.count()).group_by(assets.c.state))
    ).all()
    state_counts = {state: count for state, count in state_counts_rows}

    recent = (
        await conn.execute(
            select(assets).order_by(assets.c.created_at.desc()).limit(5)
        )
    ).mappings().all()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "total_spend": total_spend,
            "state_counts": state_counts,
            "recent_assets": recent,
        },
    )
