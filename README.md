# Bulk Certificate Generator

A backend REST API for generating participation certificates in bulk from a predefined certificate template.

The application accepts a list of recipients, creates a certificate generation job, processes certificates in the background, tracks the generation progress, handles individual certificate failures without stopping the entire job, and provides an API for downloading generated certificates.

## Features

- Create bulk certificate generation jobs
- Validate recipient information
- Support up to 100 recipients per request
- Generate individual PDF certificates
- Process certificate generation in the background
- Track job progress
- Track individual certificate status
- Handle individual certificate failures independently
- Retrieve generated certificates
- Download generated PDF certificates
- Automated test suite using Pytest
- Interactive API documentation using Swagger/OpenAPI

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| FastAPI | REST API framework |
| Pydantic | Request validation |
| SQLAlchemy | ORM and database interaction |
| SQLite | Relational database |
| ReportLab | PDF certificate generation |
| Pytest | Automated testing |
| Uvicorn | ASGI server |

---

## Project Architecture

```text
                         Client
                           |
                           | HTTP Request
                           v
                    +--------------+
                    |   FastAPI    |
                    |     API      |
                    +------+-------+
                           |
              +------------+------------+
              |                         |
              v                         v
        Job Router              Certificate Router
              |                         |
              |                         |
              v                         v
       Pydantic Validation       File Retrieval
              |
              v
        SQLAlchemy ORM
              |
              v
         SQLite Database
              |
              v
       Background Task
              |
              v
    Certificate Generator
          ReportLab
              |
              v
       Generated PDF Files
```

---

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── jobs.py
│   │   └── certificates.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── job.py
│   │
│   └── services/
│       ├── __init__.py
│       └── certificate_generator.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_jobs.py
│   ├── test_certificate_generator.py
│   └── test_certificates.py
│
├── templates/
│
├── generated_certificates/
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/S-kavinkumar/Bulk-Certificate-Generator-API.git
```

Move into the project directory:

```bash
cd bulk-certificate-generator
```

## 2. Create a virtual environment

On Windows:

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.\venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

# Running the Application

Start the FastAPI development server:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

ReDoc documentation is available at:

```text
http://127.0.0.1:8000/redoc
```

---

# API Endpoints

## 1. Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

---

## 2. Create Certificate Generation Job

```http
POST /api/jobs/
```

This endpoint accepts an event name and a list of recipients.

### Request

```json
{
  "event_name": "Python Workshop",
  "recipients": [
    {
      "name": "Kavin Kumar",
      "email": "kavin@example.com"
    },
    {
      "name": "Rahul Kumar",
      "email": "rahul@example.com"
    },
    {
      "name": "Arun Kumar",
      "email": "arun@example.com"
    }
  ]
}
```

### Response

```json
{
  "job_id": 1,
  "status": "QUEUED",
  "total": 3
}
```

The returned `job_id` can be used to monitor the generation process.

---

# 3. Check Job Progress

```http
GET /api/jobs/{job_id}
```

Example:

```text
GET /api/jobs/1
```

Example response:

```json
{
  "job_id": 1,
  "event_name": "Python Workshop",
  "status": "COMPLETED",
  "total": 3,
  "completed": 3,
  "failed": 0,
  "remaining": 0,
  "certificates": [
    {
      "certificate_id": 1,
      "recipient_name": "Kavin Kumar",
      "recipient_email": "kavin@example.com",
      "status": "COMPLETED",
      "file_path": "generated_certificates/Kavin_Kumar_1.pdf",
      "error_message": null
    }
  ]
}
```

---

# 4. Download Certificate

```http
GET /api/certificates/{certificate_id}/download
```

Example:

```text
GET /api/certificates/1/download
```

If the certificate has been successfully generated, the API returns the PDF file.

---

# Input Validation

The application validates recipient information before creating a generation job.

The following rules are applied:

- At least one recipient is required.
- Maximum of 100 recipients can be submitted in one request.
- Recipient name must contain at least 2 characters.
- Recipient name must contain alphabetic characters.
- Recipient email must have a valid email format.
- Duplicate recipients are rejected.
- Event name cannot be empty.

Invalid requests are rejected with an appropriate HTTP validation response.

---

# Certificate Generation

The application uses **ReportLab** to generate PDF certificates.

Each certificate contains:

- Certificate title
- Recipient name
- Event name
- Certificate ID

Generated certificates are stored in:

```text
generated_certificates/
```

Example:

```text
generated_certificates/
├── Kavin_Kumar_1.pdf
├── Rahul_Kumar_2.pdf
└── Arun_Kumar_3.pdf
```

---

# Background Processing

Certificate generation is performed using FastAPI `BackgroundTasks`.

When a job is submitted, the API creates the job and returns the `job_id` without requiring the client to wait for every certificate to finish.

The job progresses through the following states:

```text
QUEUED
   |
   v
