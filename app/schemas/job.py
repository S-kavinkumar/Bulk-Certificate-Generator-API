from pydantic import BaseModel, Field, EmailStr


class RecipientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None


class JobCreate(BaseModel):
    event_name: str = Field(..., min_length=1, max_length=255)
    recipients: list[RecipientCreate] = Field(..., min_length=1)


class JobResponse(BaseModel):
    job_id: int
    status: str
    total: int