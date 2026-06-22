import os
import uuid

from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from supabase import create_client

from rag.loader import PDFLoader
from rag.chunker import Chunker
from rag.vector_store import VectorStore

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL or SUPABASE_KEY missing from .env"
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

vector_store = VectorStore()

document_bp = Blueprint("documents",  __name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


@document_bp.route("/documents/upload", methods=["POST"])

def upload_document():

    local_path = None

    try:

        file = request.files.get("file")

        if not file:
            return jsonify({
                "error": "No file uploaded."
            }), 400

        if file.filename == "":
            return jsonify({
                "error": "No file selected."
            }), 400

        if not file.filename.lower().endswith(".pdf"):
            return jsonify({
                "error": "Only PDF files are allowed."
            }), 400

        unique_filename = (
            f"{uuid.uuid4()}_{file.filename}"
        )

        local_path = os.path.join(
            UPLOAD_FOLDER,
            unique_filename
        )

        file.save(local_path)

        with open(local_path, "rb") as pdf_file:

            supabase.storage \
                .from_("documents") \
                .upload(
                    path=unique_filename,
                    file=pdf_file
                )

        file_url = (
            supabase.storage
            .from_("documents")
            .get_public_url(unique_filename)
        )

        response = (
            supabase
            .table("documents")
            .insert({
                "name": file.filename,
                "file_url": file_url
            })
            .execute()
        )

        if not response.data:
            return jsonify({
                "error": "Failed to save metadata."
            }), 500

        document_id = response.data[0]["id"]

        text = PDFLoader.load(local_path)

        if not text.strip():
            return jsonify({
                "error": "No text found in PDF."
            }), 400

        chunks = Chunker.split(text)

        if not chunks:
            return jsonify({
                "error": "No chunks generated."
            }), 400

        inserted_count = vector_store.add_document(
            doc_id=document_id,
            chunks=chunks
        )

        if inserted_count == 0:
            return jsonify({
                "error": "Failed to index document."
            }), 500

        print(
            f"Indexed {len(chunks)} chunks "
            f"for document {document_id}"
        )

        return jsonify({
            "message": "Document uploaded and indexed successfully.",
            "document_id": document_id,
            "chunks": len(chunks),
            "file_url": file_url
        }), 200

    except Exception as e:

        print("UPLOAD ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if (
            local_path and
            os.path.exists(local_path)
        ):
            os.remove(local_path)