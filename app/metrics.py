from prometheus_client import Counter, Histogram

jobs_created_total = Counter(
    "queueforge_jobs_created_total",
    "Total number of CSV processing jobs created.",
)

job_upload_size_bytes = Histogram(
    "queueforge_job_upload_size_bytes",
    "Size of uploaded CSV files in bytes.",
)

job_dispatch_total = Counter(
    "queueforge_job_dispatch_total",
    "Total number of jobs dispatched to the Celery queue.",
)