from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.database import get_db, SessionLocal
from app.database.models import Job, Certificate

from app.schemas.job import (
    JobCreate,
    JobResponse,
    JobProgressResponse,
    CertificateResult
)

from app.services.certificate_generator import generate_certificate


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"]
)


def process_job(job_id: int):

    db = SessionLocal()

    try:

        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if not job:
            return

        job.status = "PROCESSING"
        db.commit()

        certificates = (
            db.query(Certificate)
            .filter(Certificate.job_id == job_id)
            .all()
        )

        for certificate in certificates:

            try:

                certificate.status = "PROCESSING"
                db.commit()

                file_path = generate_certificate(
                    recipient_name=certificate.recipient_name,
                    event_name=job.event_name,
                    certificate_id=certificate.id
                )

                certificate.file_path = file_path
                certificate.status = "COMPLETED"

                job.completed_count += 1

                db.commit()

            except Exception as error:

                certificate.status = "FAILED"
                certificate.error_message = str(error)

                job.failed_count += 1

                db.commit()

        if job.failed_count > 0:

            if job.completed_count > 0:
                job.status = "COMPLETED_WITH_ERRORS"
            else:
                job.status = "FAILED"

        else:
            job.status = "COMPLETED"

        db.commit()

    finally:
        db.close()


@router.post(
    "/",
    response_model=JobResponse,
    status_code=201
)
def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    job = Job(
        event_name=job_data.event_name,
        status="QUEUED",
        total_count=len(job_data.recipients)
    )

    db.add(job)
    db.flush()

    for recipient in job_data.recipients:

        certificate = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            status="PENDING"
        )

        db.add(certificate)

    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        process_job,
        job.id
    )

    return JobResponse(
        job_id=job.id,
        status=job.status,
        total=job.total_count
    )


@router.get(
    "/{job_id}",
    response_model=JobProgressResponse
)
def get_job_progress(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    certificates = (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id)
        .all()
    )

    remaining = (
        job.total_count
        - job.completed_count
        - job.failed_count
    )

    return JobProgressResponse(
        job_id=job.id,
        event_name=job.event_name,
        status=job.status,
        total=job.total_count,
        completed=job.completed_count,
        failed=job.failed_count,
        remaining=remaining,
        certificates=[
            CertificateResult(
                certificate_id=certificate.id,
                recipient_name=certificate.recipient_name,
                recipient_email=certificate.recipient_email,
                status=certificate.status,
                file_path=certificate.file_path,
                error_message=certificate.error_message
            )
            for certificate in certificates
        ]
    )