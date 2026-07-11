"""Power draw + annual running cost estimation. [M3]"""

from sqlalchemy.ext.asyncio import AsyncConnection


async def estimate_project_power(conn: AsyncConnection, project_key: str) -> dict:
    raise NotImplementedError("Power estimation — implemented in M3")
