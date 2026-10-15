from pydantic import BaseModel, Field, EmailStr, field_validator


class RecipientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Recipient name cannot be empty")

        if not any(char.isalpha() for char in value):
            raise ValueError("Recipient name must contain letters")

        return value


class JobCreate(BaseModel):
    event_name: str = Field(..., min_length=1, max_length=255)
    recipients: list[RecipientCreate] = Field(
        ...,
        min_length=1,
        max_length=100
    )

    @field_validator("event_name")
    @classmethod
    def validate_event_name(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Event name cannot be empty")

        return value

    @field_validator("recipients")
    @classmethod
    def validate_recipients(cls, recipients):
        seen = set()

        for recipient in recipients:
            identifier = (
                recipient.email.lower()
                if recipient.email
                else recipient.name.lower()
            )

            if identifier in seen:
                raise ValueError(
                    f"Duplicate recipient found: {recipient.name}"
                )

            seen.add(identifier)

        return recipients


class JobResponse(BaseModel):
    job_id: int
    status: str
    total: int