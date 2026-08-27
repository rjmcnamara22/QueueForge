import base64
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas.jobs import JobDetailResponse, JobListItem, JobResponse
from app.database import get_db
from app.models.job import Job
from app.processing.csv_processor import get_csv_headers
from app.tasks.jobs import process_csv_job

router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["jobs"],
)


@router.post("", response_model=JobResponse)
async def create_job(
    file: Annotated[UploadFile, File()],
    db: Annotated[Session, Depends(get_db)],
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

    try:
        columns = get_csv_headers(contents)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    if not columns:
        raise HTTPException(
            status_code=400,
            detail="CSV file must contain a header row.",
        )

    job = Job(
        filename=file.filename,
        status="pending",
        total_rows=0,
        valid_rows=0,
        invalid_rows=0,
        duplicate_products=0,
        missing_values=0,
        invalid_numeric_values=0,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    encoded_contents = base64.b64encode(contents).decode("ascii")

    process_csv_job.delay(
        job.id,
        encoded_contents,
    )

    return JobResponse(
        id=job.id,
        filename=job.filename,
        status=job.status,
        columns=columns,
        total_rows=job.total_rows,
        valid_rows=job.valid_rows,
        invalid_rows=job.invalid_rows,
        duplicate_products=job.duplicate_products,
        missing_values=job.missing_values,
        invalid_numeric_values=job.invalid_numeric_values,
        created_at=job.created_at,
    )


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job(
    job_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> JobDetailResponse:
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )

    return JobDetailResponse(
        id=job.id,
        filename=job.filename,
        status=job.status,
        total_rows=job.total_rows,
        valid_rows=job.valid_rows,
        invalid_rows=job.invalid_rows,
        duplicate_products=job.duplicate_products,
        missing_values=job.missing_values,
        invalid_numeric_values=job.invalid_numeric_values,
        created_at=job.created_at,
    )


@router.get("", response_model=list[JobListItem])
def list_jobs(
    db: Annotated[Session, Depends(get_db)],
) -> list[JobListItem]:
    statement = select(Job).order_by(Job.created_at.desc())

    jobs = db.scalars(statement).all()

    return [
        JobListItem(
            id=job.id,
            filename=job.filename,
            status=job.status,
            total_rows=job.total_rows,
            valid_rows=job.valid_rows,
            invalid_rows=job.invalid_rows,
            created_at=job.created_at,
        )
        for job in jobs
    ]
