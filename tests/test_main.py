from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "QueueForge API"}


def test_create_job() -> None:
    response = client.post(
        "/api/v1/jobs",
        json={"filename": "inventory.csv"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "filename": "inventory.csv",
        "status": "pending",
    }