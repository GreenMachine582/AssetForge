"""GET /* Jinja2 page routes + /partials/* HTMX fragment routes."""

import json
import re
from datetime import date
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from database import get_db
from models import assets, events, projects, specs
from routers.assets import filtered_assets
from services.serialization import json_default
from services.state_machine import TRANSITIONS, validate_transition

router = APIRouter()
templates = Jinja2Templates(directory="templates")
# `type`/`key` values are free text (e.g. "PC Build") and can contain spaces,
# which breaks both CSS id selectors and unencoded URL path segments.
templates.env.filters["urlenc"] = lambda value: quote(str(value), safe="")
templates.env.filters["slug"] = lambda value: re.sub(r"[^a-zA-Z0-9_-]+", "-", str(value))


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


def _parse_filters(request: Request) -> dict:
    qp = request.query_params

    def _float(name):
        val = qp.get(name)
        return float(val) if val else None

    def _int_list(name):
        return [int(v) for v in qp.getlist(name) if v]

    def _date(name):
        val = qp.get(name)
        return date.fromisoformat(val) if val else None

    def _bool(name):
        val = qp.get(name)
        if not val:
            return None
        return val.lower() in ("1", "true", "yes", "on")

    return {
        "q": qp.get("q") or None,
        "project": qp.getlist("project"),
        "category": qp.getlist("category"),
        "state": qp.getlist("state"),
        "used_by": qp.get("used_by") or None,
        "location_id": _int_list("location_id"),
        "from_date": _date("from_date"),
        "to_date": _date("to_date"),
        "min_amount": _float("min_amount"),
        "max_amount": _float("max_amount"),
        "is_consumable": _bool("is_consumable"),
        "warranty_expiring": int(qp["warranty_expiring"]) if qp.get("warranty_expiring") else None,
        "reallocated": _bool("reallocated"),
    }


def _asset_rows_json(rows) -> str:
    display_rows = []
    for row in rows:
        row = dict(row)
        row["project"] = (
            f"{row['bought_for_type']}:{row['bought_for_key']}"
            if row.get("bought_for_type")
            else ""
        )
        display_rows.append(row)
    return json.dumps(display_rows, default=json_default)


@router.get("/")
async def dashboard(request: Request, conn: AsyncConnection = Depends(get_db)):
    total_spend = (await conn.execute(select(func.sum(assets.c.amount)))).scalar() or 0

    planned_spend = (
        await conn.execute(
            select(func.sum(assets.c.amount)).where(assets.c.state == "planned")
        )
    ).scalar() or 0

    state_counts_rows = (
        await conn.execute(select(assets.c.state, func.count()).group_by(assets.c.state))
    ).all()
    state_counts = {state: count for state, count in state_counts_rows}

    spend_by_type_rows = (
        await conn.execute(
            select(assets.c.bought_for_type, func.sum(assets.c.amount))
            .where(assets.c.bought_for_type.isnot(None))
            .group_by(assets.c.bought_for_type)
        )
    ).all()

    recent = (
        await conn.execute(
            select(assets).order_by(assets.c.created_at.desc()).limit(5)
        )
    ).mappings().all()

    project_rows = (await conn.execute(select(projects))).mappings().all()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "total_spend": total_spend,
            "planned_spend": planned_spend,
            "state_counts": state_counts,
            "recent_assets": recent,
            "spend_by_type_json": json.dumps(
                {t: s for t, s in spend_by_type_rows}, default=json_default
            ),
            "projects": project_rows,
        },
    )


async def _all_projects(conn: AsyncConnection):
    return (await conn.execute(select(projects))).mappings().all()


@router.get("/assets")
async def assets_page(request: Request, conn: AsyncConnection = Depends(get_db)):
    filters = _parse_filters(request)
    rows = await filtered_assets(conn, **filters)
    return templates.TemplateResponse(
        request,
        "assets.html",
        {
            "filters": filters,
            "rows_json": _asset_rows_json(rows),
            "all_projects": await _all_projects(conn),
        },
    )


@router.get("/partials/filter-bar")
async def partial_filter_bar(request: Request, conn: AsyncConnection = Depends(get_db)):
    filters = _parse_filters(request)
    return templates.TemplateResponse(
        request,
        "partials/filter-bar.html",
        {"filters": filters, "all_projects": await _all_projects(conn)},
    )


@router.get("/partials/assets-table")
async def partial_assets_table(request: Request, conn: AsyncConnection = Depends(get_db)):
    filters = _parse_filters(request)
    rows = await filtered_assets(conn, **filters)
    return templates.TemplateResponse(
        request, "partials/assets-table.html", {"rows_json": _asset_rows_json(rows)}
    )


async def _event_timeline_rows(conn: AsyncConnection, uid: str):
    rows = (
        await conn.execute(
            select(events).where(events.c.part_uid == uid).order_by(events.c.date.desc())
        )
    ).mappings().all()
    return rows


@router.get("/partials/event-timeline/{uid}")
async def partial_event_timeline(uid: str, request: Request, conn: AsyncConnection = Depends(get_db)):
    rows = await _event_timeline_rows(conn, uid)
    return templates.TemplateResponse(
        request, "partials/event-timeline.html", {"uid": uid, "events": rows, "oob": False}
    )


async def _state_badge_context(conn: AsyncConnection, uid: str) -> dict:
    row = (await conn.execute(select(assets.c.state).where(assets.c.part_uid == uid))).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"uid": uid, "state": row.state, "transitions": TRANSITIONS.get(row.state, [])}


