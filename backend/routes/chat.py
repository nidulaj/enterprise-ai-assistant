from flask import Blueprint, request, jsonify
from services.ai_manager import AIManager

chat_bp = Blueprint('chat', __name__)
ai_manager = AIManager()

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    
    message = data.get("message", "")
    model = data.get("model", "auto")

    if not message:
        return jsonify({
            "error": "Message is required."
        }), 400
    
    try:
        result = ai_manager.generate(
            prompt=message,
            model=model
        )

        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500