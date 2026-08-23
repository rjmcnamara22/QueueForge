from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="QueueForge API",
    version="0.1.0",
)


class JobCreate(BaseModel):
    filename: str


class JobResponse(BaseModel):
    id: int
    filename: str
    status: str


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "QueueForge API"}


@app.post("/api/v1/jobs", response_model=JobResponse)
def create_job(job: JobCreate) -> JobResponse:
    return JobResponse(
        id=1,
        filename=job.filename,
        status="pending",
    )