import os
from flask import BluePrint, request, jsonify
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

document_bp = BluePrint("documents", __name__)

@document_bp.route("/document/upload", methods=["POST"])
def upload_document():

    file = request.files.get("file")

    if not file:
        return jsonify({
            "error": "No file uploaded."
        }), 400
    
    file_name = file.filename

    supabase.storage \
        .from_("documents") \
        .upload(file_name, file.read())
    
    file_url = supabase.storage \
        .from_("documents") \
        .get_public_url(file_name)

    supabase.table("documents").insert({
        "name": file_name,
        "file_url": file_url
    })
    
    return jsonify({
        "Message": "File uploaded successfully."
    })