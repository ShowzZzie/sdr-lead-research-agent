from evals.rubric import RUBRIC, JudgeScore, Score
from lra.database import get_profile_by_domain, create_db_and_tables
from lra.config import anthropic_api_key as api_key
import anthropic
import json
import pytest

client = anthropic.Anthropic(api_key=api_key)

def judge(domain: str, dimension: str, value: str) -> JudgeScore:
    msg = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""You are evaluating an AI-generated company research profile.
Company: {domain}
Dimension being evaluated: {dimension}
Evaluation question: {RUBRIC[dimension]}
Value to evaluate:
{value}
Return a JSON object matching this schema exactly:
{json.dumps(JudgeScore.model_json_schema(), indent=2)}
Return only the JSON object, no other text."""
        }]
    )
    for block in msg.content:
        if block.type == "text":
            formatted = block.text.replace("```json","").replace("```","")
            return JudgeScore.model_validate_json(formatted)
    raise ValueError("No text block in judge response")

@pytest.mark.parametrize("domain", ["monday.com", "zapier.com", "stripe.com"])
def test_fit_signal(domain):
    create_db_and_tables()
    profile = get_profile_by_domain(domain)
    jsonified = json.loads(profile.profile_json)
    fit_signals = str(jsonified["fit_signal"])
    judge_result = judge(domain, "fit_signal", fit_signals)
    print(judge_result)
    assert judge_result.score != Score.NO

@pytest.mark.parametrize("domain", ["monday.com", "zapier.com", "stripe.com"])
def test_company_description(domain):
    create_db_and_tables()
    profile = get_profile_by_domain(domain)
    jsonified = json.loads(profile.profile_json)
    company_description_str = str(jsonified["company"]["description"])
    judge_result = judge(domain, "company_description", company_description_str)
    print(judge_result)
    assert judge_result.score != Score.NO

@pytest.mark.parametrize("domain", ["monday.com", "zapier.com", "stripe.com"])
def test_tech_signal(domain):
    create_db_and_tables()
    profile = get_profile_by_domain(domain)
    jsonified = json.loads(profile.profile_json)
    tech_signals = str(jsonified["tech_signal"])
    judge_result = judge(domain, "tech_signal", tech_signals)
    print(judge_result)
    assert judge_result.score != Score.NO