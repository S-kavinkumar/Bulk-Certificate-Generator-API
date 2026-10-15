from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Job, Certificate
from app.schemas.job import JobCreate, JobResponse


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"]
)


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(
    job_data: JobCreate,
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

    return JobResponse(
        job_id=job.id,
        status=job.status,
        total=job.total_count
    )