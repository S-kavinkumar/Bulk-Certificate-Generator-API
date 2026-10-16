from app.database.models import Certificate


def test_certificate_download(client, db, tmp_path):

    pdf_file = tmp_path / "certificate.pdf"

    pdf_file.write_bytes(
        b"%PDF-1.4 test certificate"
    )

    certificate = Certificate(
        job_id=1,
        recipient_name="Kavin Kumar",
        recipient_email="kavin@example.com",
        status="COMPLETED",
        file_path=str(pdf_file)
    )

    from app.database.models import Job

    job = Job(
        event_name="Python Workshop",
        status="COMPLETED",
        total_count=1,
        completed_count=1,
        failed_count=0
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    certificate.job_id = job.id

    db.add(certificate)
    db.commit()
    db.refresh(certificate)

    response = client.get(
        f"/api/certificates/{certificate.id}/download"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

def test_certificate_not_found(client):

    response = client.get(
        "/api/certificates/999999/download"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Certificate not found"