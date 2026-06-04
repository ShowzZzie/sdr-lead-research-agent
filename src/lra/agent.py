from typing import cast
from anthropic.types import MessageParam, ToolParam
from lra.schemas import LeadProfile
from lra.llm import LLMClient
from lra.config import anthropic_api_key as api_key, claude_model as model
from lra.tools.fetch_homepage import FETCH_HOMEPAGE_TOOL, fetch_homepage
from lra.tools.extract_tech_stack import EXTRACT_TECH_STACK, extract_tech_stack
from lra.database import create_db_and_tables, store_profile
import json
import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

tools: list[ToolParam] = cast(list[ToolParam], [FETCH_HOMEPAGE_TOOL, EXTRACT_TECH_STACK])

def run(domain: str, client: LLMClient, httpx_client: httpx.Client, job_id: int | None = None) -> LeadProfile:    
    messages: list[MessageParam] = []
    first_message = {
        "role": "user",
        "content": f"Research the company at {domain}. Use the fetch_homepage tool to retrieve their homepage content, then analyze it."
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

        response = client.call(messages, tools)
        messages.append(cast(MessageParam, {
            "role": "assistant",
            "content": response.content
        }))
        input_tokens_track += response.usage.input_tokens
        output_tokens_track += response.usage.output_tokens
        
        logger.info("iteration complete", extra={"iteration": iterations, "stop_reason": response.stop_reason})
        if response.stop_reason == "end_turn":
            messages.append(cast(MessageParam, {
                "role": "user",
                "content": f"Based on your research, return a JSON object matching this schema exactly:\n{json.dumps(LeadProfile.model_json_schema(), indent=2)}\n\nReturn only the JSON object, no other text."
            }))
            final_response, input_tokens_final_call_only, output_tokens_final_call_only = client.final(
                messages=messages,
                output_model=LeadProfile
            )
            input_tokens_track += input_tokens_final_call_only
            output_tokens_track += output_tokens_final_call_only
            assert isinstance(final_response, LeadProfile)
            store_profile(domain=domain, profile=final_response, input_tokens=input_tokens_track, output_tokens=output_tokens_track, job_id=job_id)
            logger.info("run complete", extra={
                "domain": domain,
                "input_tokens": input_tokens_track,
                "output_tokens": output_tokens_track
            })
            return final_response

        if response.stop_reason == "tool_use":
            for block in response.content:
                if block.type == "tool_use" and block.name == "fetch_homepage":
                    logger.info("tool usage", extra={"tool": block.name, "domain": domain})
                    fh_result = fetch_homepage(str(block.input["domain"]), httpx_client)
                    assert fh_result is not None
                    soup = BeautifulSoup(fh_result, 'html.parser')
                    messages.append(cast(MessageParam, {
                        "role": "user",
                        "content": [{"type": "tool_result", "tool_use_id": block.id, "content": soup.get_text(separator="\n", strip=True)[:3000]}]
                    }))
                if block.type == "tool_use" and block.name == "extract_tech_stack":
                    logger.info("tool_usage", extra={"tool": block.name, "fh_result_available": fh_result is not None})
                    assert fh_result is not None
                    ets_result = extract_tech_stack(fh_result)
                    messages.append(cast(MessageParam, {
                        "role": "user",
                        "content": [{"type": "tool_result", "tool_use_id": block.id, "content": json.dumps(ets_result)}]
                    }))


def main(domain: str, job_id: int | None = None) -> LeadProfile:
    create_db_and_tables()

    assert api_key is not None
    client = LLMClient(
        api_key=api_key,
        model=model
    )

    with httpx.Client(timeout=10.0) as httpx_client:
        result = run(domain=domain, client=client, httpx_client=httpx_client, job_id=job_id)
        return result


if __name__ == "__main__":
    main("monday.com")