from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.database import get_db
from app.main import app
from app.models.base import Base
from app.models.job import Job

if not settings.test_database_url:
    raise RuntimeError("TEST_DATABASE_URL is not configured.")


test_engine = create_engine(settings.test_database_url)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()

    db.execute(delete(Job))
    db.commit()

    try:
        yield db
    finally:
        db.rollback()
        db.close()

        cleanup_db = TestingSessionLocal()

        try:
            cleanup_db.execute(delete(Job))
            cleanup_db.commit()
        finally:
            cleanup_db.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()