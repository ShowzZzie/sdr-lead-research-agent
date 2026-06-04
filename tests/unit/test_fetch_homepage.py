from lra.tools.fetch_homepage import fetch_homepage
import httpx

def test_fetch_homepage_returns_text():
    with httpx.Client(timeout=10.0) as client:
        result = fetch_homepage("stripe.com", client)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "<html" in result.lower()