from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Certificate


router = APIRouter(
    prefix="/api/certificates",
    tags=["Certificates"]
)


@router.get("/{certificate_id}/download")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db)
):

    certificate = (
        db.query(Certificate)
        .filter(Certificate.id == certificate_id)
        .first()
    )

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    if certificate.status != "COMPLETED":
        raise HTTPException(
            status_code=409,
            detail=(
                f"Certificate is not available. "
                f"Current status: {certificate.status}"
            )
        )

    if not certificate.file_path:
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found"
        )

    file_path = Path(certificate.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Certificate file does not exist"
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.name
    )