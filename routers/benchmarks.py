"""/api/benchmarks. [M4]"""

from fastapi import APIRouter, HTTPException

router = APIRouter()

_NOT_IMPLEMENTED = "Benchmarks — implemented in M4"


@router.get("/{uid}")
async def list_benchmarks(uid: str):
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.post("/{uid}")
async def add_benchmark(uid: str):
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)


@router.delete("/{benchmark_id}")
async def delete_benchmark(benchmark_id: int):
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED)
