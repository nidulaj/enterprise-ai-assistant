from rag.retriever import Retriever
from services.llm.ai_manager import AIManager


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

        from agents.knowledge.prompts import RAG_QA_PROMPT
        prompt = RAG_QA_PROMPT.format(context=context, question=question)

        response = self.ai_manager.generate(
            prompt=prompt,
            model=model
        )

        if isinstance(response, dict):
            return response.get("response", "")

        return response