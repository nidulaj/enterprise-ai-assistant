import chromadb
from rag.embeddings import EmbeddingService

class VectorStore:
    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="./chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

    def add_document(self, doc_id, chunks):
        for index, chunk in enumerate(chunks):
            embedding = EmbeddingService.embed(chunk)

            self.collection.add(
                ids=[f"{doc_id}_{index}"],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{"document_id": doc_id}]
            )

    def search(self, query, n_results=5):
        query_embedding = EmbeddingService.embed(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return results