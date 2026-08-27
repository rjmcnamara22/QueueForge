from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "QueueForge API"}


def test_create_job_with_csv() -> None:
    response = client.post(
        "/api/v1/jobs",
        files={
            "file": (
                "inventory.csv",
                b"product,quantity,price\nMiller Lite,48,3.50\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["id"], int)
    assert data["id"] > 0
    assert data["filename"] == "inventory.csv"
    assert data["status"] == "completed"
    assert data["columns"] == ["product", "quantity", "price"]
    assert data["total_rows"] == 1
    assert data["valid_rows"] == 1
    assert data["invalid_rows"] == 0
    assert data["duplicate_products"] == 0
    assert data["missing_values"] == 0
    assert data["invalid_numeric_values"] == 0
    assert data["created_at"] is not None


def test_create_job_rejects_non_csv_file() -> None:
    response = client.post(
        "/api/v1/jobs",
        files={
            "file": (
                "notes.txt",
                b"hello world",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Only CSV files are supported."
    }


def test_create_job_rejects_empty_csv() -> None:
    response = client.post(
        "/api/v1/jobs",
        files={
            "file": (
                "empty.csv",
                b"",
                "text/csv",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "CSV file must contain a header row."
    }
    