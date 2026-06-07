from enum import Enum
from pydantic import BaseModel


RUBRIC={
    "fit_signal": "Is each fit signal plausible based on publicly known information about this company? Answer with either: YES / PARTIALLY / NO",
    "company_description": "Does this description accurately represent what the company does? Answer with either: YES / PARTIALLY / NO",
    "tech_signal": "Is the confidence level appropriate given that this signal was detected from HTML patterns? Answer with either: YES / PARTIALLY / NO"
}

class Score(str, Enum):
    YES = "yes"
    PARTIALLY = "partially"
    NO = "no"

class JudgeScore(BaseModel):
    name: str
    score: Score
    reasoning: str