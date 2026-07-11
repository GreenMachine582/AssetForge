"""Render AI context profiles as self-contained markdown — see docs/ai-context.md."""

from sqlalchemy import select
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


async def render_specs_markdown(conn: AsyncConnection) -> str:
    """Specs / Compatibility profile — GET /api/ai-context/specs [M1]."""
    query = select(assets.c.part_uid, assets.c.name, specs).join(
        specs, assets.c.part_uid == specs.c.part_uid
    )
    rows = (await conn.execute(query)).mappings().all()

    header = SPECS_COLUMNS
    lines = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join(["---"] * len(header)) + "|",
    ]
    for row in rows:
        cells = [str(row.get(col, "") or "—") for col in header]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


async def render_build_planning(conn: AsyncConnection, project_type: str, project_key: str) -> str:
    raise NotImplementedError("Build Planning profile — implemented as an M1 follow-up")


async def render_upgrade_planning(conn: AsyncConnection, project_type: str, project_key: str) -> str:
    raise NotImplementedError("Upgrade Planning profile — implemented as an M1 follow-up")
