from mcp.server.fastmcp import FastMCP
from lra.agent import main

mcp = FastMCP("SDR Lead Research Agent")

@mcp.tool()
async def research_company(domain: str) -> str:
    """Research a B2B company by domain. Returns a structured JSON profile including company details, people, tech signals, funding events, and news."""
    profile = await main(domain)
    return profile.model_dump_json()

def serve() -> None:
    mcp.run()

if __name__ == "__main__":
    serve()