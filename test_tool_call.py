import json
from kiro_proxy.converters import (
    convert_openai_messages_to_kiro,
    convert_kiro_response_to_openai,
    convert_openai_tools_to_kiro,
)

# simulate OpenAI chat completion with tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_price",
            "description": "Get price for product",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {"type": "string"}
                },
                "required": ["sku"]
            }
        }
    }
]
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the price for SKU12345?"},
    {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "id": "call_1",
                "function": {
                    "name": "get_price",
                    "arguments": "{\"sku\": \"SKU12345\"}"
                }
            }
        ]
    }
]
user_content, history, tool_results, kiro_tools = convert_openai_messages_to_kiro(
    messages,
    "gemini-3.1-pro-high",
    tools,
    None
)
print("Kiro payload:")
print(json.dumps({
    "user_content": user_content,
    "history": history,
    "tool_results": tool_results,
    "kiro_tools": kiro_tools
}, indent=2))

# simulate Kiro service response (tool_use)
kiro_resp = {
    "content": ["The price for SKU12345 is $29.99."],
    "tool_uses": [
        {
            "type": "tool_use",
            "id": "call_1",
            "name": "get_price",
            "input": {"sku": "SKU12345"}
        }
    ],
    "stop_reason": "tool_use"
}
openai_resp = convert_kiro_response_to_openai(kiro_resp, "gemini-3.1-pro-high", "msg-001")
print("Converted OpenAI response: ")
print(json.dumps(openai_resp, indent=2))
