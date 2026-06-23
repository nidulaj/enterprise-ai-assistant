from rag.embeddings import EmbeddingService
from rag.vector_store import VectorStore


class Retriever:
    
    vector_store = VectorStore()

    @staticmethod
    def search(question):

        embedding = EmbeddingService.embed(question)

        results = Retriever.vector_store.search(
            query=question,
            n_results=5
        )

        documents = results.get("documents", [])
        distances = results.get("distances", [])

        if not documents or not documents[0]:
            return None

        score = 999

        if distances and distances[0]:
            score = distances[0][0]

        return {
            "chunks": documents[0],
            "score": score
        }