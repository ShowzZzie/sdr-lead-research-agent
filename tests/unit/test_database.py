from sqlmodel import create_engine, SQLModel
from lra import database
from lra.schemas import JobStatus
import pytest
from sqlalchemy.pool import StaticPool

@pytest.fixture
def db(monkeypatch):
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(test_engine)
    monkeypatch.setattr(database, "engine", test_engine)
    

def test_create_job(db):
    job = database.create_job("stripe.com")
    assert job.domain == "stripe.com"

def test_store_profile(db, fake_profile):
    database.store_profile("foobar.baz", fake_profile, 12, 13, 2)
    result = database.get_profile_by_domain("foobar.baz")
    assert result.domain == "foobar.baz"
    assert result.input_tokens == 12
    assert result.output_tokens == 13
    assert result.job_id == 2

def test_update_job_status(db):
    new_job = database.create_job("foobar.baz")
    assert new_job.status == JobStatus.PENDING

    database.update_job_status(new_job.id, JobStatus.RUNNING)
    updated = database.get_job(new_job.id)
    assert updated is not None
    assert updated.status == JobStatus.RUNNING

def test_get_job(db):
    new_job = database.create_job("foobar.baz")
    found = database.get_job(new_job.id)
    assert found is not None
    assert isinstance(found, database.Job)
    assert found.domain == "foobar.baz"

def test_get_profile_by_domain(db, fake_profile):
    database.store_profile("foobar.baz", fake_profile, 11, 22, 33)
    result = database.get_profile_by_domain("foobar.baz")
    assert result is not None
    assert result.domain == "foobar.baz"
    assert result.input_tokens == 11
    assert result.output_tokens == 22
    assert result.job_id == 33