"""/api/attachments. [M2]"""

from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPLEMENTED = "Attachments — implemented in M2"


@router.get("/{uid}")
async def list_attachments(uid: str):
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.post("/{uid}")
async def upload_attachment(uid: str):
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.get("/{uid}/{attachment_id}")
async def download_attachment(uid: str, attachment_id: int):
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.delete("/{uid}/{attachment_id}")
async def delete_attachment(uid: str, attachment_id: int):
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)
