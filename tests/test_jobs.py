from tests.conftest import TestingSessionLocal
def test_create_job(client):

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "recipients": [
                {
                    "name": "Kavin Kumar",
                    "email": "kavin@example.com"
                },
                {
                    "name": "Rahul Kumar",
                    "email": "rahul@example.com"
                }
            ]
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["job_id"] > 0
    assert data["status"] == "QUEUED"
    assert data["total"] == 2

def test_empty_recipients_rejected(client):

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "recipients": []
        }
    )

    assert response.status_code == 422

def test_invalid_email_rejected(client):

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "recipients": [
                {
                    "name": "Kavin Kumar",
                    "email": "invalid-email"
                }
            ]
        }
    )

    assert response.status_code == 422

def test_duplicate_recipient_rejected(client):

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "recipients": [
                {
                    "name": "Kavin Kumar",
                    "email": "kavin@example.com"
                },
                {
                    "name": "Kavin Kumar",
                    "email": "kavin@example.com"
                }
            ]
        }
    )

    assert response.status_code == 422

def test_get_job_progress(client):

    create_response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "recipients": [
                {
                    "name": "Kavin Kumar",
                    "email": "kavin@example.com"
                }
            ]
        }
    )

    assert create_response.status_code == 201

    job_id = create_response.json()["job_id"]

    response = client.get(
        f"/api/jobs/{job_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["event_name"] == "Python Workshop"
    assert data["total"] == 1

def test_job_not_found(client):

    response = client.get(
        "/api/jobs/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"

def test_more_than_100_recipients_rejected(client):

    recipients = [
        {
            "name": f"Participant {i}",
            "email": f"user{i}@example.com"
        }
        for i in range(101)
    ]

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "recipients": recipients
        }
    )

    assert response.status_code == 422

def test_individual_certificate_failure_does_not_stop_job(
    db,
    monkeypatch
):
    from app.database.models import Job, Certificate
    from app.routers.jobs import process_job
    from tests.conftest import TestingSessionLocal

    call_count = 0

    def mock_generate_certificate(
        recipient_name,
        event_name,
        certificate_id
    ):
        nonlocal call_count

        call_count += 1

        if call_count == 1:
            raise Exception("Simulated PDF generation failure")

        return f"generated_certificates/{recipient_name}.pdf"

    monkeypatch.setattr(
        "app.routers.jobs.generate_certificate",
        mock_generate_certificate
    )

    monkeypatch.setattr(
        "app.routers.jobs.SessionLocal",
        TestingSessionLocal
    )

    job = Job(
        event_name="Python Workshop",
        status="QUEUED",
        total_count=2,
        completed_count=0,
        failed_count=0
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    certificate1 = Certificate(
        job_id=job.id,
        recipient_name="Kavin Kumar",
        recipient_email="kavin@example.com",
        status="PENDING"
    )

    certificate2 = Certificate(
        job_id=job.id,
        recipient_name="Rahul Kumar",
        recipient_email="rahul@example.com",
        status="PENDING"
    )

    db.add_all([
        certificate1,
        certificate2
    ])

    db.commit()

    process_job(job.id)

    db.refresh(job)

    assert job.failed_count == 1
    assert job.completed_count == 1
    assert job.status == "COMPLETED_WITH_ERRORS"