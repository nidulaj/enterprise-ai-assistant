from flask import Blueprint, request, jsonify

from services.ai_manager import AIManager
from services.rag_service import RAGService

chat_bp = Blueprint('chat', __name__)

ai_manager = AIManager()
rag_service = RAGService()

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    
    message = data.get("message", "")
    model = data.get("model", "auto")

    if not message:
        return jsonify({
            "error": "Message is required."
        }), 400
    
    rag_answer = rag_service.answer_with_documents(
        question=message,
        model=model
    )
    
    if rag_answer:
        return jsonify({
            "source": "documents",
            "answer": rag_answer
        })
    
    try:
        ai_answer  = ai_manager.generate(
            prompt=message,
            model=model
        )

        return jsonify({
            "source": "ai",
            "answer": ai_answer
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500