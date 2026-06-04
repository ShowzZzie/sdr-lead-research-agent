from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from lra.database import create_db_and_tables, create_job, update_job_status, get_job, get_profile_by_domain
from lra.agent import main
from lra.schemas import JobStatus
from typing import Any
from contextlib import asynccontextmanager
import json
from collections.abc import AsyncGenerator

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

class RequestSearch(BaseModel):
    domain: str
    
def run_research_job(domain: str, job_id: int) -> None:
    update_job_status(job_id, JobStatus.RUNNING)
    try:
        main(domain, job_id)
        update_job_status(job_id, JobStatus.COMPLETED)
    except Exception as e:
        update_job_status(job_id, JobStatus.FAILED, error=str(e))

@app.post("/research")
def post_research(request: RequestSearch, background_tasks: BackgroundTasks) -> dict[str, Any]:
    job = create_job(request.domain)
    assert job.id is not None
    background_tasks.add_task(run_research_job, job.domain, job.id)
    return {"message": "job_created", "job_id": job.id, "status": job.status}

@app.get("/research/{job_id}")
def get_research(job_id: int) -> dict[str, Any]:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found, id: {job_id}")
    
    if job.status == JobStatus.COMPLETED:
        profile = get_profile_by_domain(job.domain)
        assert profile is not None
        return {"status": job.status, "profile": json.loads(profile.profile_json)}
    return {"status": job.status}

@app.get("/profiles/{domain}")
def get_profile(domain: str) -> dict[str, Any]:
    profile = get_profile_by_domain(domain)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Can't find a profile for domain: {domain}")
    return {"profile": json.loads(profile.profile_json)}