PROCESSING
   |
   +-------------------------+
   |                         |
   v                         v
COMPLETED          COMPLETED_WITH_ERRORS
   |
   v
FAILED
```

Individual certificates follow:

```text
PENDING
   |
   v
PROCESSING
   |
   +----------------+
   |                |
   v                v
COMPLETED         FAILED
```

---

# Failure Handling

Each certificate is processed independently.

If one certificate fails during generation:

1. The certificate is marked as `FAILED`.
2. The error message is stored in the database.
3. The job's failed count is incremented.
4. Processing continues with the remaining certificates.

For example:

```text
Recipient 1 → COMPLETED
Recipient 2 → FAILED
Recipient 3 → COMPLETED
Recipient 4 → COMPLETED
```

The final job status becomes:

```text
COMPLETED_WITH_ERRORS
```

This ensures that one failed certificate does not stop the entire bulk generation process.

---

# Database Design

The application uses SQLite as its relational database.

There are two main tables.

## Jobs Table

The `jobs` table stores information about each bulk generation request.

Important fields include:

```text
id
event_name
status
total_count
completed_count
failed_count
created_at
completed_at
```

## Certificates Table

The `certificates` table stores information about individual certificates.

Important fields include:

```text
id
job_id
recipient_name
recipient_email
status
file_path
error_message
created_at
```

## Relationship

A single job can contain multiple certificates.

```text
Job
 |
 +---- Certificate
 |
 +---- Certificate
 |
 +---- Certificate
 |
 +---- Certificate
```

This represents a one-to-many relationship.

---

# Testing

The project includes automated tests using Pytest.

Run all tests with:

```powershell
pytest -v
```

The test suite covers:

- Job creation
- Empty recipient validation
- Invalid email validation
- Duplicate recipient validation
- Maximum recipient limit
- Job progress retrieval
- Job not found handling
- PDF certificate generation
- Certificate download
- Certificate not found handling
- Individual certificate failure
- Continued processing after a certificate failure

Expected result:

```text
11 passed
```

---

# Design Decisions

## FastAPI

FastAPI was selected because it provides:

- Automatic request validation
- Type hints
- Automatic Swagger/OpenAPI documentation
- Simple REST API development
- Good performance
- Easy integration with Python services

## SQLite

SQLite was selected because this assignment does not require a production-scale database.

It provides a simple relational database without requiring a separate database server.

The application can later be migrated to PostgreSQL by changing the database configuration.

## SQLAlchemy

SQLAlchemy provides ORM-based database access.

It keeps database operations separate from API and business logic.

## Pydantic

Pydantic is used for validating incoming API requests.

This prevents invalid recipient data from entering the certificate generation workflow.

## BackgroundTasks

FastAPI BackgroundTasks is used to process certificate generation after the job request is accepted.

For a larger production system, this could later be replaced by a distributed task queue such as Celery.

## ReportLab

ReportLab was selected because it provides direct PDF generation using Python.

---

# Error Isolation

A key design requirement is that an individual certificate failure must not stop the entire bulk operation.

The implementation handles each certificate inside its own `try/except` block.

Conceptually:

```text
for certificate in certificates:

    try:
        generate certificate
        mark COMPLETED

    except Exception:
        mark FAILED
        continue processing
```

This provides fault isolation between individual certificate generations.

---

# Future Improvements

The current implementation focuses on the requirements of the assignment.

Possible future improvements include:

- PostgreSQL for production environments
- Google Cloud Storage for generated certificates
- Redis and Celery for distributed background processing
- Authentication and authorization
- CSV/Excel recipient upload
- Custom certificate templates
- Certificate email delivery
- Retry failed certificates
- Job cancellation
- Job history
- Admin dashboard
- Docker containerization
- Cloud deployment
- Monitoring and logging

---

# Learning Outcomes

This project provided practical experience with:

- REST API development
- FastAPI
- Pydantic validation
- SQLAlchemy
- Relational database design
- Background processing
- PDF generation
- Error handling
- Automated testing
- API documentation
- Git and GitHub workflow
- Backend application architecture

---

# License

This project was developed as part of a backend development assignment.