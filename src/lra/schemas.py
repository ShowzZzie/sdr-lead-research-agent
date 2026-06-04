from datetime import datetime
from pydantic import AnyUrl, BaseModel
from enum import Enum

class Source(BaseModel):
    url: AnyUrl
    name: str
    date_retrieved: datetime

class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class FundingEvent(BaseModel):
    round: str | None = None
    date: datetime
    amount_raised: float | None = None
    investors: list[str]
    source: Source

class Person(BaseModel):
    name: str
    email: str | None = None
    role: str
    phone_number: str | None = None # for country prefix, the '+'
    source: Source | None = None

class TechSignal(BaseModel):
    tool: str
    source: Source
    confidence: Confidence | None = None

class FitSignal(BaseModel):
    reason: str
    confidence: Confidence
    source: Source

class NewsItem(BaseModel):
    text: str
    date_created: datetime
    source: Source

class Company(BaseModel):
    name: str
    website: AnyUrl | None = None
    stock_symbol: str | None = None
    category: str
    description: str
    employees_amount: int | None = None
    employees_amount_confidence: Confidence | None = None
    yoy_growth: float | None = None
    yoy_growth_confidence: Confidence | None = None
    sources: list[Source]

class LeadProfile(BaseModel):
    person: list[Person] = []
    company: Company
    tech_signal: list[TechSignal] = []
    funding_events: list[FundingEvent] = []
    fit_signal: list[FitSignal] = []
    news_items: list[NewsItem] = []