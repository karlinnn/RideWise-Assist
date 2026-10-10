import time
from openai import OpenAI
from src.config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL

def get_client():
    return OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY, timeout=30.0)

def chat(messages, tools=None):
    client = get_client()
    for attempt in range(2):
        try:
            kwargs = {"model": LLM_MODEL, "messages": messages}
            if tools:
                kwargs["tools"] = tools
            completion = client.chat.completions.create(**kwargs)
            return completion.choices[0].message
        except Exception:
            if attempt == 1:
                return {"error": "Failed to communicate with LLM"}
            time.sleep(1)
