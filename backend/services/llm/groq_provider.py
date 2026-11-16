import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

DEFAULT_GROQ_MODELS = [
    os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b"
]

class GroqProvider:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in the environment variables.")
        
        self.client = Groq(api_key=api_key)
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    def generate(self, prompt: str) -> str:
        last_err = ""
        for model_candidate in DEFAULT_GROQ_MODELS:
            try:
                response = self.client.chat.completions.create(
                    model=model_candidate,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=0.7,
                    max_tokens=2048
                )
                return response.choices[0].message.content
            except Exception as e:
                last_err = str(e)
                continue

        return f"Groq Error: {last_err}"

    def generate_stream(self, prompt: str):
        last_err = ""
        for model_candidate in DEFAULT_GROQ_MODELS:
            try:
                stream = self.client.chat.completions.create(
                    model=model_candidate,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=0.7,
                    max_tokens=2048,
                    stream=True
                )
                emitted = False
                for chunk in stream:
                    delta = chunk.choices[0].delta.content if chunk.choices else None
                    if delta:
                        emitted = True
                        yield delta
                if emitted:
                    return
            except Exception as e:
                last_err = str(e)
                continue

        yield f"Groq Error: {last_err}"
