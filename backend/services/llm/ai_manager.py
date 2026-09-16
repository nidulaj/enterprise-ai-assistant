from services.llm.gemini_provider import GeminiProvider
from services.llm.groq_provider import GroqProvider

class AIManager:
    def __init__(self):
        self.gemini = GeminiProvider()
        self.groq = GroqProvider()

    def generate(self, prompt: str, model: str = "auto"):
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

    def generate_stream(self, prompt: str, model: str = "auto"):
        """Yields dicts: {
            "token": "...",
            "model": "gemini" | "groq"
        }"""
        if model == "gemini":
            for chunk in self.gemini.generate_stream(prompt):
                if chunk.startswith("Gemini Error"):
                    raise Exception(chunk)
                yield {"token": chunk, "model": "gemini"}
            return

        if model == "groq":
            for chunk in self.groq.generate_stream(prompt):
                if chunk.startswith("Groq Error"):
                    raise Exception(chunk)
                yield {"token": chunk, "model": "groq"}
            return

        # Auto mode: try gemini first with groq fallback
        try:
            gemini_gen = self.gemini.generate_stream(prompt)
            first_chunk = next(gemini_gen, None)
            if first_chunk is not None and not first_chunk.startswith("Gemini Error"):
                yield {"token": first_chunk, "model": "gemini"}
                for chunk in gemini_gen:
                    if chunk.startswith("Gemini Error"):
                        break
                    yield {"token": chunk, "model": "gemini"}
                return
        except Exception:
            pass

        try:
            groq_gen = self.groq.generate_stream(prompt)
            first_chunk = next(groq_gen, None)
            if first_chunk is not None and not first_chunk.startswith("Groq Error"):
                yield {"token": first_chunk, "model": "groq"}
                for chunk in groq_gen:
                    if chunk.startswith("Groq Error"):
                        break
                    yield {"token": chunk, "model": "groq"}
                return
        except Exception:
            pass

        raise Exception("All AI providers failed streaming")

