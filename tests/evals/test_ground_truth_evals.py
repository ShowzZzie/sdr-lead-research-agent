import pytest
from evals.golden_profiles import ALL_GOLDEN_PROFILES
from lra.agent import main
from lra.database import get_profile_by_domain, create_db_and_tables
import json
import asyncio

def get_nested_value(data: dict, path: str):
    parts = path.split(".")
    current = data
    for part in parts:
        current = current[part]
    return current

async def run_eval(domain: str, facts: list, use_cache: bool = True) -> tuple[int, int]:
    if use_cache:
        create_db_and_tables()
        profile_row = get_profile_by_domain(domain)
        if profile_row is None:
            agent_result = await main(domain)
            agent_result_dict = agent_result.model_dump()
        else:
            agent_result_dict = json.loads(profile_row.profile_json)
    else:
        agent_result = await main(domain)
        agent_result_dict = agent_result.model_dump()
    
    correct = 0
    for path, expected, operator in facts:
        actual = get_nested_value(agent_result_dict, path)
        if operator=="eq":
            if actual == expected:
                correct += 1
        elif operator=="is_not_none":
            if actual is not None:
                correct+=1
        elif operator=="eq_any":
            if actual in expected:
                correct+=1
    return correct, len(facts)

@pytest.mark.parametrize("domain,facts", ALL_GOLDEN_PROFILES)
def test_golden_profile(domain: str, facts: list[tuple[str, str | list[str], str]]):
    correct, total = asyncio.run(run_eval(domain, facts))
    print(f"{domain}: {correct}/{total}")
    assert correct == total