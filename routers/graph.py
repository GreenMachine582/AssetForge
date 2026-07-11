"""/api/graph — part lineage graph. [M3]"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("")
async def get_graph():
    raise HTTPException(status_code=501, detail="Part lineage graph — implemented in M3")
