import os
import chromadb
from rag.embeddings import EmbeddingService

class VectorStore:
    def __init__(self):
        # Resolve to backend/chroma_db relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chroma_path = os.path.join(base_dir, "chroma_db")

        self.client = chromadb.PersistentClient(
            path=chroma_path
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

    def add_document(self, doc_id, chunks):
        inserted = 0

        for index, chunk in enumerate(chunks):
            embedding = EmbeddingService.embed(chunk)

            self.collection.add(
                ids=[f"{doc_id}_{index}"],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{"document_id": doc_id}]
            )

            inserted += 1

        return inserted

    def search(self, query, n_results=5):
        query_embedding = EmbeddingService.embed(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return results