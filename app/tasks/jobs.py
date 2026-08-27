import base64

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.job import Job
from app.processing.csv_processor import process_csv


@celery_app.task(name="process_csv_job")  # type: ignore[untyped-decorator]
def process_csv_job(job_id: int, encoded_contents: str) -> None:
    db = SessionLocal()

    try:
        job = db.get(Job, job_id)

        if job is None:
            return

        job.status = "processing"
        db.commit()

        contents = base64.b64decode(encoded_contents)

        try:
            report = process_csv(contents)

            job.status = "completed"
            job.total_rows = report.total_rows
            job.valid_rows = report.valid_rows
            job.invalid_rows = report.invalid_rows
            job.duplicate_products = report.duplicate_products
            job.missing_values = report.missing_values
            job.invalid_numeric_values = report.invalid_numeric_values

        except (ValueError, UnicodeDecodeError):
            job.status = "failed"

        db.commit()

    finally:
        db.close()
