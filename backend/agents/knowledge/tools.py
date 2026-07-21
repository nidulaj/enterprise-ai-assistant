import os
from dotenv import load_dotenv
from supabase import create_client
from rag.retriever import Retriever
from services.rag_service import RAGService

load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

_rag_service = RAGService()

def search_documents(query):
    """
    Search for documents related to the query in the vector store.
    """
    if not query:
        return {"error": "Query is required"}
    
    result = Retriever.search(query)
    if not result:
        return {"chunks": [], "score": 999}
        
    return result

def answer_question(question, model="auto"):
    """
    Answer a question using the documents in the knowledge base.
    """
    if not question:
        return {"response": "Question is required"}
        
    response = _rag_service.answer_with_documents(question, model)
    if not response:
        return {"response": "I could not find that information in the uploaded documents."}
    
    if isinstance(response, dict):
        response = response.get("response", "I could not find that information in the uploaded documents.")
        
    return {"response": response}

def get_documents():
    """
    Get the list of uploaded documents from Supabase.
    """
    if not _supabase:
        return {"error": "Supabase client is not configured"}
        
    try:
        response = (
            _supabase
            .table("documents")
            .select("*")
            .order("uploaded_at", desc=True)
            .execute()
        )
        
        formatted_docs = []
        for doc in response.data:
            formatted_docs.append({
                "id": doc.get("id"),
                "name": doc.get("name"),
                "file_url": doc.get("file_url"),
                "uploaded_at": doc.get("uploaded_at")
            })
        return formatted_docs
    except Exception as e:
        return {"error": str(e)}
