from src.lra.schemas import LeadProfile
from src.lra.llm import LLMClient
from src.lra.config import anthropic_api_key as api_key, claude_model as model
from src.lra.tools.fetch_homepage import FETCH_HOMEPAGE_TOOL, fetch_homepage
import json

tools = [FETCH_HOMEPAGE_TOOL]

def run(domain: str, client: LLMClient):
    messages = [] # initiating the list of messages
    first_message = {
        "role": "user",
        "content": f"Research the company at {domain}. Use the fetch_homepage tool to retrieve their homepage content, then analyze it."
    }
    messages.append(first_message)

    iterations = 0

    while True:
        if iterations >= 15:
            raise RuntimeError(f"Agent loop exceeded maximum iterations (15). Iteration ran {iterations}")
        iterations += 1

        response = client.call(messages, tools)
        messages.append({
            "role": "assistant",
            "content": response.content
        })

        print(f"[iteration {iterations}] stop_reason={response.stop_reason}")
        if response.stop_reason == "end_turn":
            messages.append({
                "role": "user",
                "content": f"Based on your research, return a JSON object matching this schema exactly:\n{json.dumps(LeadProfile.model_json_schema(), indent=2)}\n\nReturn only the JSON object, no other text."
            })
            final_response = client.final(
                messages=messages,
                output_model=LeadProfile
            )
            return final_response

        if response.stop_reason == "tool_use":
            for block in response.content:
                if block.type == "tool_use" and block.name == "fetch_homepage":
                    print(f"[tool] calling fetch_homepage with domain={domain}")
                    fh_result = fetch_homepage(block.input["domain"])
                    messages.append({
                        "role": "user",
                        "content": [{"type": "tool_result", "tool_use_id": block.id, "content": fh_result}]
                    })


def main():
    client = LLMClient(
        api_key=api_key,
        model=model
    )

    result = run(domain="stripe.com", client=client)
    print(result)

    return result


if __name__ == "__main__":
    main()