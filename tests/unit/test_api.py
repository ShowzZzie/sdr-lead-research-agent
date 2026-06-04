from fastapi.testclient import TestClient
from sqlmodel import create_engine
from lra import api, database
import pytest
from unittest.mock import patch
from sqlalchemy.pool import StaticPool

@pytest.fixture
def db_and_client(monkeypatch):
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    monkeypatch.setattr(database, "engine", test_engine)
    database.create_db_and_tables()
    
    client = TestClient(api.app)
    yield client


def test_post_research(db_and_client):
    with patch("lra.api.run_research_job"):
        response = db_and_client.post("/research", json={"domain": "zapier.com"})
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert response.json()["status"] == "pending"

def test_get_research(db_and_client):
    with patch("lra.api.run_research_job"):
        response = db_and_client.post("/research", json={"domain": "zapier.com"})
    assert response is not None

    get_research_response = db_and_client.get(f"/research/{response.json()['job_id']}")
    assert get_research_response.json()["status"] is not None
    assert get_research_response.json()["status"] == "pending"

def test_get_research_not_found(db_and_client):
    get_research_response = db_and_client.get("/research/1")
    assert get_research_response.status_code == 404

def test_get_profile(db_and_client, fake_profile):
    database.store_profile("foobar.baz", fake_profile, 11, 22, 33)
    response = db_and_client.get("/profiles/foobar.baz")
    assert response.status_code == 200
    assert response.json()["profile"]["company"]["name"] == "Test Co"
    assert response.json()["profile"]["company"]["category"] == "Test"
    assert response.json()["profile"]["company"]["description"] == "Test description"
    assert isinstance(response.json()["profile"]["company"]["sources"], list)
    assert len(response.json()["profile"]["company"]["sources"]) == 0

def test_get_profile_not_found(db_and_client):
    response = db_and_client.get("/profiles/foobar.baz")
    assert response.status_code == 404