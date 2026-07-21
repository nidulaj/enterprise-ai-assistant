import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqProvider:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in the environment variables.")
        
        self.client = Groq(api_key=api_key)

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=2048
            )

            return response.choices[0].message.content
        
        except Exception as e:
            return f"Groq Error: {str(e)}"
