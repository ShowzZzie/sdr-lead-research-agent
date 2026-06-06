import datetime
from lra import schemas
import pytest
from pydantic import ValidationError

fake_profile_GOOD = schemas.LeadProfile(
    person=[
        schemas.Person(
            name="John Doe",
            email="randomemail@gmail.com",
            role="CFO",
            phone_number="+123456789",
            source=schemas.Source(
                url="https://www.wikipedia.org",
                name="Wikipedia",
                date_retrieved=datetime.datetime(2026,6,6,16,40,25)
            )
        )
    ], # list[Person]
    company=schemas.Company(
        name="Random Company",
        website="https://www.website.com",
        stock_symbol="FYI",
        category="Testing",
        description="Random Description of this",
        employees_amount=12,
        employees_amount_confidence=schemas.Confidence.HIGH,
        yoy_growth=-5.0,
        yoy_growth_confidence=schemas.Confidence.MEDIUM,
        sources=[schemas.Source(
            url="https://miniclip.com",
            name="Miniclip",
            date_retrieved=datetime.datetime(2014,10,14,15,15,15)
        )]
    ), # Company
    tech_signal=[
        schemas.TechSignal(
            tool="Random Tool 1",
            source=schemas.Source(
                url="https://rand.tech.signal.com/",
                name="RAND TECH SIGNAL",
                date_retrieved=datetime.datetime(1111,11,11,11,11,11)
            ),
            confidence=schemas.Confidence.HIGH
        )
    ], # list[TechSignal]
    funding_events=[
        schemas.FundingEvent(
            round="Series XYZ",
            date=datetime.datetime(2222,12,12,22,22,22),
            amount_raised=313424.56,
            investors=["investor a", "investor b", "investor c"],
            source=schemas.Source(
                url="https://seriesxyz.com",
                name="Series XYZ website",
                date_retrieved=datetime.datetime(1234,8,7,6,5,4)
            )
        )
    ], # list[FundingEvent]
    fit_signal=[
        schemas.FitSignal(
            reason="just because of the test",
            confidence=schemas.Confidence.LOW,
            source=schemas.Source(url="https://random.org",name="Random ORG",date_retrieved=datetime.datetime(3333,11,22,3,4,5))
        )
    ], # list[FitSignal]
    news_items=[
        schemas.NewsItem(
            text="replacement text for some news item article",
            date_created=datetime.datetime(2015,3,13,12,12,12),
            source=schemas.Source(url="https://www.randomnews.com",name="Random News", date_retrieved=datetime.datetime(1993, 11, 13, 17, 17, 17))
        )
    ] # list[NewsItem]
)


def test_valid_profile_passes_validation():
    schemas.LeadProfile.model_validate(fake_profile_GOOD.model_dump())

def test_invalid_profile_raises_validation_error():
    with pytest.raises(ValidationError):
        schemas.LeadProfile(company=None)

def test_invalid_url_raises_validation_error():
    with pytest.raises(ValidationError):
        schemas.Company(website="website.com/pl")