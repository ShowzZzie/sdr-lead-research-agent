from datetime import datetime
from sqlmodel import Field, SQLModel, create_engine, Session
from src.lra.config import db_path
from src.lra.schemas import LeadProfile

class Profile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    domain: str
    created_at: datetime = Field(default_factory=datetime.now)
    profile_json: str
    input_tokens: int
    output_tokens: int

engine = create_engine(db_path)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def store_profile(domain: str, profile: LeadProfile, input_tokens: int, output_tokens: int) -> None:
    with Session(engine) as session:
        db_profile = Profile(domain=domain, profile_json=profile.model_dump_json(), input_tokens=input_tokens, output_tokens=output_tokens)
        session.add(db_profile)
        session.commit()