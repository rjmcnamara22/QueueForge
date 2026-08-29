from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.database import SessionLocal
from app.redis_client import redis_client

router = APIRouter(
    tags=["readiness"],
)


@router.get("/ready")
def readiness_check() -> dict[str, str]:
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()

        redis_client.ping()

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Service dependencies are not ready.",
        ) from error

    return {"status": "ready"}