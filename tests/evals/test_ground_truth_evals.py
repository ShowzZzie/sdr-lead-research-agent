from evals.golden_profiles import MONDAY_FACTS, ZAPIER_FACTS, STRIPE_FACTS
from lra.agent import main
from lra.database import get_profile_by_domain, create_db_and_tables
import json

def get_nested_value(data: dict, path: str):
    parts = path.split(".")
    current = data
    for part in parts:
        current = current[part]
    return current

def run_eval(domain: str, facts: list, use_cache: bool = True) -> tuple[int, int]:
    if use_cache:
        create_db_and_tables()
        profile_row = get_profile_by_domain(domain)
        if profile_row is None:
            agent_result = main(domain)
            agent_result_dict = agent_result.model_dump()
        else:
            agent_result_dict = json.loads(profile_row.profile_json)
    else:
        agent_result = main(domain)
        agent_result_dict = agent_result.model_dump()
    
    correct = 0
    for path, expected in facts:
        actual = get_nested_value(agent_result_dict, path)
        if actual == expected:
            correct += 1
    return correct, len(facts)

def test_monday():
    correct, total = run_eval("monday.com", MONDAY_FACTS)
    print(f"monday.com: {correct}/{total}")
    assert correct == total

def test_zapier():
    correct, total = run_eval("zapier.com", ZAPIER_FACTS)
    print(f"zapier.com: {correct}/{total}")
    assert correct == total

def test_stripe():
    correct, total = run_eval("stripe.com", STRIPE_FACTS)
    print(f"stripe.com: {correct}/{total}")
    assert correct == total