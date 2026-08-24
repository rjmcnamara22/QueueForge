from fastapi import FastAPI

from app.api.routes.jobs import router as jobs_router

app = FastAPI(
    title="QueueForge API",
    version="0.1.0",
)

app.include_router(jobs_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "QueueForge API"}