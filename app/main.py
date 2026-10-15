from fastapi import FastAPI

from app.database.database import Base, engine
from app.database import models
from app.routers import jobs


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Bulk Certificate Generator",
    description="API for generating certificates in bulk.",
    version="1.0.0"
)


app.include_router(jobs.router)


@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }