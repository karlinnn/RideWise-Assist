from src.llm import chat

if __name__ == "__main__":
    print("Testing LLM credentials...")
    res = chat([{"role": "user", "content": "Say hello!"}])
    if isinstance(res, dict) and "error" in res:
        print("Error:", res["error"])
        exit(1)
    else:
        print("Success! LLM responded:", res.content)
