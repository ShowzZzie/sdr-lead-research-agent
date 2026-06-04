import pytest
from lra.schemas import Company, LeadProfile

@pytest.fixture
def fake_profile():
    company = Company(
        name="Test Co",
        category="Test",
        description="Test description",
        sources=[]
    )
    return LeadProfile(company=company)