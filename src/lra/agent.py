from typing import cast
from anthropic.types import MessageParam, ToolParam
from lra.schemas import LeadProfile
from lra.llm import LLMClient
from lra.config import anthropic_api_key as api_key, claude_model as model
from lra.tools.fetch_homepage import FETCH_HOMEPAGE_TOOL, fetch_homepage
from lra.tools.extract_tech_stack import EXTRACT_TECH_STACK, extract_tech_stack
from lra.database import create_db_and_tables, store_profile, get_profile_by_domain
import json
import httpx
from bs4 import BeautifulSoup
import logging
import asyncio
from langfuse import get_client

logger = logging.getLogger(__name__)
langfuse = get_client()

WEB_SEARCH_TOOL = {"type": "web_search_20250305", "name": "web_search", "max_uses": 1}

tools: list[ToolParam] = cast(list[ToolParam], [FETCH_HOMEPAGE_TOOL, EXTRACT_TECH_STACK, WEB_SEARCH_TOOL])

async def run(domain: str, client: LLMClient, httpx_client: httpx.AsyncClient, job_id: int | None = None) -> LeadProfile:    
    with langfuse.start_as_current_observation(as_type="agent", name=f"main-sdr-{domain}", metadata={"domain": domain}):
        messages: list[MessageParam] = []
        first_message = {
            "role": "user",
            "content": f"Research the company at {domain} thoroughly. Use fetch_homepage to get their homepage, extract_tech_stack to detect their technology, and web_search to find recent news, funding events, and leadership information that may not be on the homepage. Build the most complete profile possible."
        }
        messages.append(cast(MessageParam, first_message))

        iterations = 0
        input_tokens_track = 0
        output_tokens_track = 0

        fh_result = None

        while True:
            if iterations >= 15:
                raise RuntimeError(f"Agent loop exceeded maximum iterations (15). Iteration ran {iterations}")
            iterations += 1

            response = await client.call(messages, tools)
            with langfuse.start_as_current_observation(
                as_type="generation",
                name="llm-call",
                model=model,
                input=messages,
                output=response.content,
                usage_details={"input": response.usage.input_tokens, "output": response.usage.output_tokens}
            ):
                pass
            
            messages.append(cast(MessageParam, {
                "role": "assistant",
                "content": response.content
            }))
            input_tokens_track += response.usage.input_tokens
            output_tokens_track += response.usage.output_tokens
            
            logger.info("iteration complete", extra={"iteration": iterations, "stop_reason": response.stop_reason})
            if response.stop_reason == "end_turn":
                for block in response.content:
                    if block.type == "server_tool_use":
                        logger.info("server tool called", extra={"tool": block.name})
                    if block.type == "web_search_tool_result":
                        logger.info("web search results received")
                messages.append(cast(MessageParam, {
                    "role": "user",
                    "content": f"Based on your research, return a JSON object matching this schema exactly:\n{json.dumps(LeadProfile.model_json_schema(), indent=2)}\n\nReturn only the JSON object, no other text."
                }))
                final_response, input_tokens_final_call_only, output_tokens_final_call_only = await client.final(
                    messages=messages,
                    output_model=LeadProfile
                )
                with langfuse.start_as_current_observation(
                    as_type="generation",
                    name="llm-final",
                    model=model,
                    input=messages,
                    output=final_response,
                    usage_details={"input": input_tokens_final_call_only, "output": output_tokens_final_call_only}
                ):
                    pass
                input_tokens_track += input_tokens_final_call_only
                output_tokens_track += output_tokens_final_call_only
                assert isinstance(final_response, LeadProfile)
                store_profile(domain=domain, profile=final_response, input_tokens=input_tokens_track, output_tokens=output_tokens_track, job_id=job_id)
                logger.info("run complete", extra={
                    "domain": domain,
                    "input_tokens": input_tokens_track,
                    "output_tokens": output_tokens_track
                })
                langfuse.flush()
                return final_response


            # TODO V2.1: add asyncio.gather() for parallel tool dispatch
            # when tools in the same iteration are independent of each other
            # currently fetch_homepage and extract_tech_stack run in separate iterations
            if response.stop_reason == "tool_use":
                for block in response.content:
                    if block.type == "tool_use" and block.name == "fetch_homepage":
                        logger.info("tool usage", extra={"tool": block.name, "domain": domain})
                        with langfuse.start_as_current_observation(as_type="span", name="fetch_homepage", input={"domain": str(block.input["domain"])}) as span:
                            fh_result = await fetch_homepage(str(block.input["domain"]), httpx_client)
                            span.update(output={"length": len(fh_result)})
                        assert fh_result is not None
                        soup = BeautifulSoup(fh_result, 'html.parser')
                        messages.append(cast(MessageParam, {
                            "role": "user",
                            "content": [{"type": "tool_result", "tool_use_id": block.id, "content": soup.get_text(separator="\n", strip=True)[:3000]}]
                        }))
                    if block.type == "tool_use" and block.name == "extract_tech_stack":
                        logger.info("tool_usage", extra={"tool": block.name, "fh_result_available": fh_result is not None})
                        assert fh_result is not None
                        with langfuse.start_as_current_observation(as_type="span", name="extract_tech_stack", input={"html_length": len(fh_result)}) as span:
                            ets_result = extract_tech_stack(fh_result)
                            span.update(output={"tools_found": ets_result})
                        messages.append(cast(MessageParam, {
                            "role": "user",
                            "content": [{"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(ets_result)}]
                        }))


async def main(domain: str, job_id: int | None = None, use_cache: bool = False) -> LeadProfile:
    create_db_and_tables()

    if use_cache:
        profile_row = get_profile_by_domain(domain)
        if profile_row is not None:
            return LeadProfile.model_validate_json(profile_row.profile_json)

    assert api_key is not None
    client = LLMClient(
        api_key=api_key,
        model=model
    )

    async with httpx.AsyncClient(timeout=10.0) as httpx_client:
        result = await run(domain=domain, client=client, httpx_client=httpx_client, job_id=job_id)
        return result


if __name__ == "__main__":
    asyncio.run(main("monday.com"))