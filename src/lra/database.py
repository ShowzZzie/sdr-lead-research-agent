from datetime import datetime
from sqlmodel import Field, SQLModel, create_engine, Session, select, col
from lra.config import db_path
from lra.schemas import LeadProfile, JobStatus

class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    domain: str
    status: JobStatus
    created_at: datetime = Field(default_factory=datetime.now)
    error: str | None

class Profile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    domain: str
    created_at: datetime = Field(default_factory=datetime.now)
    profile_json: str
    input_tokens: int
    output_tokens: int
    job_id: int | None = Field(default=None, foreign_key="job.id")

engine = create_engine(db_path)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def store_profile(domain: str, profile: LeadProfile, input_tokens: int, output_tokens: int, job_id: int | None) -> None:
    with Session(engine) as session:
        db_profile = Profile(domain=domain, profile_json=profile.model_dump_json(), input_tokens=input_tokens, output_tokens=output_tokens, job_id=job_id)
        session.add(db_profile)
        session.commit()

def create_job(domain: str) -> Job:
    with Session(engine) as session:
        new_job = Job(domain=domain, status=JobStatus.PENDING)
        session.add(new_job)
        session.commit()
        session.refresh(new_job)
        assert new_job.id is not None
        return new_job

def update_job_status(job_id: int, status: JobStatus, error: str | None = None) -> None:
    with Session(engine) as session:
        stmnt = select(Job).where(Job.id==job_id)
        job = session.exec(stmnt).first()
        if job is None:
            raise ValueError(f"Job {job_id} was not found")
        job.status = status
        job.error = error
        session.add(job)
        session.commit()

def get_job(job_id: int) -> Job | None:
    with Session(engine) as session:
        stmnt = select(Job).where(Job.id==job_id)
        job = session.exec(stmnt).first()
        return job

def get_profile_by_domain(domain: str) -> Profile | None:
    with Session(engine) as session:
        stmnt = select(Profile).where(Profile.domain==domain).order_by(col(Profile.created_at).desc())
        profile = session.exec(stmnt).first()
        return profile