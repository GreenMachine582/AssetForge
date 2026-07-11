"""Render AI context profiles as self-contained markdown — see docs/ai-context.md."""

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncConnection

from models import assets, specs

SPECS_COLUMNS = [
    "part_uid",
    "name",
    "socket_interface",
    "form_factor",
    "tdp_watt",
    "ram_gen",
    "pcie_gen",
    "chipset",
    "slots_used",
    "slots_total",
    "compat_notes",
]

BUILD_COLUMNS = [
    "part_uid",
    "name",
    "state",
    "socket_interface",
    "form_factor",
    "tdp_watt",
    "ram_gen",
    "pcie_gen",
    "chipset",
    "slots_used",
    "slots_total",
    "compat_notes",
]

UPGRADE_COLUMNS = [
    "part_uid",
    "name",
    "state",
    "amount",
    "socket_interface",
    "form_factor",
    "tdp_watt",
    "ram_gen",
    "pcie_gen",
    "chipset",
    "compat_notes",
]


def _render_markdown_table(columns: list[str], rows) -> str:
    if not rows:
        return "_No matching assets._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "|" + "|".join(["---"] * len(columns)) + "|",
    ]
    for row in rows:
        cells = [str(row.get(col) if row.get(col) is not None else "—") for col in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _project_filter(project_type: str, project_key: str):
    return or_(
        and_(assets.c.bought_for_type == project_type, assets.c.bought_for_key == project_key),
        and_(assets.c.used_by_type == project_type, assets.c.used_by_key == project_key),
    )


async def render_specs_markdown(conn: AsyncConnection) -> str:
    """Specs / Compatibility profile — GET /api/ai-context/specs [M1]."""
    query = select(assets.c.part_uid, assets.c.name, specs).join(
        specs, assets.c.part_uid == specs.c.part_uid
    )
    rows = (await conn.execute(query)).mappings().all()
    return _render_markdown_table(SPECS_COLUMNS, rows)


async def render_build_planning(conn: AsyncConnection, project_type: str, project_key: str) -> str:
    """Build Planning profile — GET /api/ai-context/build/{type}/{key} [M1].

    Specs + state for every asset currently in the project. Does not include
    PSU-headroom/slot-availability math — that belongs to
    services/power.py / services/compatibility.py, both explicit M3 stubs.
    """
    query = (
        select(assets.c.part_uid, assets.c.name, assets.c.state, specs)
        .select_from(assets.outerjoin(specs, assets.c.part_uid == specs.c.part_uid))
        .where(_project_filter(project_type, project_key))
    )
    rows = (await conn.execute(query)).mappings().all()
    return _render_markdown_table(BUILD_COLUMNS, rows)


async def render_upgrade_planning(conn: AsyncConnection, project_type: str, project_key: str) -> str:
    """Upgrade Planning profile — GET /api/ai-context/upgrade/{type}/{key} [M1].

    Current build (non-planned assets in the project) vs. planned upgrades
    (state=planned, bought for the project), plus total planned spend.
    """
    current_query = (
        select(assets.c.part_uid, assets.c.name, assets.c.state, assets.c.amount, specs)
        .select_from(assets.outerjoin(specs, assets.c.part_uid == specs.c.part_uid))
        .where(_project_filter(project_type, project_key), assets.c.state != "planned")
    )
    planned_query = (
        select(assets.c.part_uid, assets.c.name, assets.c.state, assets.c.amount, specs)
        .select_from(assets.outerjoin(specs, assets.c.part_uid == specs.c.part_uid))
        .where(
            assets.c.bought_for_type == project_type,
            assets.c.bought_for_key == project_key,
            assets.c.state == "planned",
        )
    )

    current_rows = (await conn.execute(current_query)).mappings().all()
    planned_rows = (await conn.execute(planned_query)).mappings().all()
    planned_total = sum(row["amount"] or 0 for row in planned_rows)

    return "\n".join(
        [
            "## Current Build",
            "",
            _render_markdown_table(UPGRADE_COLUMNS, current_rows),
            "",
            "## Planned Upgrades",
            "",
            _render_markdown_table(UPGRADE_COLUMNS, planned_rows),
            "",
            f"**Total planned spend:** {planned_total:.2f}",
        ]
    )
