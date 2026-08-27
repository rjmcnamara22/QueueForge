from datetime import datetime

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: int
    filename: str
    status: str
    columns: list[str]
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_products: int
    missing_values: int
    invalid_numeric_values: int
    created_at: datetime


class JobDetailResponse(BaseModel):
    id: int
    filename: str
    status: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_products: int
    missing_values: int
    invalid_numeric_values: int
    created_at: datetime


class JobListItem(BaseModel):
    id: int
    filename: str
    status: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    created_at: datetime