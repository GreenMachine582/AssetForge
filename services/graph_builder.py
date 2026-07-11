"""Materialise part-lineage graph nodes + edges from the DB. [M3]"""

from sqlalchemy.ext.asyncio import AsyncConnection


async def build_graph(conn: AsyncConnection) -> dict:
    raise NotImplementedError("Graph builder — implemented in M3")
