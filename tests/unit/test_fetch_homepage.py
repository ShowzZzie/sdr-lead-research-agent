from lra.tools.fetch_homepage import fetch_homepage
import httpx
import asyncio

def test_fetch_homepage_returns_text():
    async def _inner():
        async with httpx.AsyncClient(timeout=10.0) as client:
            result = await fetch_homepage("stripe.com", client)
            assert isinstance(result, str)
            assert len(result) > 0
            assert "<html" in result.lower()
    asyncio.run(_inner())