@router.get("/partials/state-badge/{uid}")
async def partial_state_badge(uid: str, request: Request, conn: AsyncConnection = Depends(get_db)):
    context = await _state_badge_context(conn, uid)
    context["oob"] = False
    return templates.TemplateResponse(request, "partials/state-badge.html", context)


@router.get("/partials/asset-card/{uid}")
async def partial_asset_card(uid: str, request: Request, conn: AsyncConnection = Depends(get_db)):
    row = (
        await conn.execute(
            select(assets, specs)
            .select_from(assets.outerjoin(specs, assets.c.part_uid == specs.c.part_uid))
            .where(assets.c.part_uid == uid)
        )
    ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    event_rows = await _event_timeline_rows(conn, uid)
    breadcrumb = []
    for event in reversed(event_rows):
        if event["to_project_type"]:
            hop = f"{event['to_project_type']}:{event['to_project_key']}"
            if not breadcrumb or breadcrumb[-1] != hop:
                breadcrumb.append(hop)

    return templates.TemplateResponse(
        request,
        "partials/asset-card.html",
        {"asset": row, "breadcrumb": breadcrumb},
    )


@router.post("/partials/asset/{uid}/note")
async def partial_asset_note(
    uid: str, request: Request, notes: str = Form(""), conn: AsyncConnection = Depends(get_db)
):
    result = await conn.execute(
        update(assets).where(assets.c.part_uid == uid).values(notes=notes)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Asset not found")
    await conn.execute(insert(events).values(part_uid=uid, event_type="noted", notes=notes))
    await conn.commit()

    row = (await conn.execute(select(assets).where(assets.c.part_uid == uid))).mappings().first()
    event_rows = await _event_timeline_rows(conn, uid)

    note_html = templates.get_template("partials/asset-note.html").render(
        {"request": request, "asset": row}
    )
    timeline_html = templates.get_template("partials/event-timeline.html").render(
        {"request": request, "uid": uid, "events": event_rows, "oob": True}
    )
    return HTMLResponse(content=note_html + timeline_html)


@router.post("/partials/asset/{uid}/state")
async def partial_asset_state(
    uid: str, request: Request, new_state: str = Form(...), conn: AsyncConnection = Depends(get_db)
):
    row = (await conn.execute(select(assets).where(assets.c.part_uid == uid))).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    try:
        validate_transition(row["state"], new_state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    await conn.execute(update(assets).where(assets.c.part_uid == uid).values(state=new_state))
    await conn.execute(
        insert(events).values(
            part_uid=uid,
            event_type=new_state if new_state in ("installed", "removed") else "noted",
        )
    )
    await conn.commit()

    badge_context = await _state_badge_context(conn, uid)
    badge_context["oob"] = False
    badge_html = templates.get_template("partials/state-badge.html").render(
        {"request": request, **badge_context}
    )
    event_rows = await _event_timeline_rows(conn, uid)
    timeline_html = templates.get_template("partials/event-timeline.html").render(
        {"request": request, "uid": uid, "events": event_rows, "oob": True}
    )
    return HTMLResponse(content=badge_html + timeline_html)


@router.get("/specs")
async def specs_page(request: Request, conn: AsyncConnection = Depends(get_db)):
    query = select(assets.c.part_uid, assets.c.name, specs).select_from(
        assets.outerjoin(specs, assets.c.part_uid == specs.c.part_uid)
    )
    rows = (await conn.execute(query)).mappings().all()
    rows_json = json.dumps([dict(row) for row in rows], default=json_default)
    return templates.TemplateResponse(request, "specs.html", {"rows_json": rows_json})


async def _project_card_context(conn: AsyncConnection, project_type: str, project_key: str, expanded: bool) -> dict:
    project_row = (
        await conn.execute(
            select(projects).where(projects.c.type == project_type, projects.c.key == project_key)
        )
    ).mappings().first()
    if project_row is None:
        raise HTTPException(status_code=404, detail="Project not found")

    bought_for = (assets.c.bought_for_type == project_type) & (assets.c.bought_for_key == project_key)
    used_by = (assets.c.used_by_type == project_type) & (assets.c.used_by_key == project_key)

    bought_for_total = (
        await conn.execute(select(func.sum(assets.c.amount)).where(bought_for))
    ).scalar() or 0
    used_by_total = (
        await conn.execute(select(func.sum(assets.c.amount)).where(used_by))
    ).scalar() or 0

    project_assets_rows = (
        await conn.execute(select(assets).where(or_(bought_for, used_by)))
    ).mappings().all()

    state_counts = {}
    for row in project_assets_rows:
        state_counts[row["state"]] = state_counts.get(row["state"], 0) + 1

    return {
        "project": project_row,
        "bought_for_total": bought_for_total,
        "used_by_total": used_by_total,
        "item_count": len(project_assets_rows),
        "state_counts": state_counts,
        "state_counts_json": json.dumps(state_counts),
        "assets": project_assets_rows if expanded else [],
        "expanded": expanded,
    }


@router.get("/projects")
async def projects_page(request: Request, conn: AsyncConnection = Depends(get_db)):
    project_rows = (await conn.execute(select(projects))).mappings().all()
    cards = [
        await _project_card_context(conn, row["type"], row["key"], expanded=False)
        for row in project_rows
    ]
    return templates.TemplateResponse(request, "projects.html", {"cards": cards})


@router.get("/partials/project-card/{project_type}/{project_key}")
async def partial_project_card(
    project_type: str,
    project_key: str,
    request: Request,
    expanded: bool = False,
    conn: AsyncConnection = Depends(get_db),
):
    context = await _project_card_context(conn, project_type, project_key, expanded)
    return templates.TemplateResponse(request, "partials/project-card.html", context)
