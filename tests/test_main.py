from unittest.mock import patch

from fastapi.testclient import TestClient


def test_read_root(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "QueueForge API"}


def test_create_job_with_csv(client: TestClient) -> None:
    with patch("app.api.routes.jobs.process_csv_job.delay") as mocked_delay:
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
    assert data["status"] == "pending"
    assert data["columns"] == ["product", "quantity", "price"]
    assert data["total_rows"] == 0
    assert data["valid_rows"] == 0
    assert data["invalid_rows"] == 0
    assert data["duplicate_products"] == 0
    assert data["missing_values"] == 0
    assert data["invalid_numeric_values"] == 0
    assert data["created_at"] is not None

    mocked_delay.assert_called_once()


def test_create_job_rejects_non_csv_file(client: TestClient) -> None:
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


def test_create_job_rejects_empty_csv(client: TestClient) -> None:
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

def test_get_job(client: TestClient) -> None:
    with patch("app.api.routes.jobs.process_csv_job.delay"):
        create_response = client.post(
            "/api/v1/jobs",
            files={
                "file": (
                    "inventory.csv",
                    b"product,quantity,price\nMiller Lite,48,3.50\n",
                    "text/csv",
                )
            },
        )

    assert create_response.status_code == 200

    created_job = create_response.json()
    job_id = created_job["id"]

    response = client.get(f"/api/v1/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == job_id
    assert data["filename"] == "inventory.csv"
    assert data["status"] == "pending"
    assert data["total_rows"] == 0
    assert data["valid_rows"] == 0
    assert data["invalid_rows"] == 0
    assert data["duplicate_products"] == 0
    assert data["missing_values"] == 0
    assert data["invalid_numeric_values"] == 0
    assert data["created_at"] is not None

def test_get_job_returns_404_for_missing_job(client: TestClient) -> None:
    response = client.get("/api/v1/jobs/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Job not found."
    }

def test_list_jobs_returns_created_jobs(client: TestClient) -> None:
    first_response = client.post(
        "/api/v1/jobs",
        files={
            "file": (
                "first.csv",
                b"product,quantity,price\nMiller Lite,48,3.50\n",
                "text/csv",
            )
        },
    )

    second_response = client.post(
        "/api/v1/jobs",
        files={
            "file": (
                "second.csv",
                b"product,quantity,price\nBud Light,24,3.25\n",
                "text/csv",
            )
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    response = client.get("/api/v1/jobs")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["filename"] == "second.csv"
    assert data[1]["filename"] == "first.csv"

def test_list_jobs_returns_empty_list(client: TestClient) -> None:
    response = client.get("/api/v1/jobs")

    assert response.status_code == 200
    assert response.json() == []
    