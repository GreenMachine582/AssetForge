"""AssetForge — FastAPI app entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import create_all, seed_default_settings
from routers import (
    assets,
    attachments,
    benchmarks,
    events,
    graph,
    io,
    locations,
    pages,
    projects,
    reports,
    settings,
    specs,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all()
    await seed_default_settings()
    yield


app = FastAPI(title="AssetForge", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(specs.router, prefix="/api/specs", tags=["specs"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])
app.include_router(attachments.router, prefix="/api/attachments", tags=["attachments"])
app.include_router(benchmarks.router, prefix="/api/benchmarks", tags=["benchmarks"])
app.include_router(reports.router, prefix="/api", tags=["reports"])
app.include_router(io.router, prefix="/api", tags=["import/export"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
