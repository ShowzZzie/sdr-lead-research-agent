from src.lra.tools.extract_tech_stack import extract_tech_stack

def test_extract_tech_stack_returns_list():
    result = extract_tech_stack("hotjar.com")

    assert isinstance(result, list)
    assert all(isinstance(item, str) for item in result)
    assert len(result) == 1
    assert result == ["Hotjar"]


def test_extract_tech_stack_null_input():
    result = extract_tech_stack("")
    
    assert isinstance(result, list)
    assert len(result) == 0
    assert result == []