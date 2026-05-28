from src.lra.schemas import LeadProfile
from src.lra.llm import LLMClient
from src.lra.config import anthropic_api_key as api_key, claude_model as model
import json

tools = [
    {
        "name": "fetch_homepage",
        "description": "Retrieve the domain of home page for the given company. Accepted output is: domain.tld",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Provide the name of the company, for which homepage URL should be fetched"
                }
            },
            "required": ["company_name"]
        }
    }
]

def fetch_homepage(domain: str):
    return "stripe.com"

def run(domain: str, client: LLMClient):
    messages = [] # initiating the list of messages
    first_message = {
        "role": "user",
        "content": f"retrieve the domain from the home page of {domain}"
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
                    fh_result = fetch_homepage(block.input["company_name"])
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