from rag.retriever import Retriever
from services.ai_manager import AIManager


class RAGService:

    def __init__(self):
        self.ai_manager = AIManager()

    def answer_with_documents(self, question, model="auto"):

        search_result = Retriever.search(question)

        if not search_result:
            return None

        if search_result["score"] > 1.2:
            return None

        chunks = search_result["chunks"]

        context = "\n\n".join(chunks)

        prompt = f"""
Use ONLY the context below to answer the question.

If the answer is not present in the context, say:
"I could not find that information in the uploaded documents."

Context:
{context}

Question:
{question}
"""

        response = self.ai_manager.generate(
            prompt=prompt,
            model=model
        )

        return response