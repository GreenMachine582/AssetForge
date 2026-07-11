"""/api/locations. [M2]"""

from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPLEMENTED = "Locations — implemented in M2"


@router.get("")
async def list_locations():
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.post("")
async def create_location():
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get("/{location_id}")
async def get_location(location_id: int):
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.put("/{location_id}")
async def update_location(location_id: int):
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get("/{location_id}/assets")
async def location_assets(location_id: int):
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)
