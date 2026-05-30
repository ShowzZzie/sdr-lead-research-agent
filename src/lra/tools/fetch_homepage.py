import httpx
from bs4 import BeautifulSoup

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


def fetch_homepage(domain: str) -> str:
    with httpx.Client(timeout=10.0) as client:
        try:
            response = client.get(f"https://{domain}", follow_redirects=True)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise RuntimeError(f"failed fetching for {domain}: {e}") from e
        
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator="\n", strip=True)[:3000]