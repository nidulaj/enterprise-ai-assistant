from providers.gemini_provider import GeminiProvider
from providers.groq_provider import GroqProvider

class AIManaer:
    def __init__(self):
        self.gemini = GeminiProvider()
        self.groq = GroqProvider()

    def generate(self, prompt:str, model: str = "auto"):
        """Returns: {
            "response": "...",
            "model": "gemini"
        }"""

        if model == "gemini":
            response = self.gemini.generate(prompt)

            if response.startswith("Gemini Error"):
                raise Exception(response)
            
            return {
                "response": response,
                "model": "gemini"
            }
        
        if model == "groq":
            response = self.groq.generate(prompt)

            if response.startswith("Groq Error"):
                raise Exception(response)
            
            return {
                "response": response,
                "model": "groq"
            }

        try:
            response = self.gemini.generate(prompt)

            if not response.startswith("Gemini Error"):
                return {
                    "response": response,
                    "model": "gemini"
                }
            
        except Exception:
            pass

        try:
            response = self.groq.generate(prompt)

            if not response.startswith("Groq Error"):
                return {
                    "response": response,
                    "model": "groq"
                }
            
        except Exception:
            pass

        raise Exception("All AI providers failed")