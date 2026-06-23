import os
import uuid
import traceback

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

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

user = supabase.auth.get_user()
print("user:", user)

vector_store = VectorStore()

document_bp = Blueprint(
    "documents",
    __name__
)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


@document_bp.route("/documents/upload", methods=["POST"])
def upload_document():

    local_path = None

    try:

        print("\n========== DOCUMENT UPLOAD START ==========")

        print("REQUEST FILES:", request.files)
        print("REQUEST FORM:", request.form)

        file = request.files.get("file")

        print("FILE OBJECT:", file)

        if file:
            print("FILENAME:", file.filename)

        if not file:
            print("ERROR: No file uploaded")
            return jsonify({
                "error": "No file uploaded."
            }), 400

        if file.filename == "":
            print("ERROR: No file selected")
            return jsonify({
                "error": "No file selected."
            }), 400

        if not file.filename.lower().endswith(".pdf"):
            print("ERROR: Invalid file type")
            return jsonify({
                "error": "Only PDF files are allowed."
            }), 400

        unique_filename = (
            f"{uuid.uuid4()}_{file.filename}"
        )

        print("UNIQUE FILENAME:", unique_filename)

        local_path = os.path.join(
            UPLOAD_FOLDER,
            unique_filename
        )

        print("LOCAL PATH:", local_path)

        file.save(local_path)

        print("PDF SAVED LOCALLY")

        # --------------------------------------------------
        # SUPABASE STORAGE UPLOAD
        # --------------------------------------------------

        print("\n----- SUPABASE UPLOAD START -----")

        try:

            with open(local_path, "rb") as pdf_file:

                upload_response = (
                    supabase.storage
                    .from_("documents")
                    .upload(
                        path=unique_filename,
                        file=pdf_file
                    )
                )

            print("UPLOAD SUCCESS")
            print("UPLOAD RESPONSE TYPE:", type(upload_response))
            print("UPLOAD RESPONSE:", upload_response)

        except Exception as upload_error:

            print("UPLOAD FAILED")
            print("ERROR TYPE:", type(upload_error))
            print("ERROR:", str(upload_error))
            traceback.print_exc()

            raise

        print("----- SUPABASE UPLOAD END -----\n")

        # --------------------------------------------------
        # GET PUBLIC URL
        # --------------------------------------------------

        print("GENERATING FILE URL...")

        try:

            file_url = (
                supabase.storage
                .from_("documents")
                .get_public_url(unique_filename)
            )

            print("FILE URL TYPE:", type(file_url))
            print("FILE URL:", file_url)

        except Exception as url_error:

            print("GET PUBLIC URL FAILED")
            print("ERROR TYPE:", type(url_error))
            print("ERROR:", str(url_error))
            traceback.print_exc()

            raise

        # --------------------------------------------------
        # DATABASE INSERT
        # --------------------------------------------------

        print("\nINSERTING DOCUMENT METADATA...")

        try:

            response = (
                supabase
                .table("documents")
                .insert({
                    "name": file.filename,
                    "file_url": file_url
                })
                .execute()
            )

            print("DB RESPONSE TYPE:", type(response))
            print("DB RESPONSE:", response)

        except Exception as db_error:

            print("DATABASE INSERT FAILED")
            print("ERROR TYPE:", type(db_error))
            print("ERROR:", str(db_error))
            traceback.print_exc()

            raise

        if not response.data:
            print("ERROR: No data returned from insert")

            return jsonify({
                "error": "Failed to save metadata."
            }), 500

        document_id = response.data[0]["id"]

        print("DOCUMENT ID:", document_id)

        # --------------------------------------------------
        # PDF EXTRACTION
        # --------------------------------------------------

        print("\nEXTRACTING PDF TEXT...")

        text = PDFLoader.load(local_path)

        print("TEXT LENGTH:", len(text))

        if len(text) > 0:
            print("TEXT PREVIEW:")
            print(text[:300])

        if not text.strip():

            print("ERROR: No text extracted")

            return jsonify({
                "error": "No text found in PDF."
            }), 400

        # --------------------------------------------------
        # CHUNKING
        # --------------------------------------------------

        print("\nCREATING CHUNKS...")

        chunks = Chunker.split(text)

        print("CHUNK COUNT:", len(chunks))

        if chunks:
            print("FIRST CHUNK:")
            print(chunks[0][:300])

        if not chunks:

            print("ERROR: No chunks generated")

            return jsonify({
                "error": "No chunks generated."
            }), 400

        # --------------------------------------------------
        # CHROMADB INDEXING
        # --------------------------------------------------

        print("\nINDEXING TO CHROMADB...")

        inserted_count = vector_store.add_document(
            doc_id=document_id,
            chunks=chunks
        )

        print("INSERTED COUNT:", inserted_count)

        if inserted_count == 0:

            print("ERROR: ChromaDB indexing failed")

            return jsonify({
                "error": "Failed to index document."
            }), 500

        print(
            f"SUCCESS: Indexed {len(chunks)} chunks "
            f"for document {document_id}"
        )

        print("========== DOCUMENT UPLOAD END ==========\n")

        return jsonify({
            "message": "Document uploaded and indexed successfully.",
            "document_id": document_id,
            "chunks": len(chunks),
            "file_url": file_url
        }), 200

    except Exception as e:

        print("\n========== EXCEPTION ==========")
        print("ERROR TYPE:", type(e))
        print("ERROR:", str(e))
        traceback.print_exc()
        print("================================\n")

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if (
            local_path and
            os.path.exists(local_path)
        ):
            print("DELETING TEMP FILE:", local_path)
            os.remove(local_path)