from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.processing.csv_processor import get_csv_headers

app = FastAPI(
    title="QueueForge API",
    version="0.1.0",
)


class JobResponse(BaseModel):
    id: int
    filename: str
    status: str
    columns: list[str]


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "QueueForge API"}


@app.post("/api/v1/jobs", response_model=JobResponse)
async def create_job(
    file: Annotated[UploadFile, File()],
) -> JobResponse:
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must have a filename.",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    contents = await file.read()
    columns = get_csv_headers(contents)

    if not columns:
        raise HTTPException(
            status_code=400,
            detail="CSV file must contain a header row.",
        )

    return JobResponse(
        id=1,
        filename=file.filename,
        status="pending",
        columns=columns,
    )
