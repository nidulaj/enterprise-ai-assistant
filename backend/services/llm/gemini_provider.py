import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiProvider:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
        
        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    def generate_stream(self, prompt: str):
        try:
            response = self.model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"Gemini Error: {str(e)}"

