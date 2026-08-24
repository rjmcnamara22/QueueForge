from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.schemas.jobs import JobResponse
from app.processing.csv_processor import get_csv_headers, process_csv

router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["jobs"],
)


@router.post("", response_model=JobResponse)
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

    try:
        report = process_csv(contents)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return JobResponse(
        id=1,
        filename=file.filename,
        status="completed",
        columns=columns,
        total_rows=report.total_rows,
        valid_rows=report.valid_rows,
        invalid_rows=report.invalid_rows,
        duplicate_products=report.duplicate_products,
        missing_values=report.missing_values,
        invalid_numeric_values=report.invalid_numeric_values,
    )