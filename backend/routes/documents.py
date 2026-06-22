import os
from flask import BluePrint, request, jsonify
from supabase import create_client
from dotenv import load_dotenv

from app.rag.loader import PDFLoader
from app.rag.chunker import Chunker
from app.rag.vecctor_store import VectorStore

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

vector_store = VectorStore()

document_bp = BluePrint("documents", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@document_bp.route("/document/upload", methods=["POST"])
def upload_document():

    file = request.files.get("file")

    if not file:
        return jsonify({
            "error": "No file uploaded."
        }), 400
    
    file_name = file.filename

    local_path = os.path.join(
        UPLOAD_FOLDER,
        file_name
    )
    file.save(local_path)

    supabase.storage \
        .from_("documents") \
        .upload(file_name, file.read())
    
    file_url = supabase.storage \
        .from_("documents") \
        .get_public_url(file_name)

    response = supabase.table("documents").insert({
        "name": file_name,
        "file_url": file_url
    }) \
    .execute()

    document_id = response.data[0]["id"]

    text =  PDFLoader.load(local_path)

    chunks = Chunker.split(text)

    vector_store.add_document(
        doc_id=document_id,
        chunks=chunks
    )
    
    return jsonify({
        "message": "Document uploaded and indexed",
        "document_id": document_id,
        "chunks": len(chunks)
    })