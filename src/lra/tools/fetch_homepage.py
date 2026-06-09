import httpx

FETCH_HOMEPAGE_TOOL = {
        "name": "fetch_homepage",
        "description": "Retrieve the domain of home page for the given company. Accepted output is: domain.tld",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Provide the website URL of the company, for which homepage URL should be fetched"
                }
            },
            "required": ["domain"]
        }
    }


async def fetch_homepage(domain: str, client: httpx.AsyncClient) -> str:
    try:
        response = await client.get(f"https://{domain}", follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise RuntimeError(f"failed fetching for {domain}: {e}") from e
        
    return response.text