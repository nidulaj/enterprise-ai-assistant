from flask import Blueprint, request

# Create a blueprint named 'chat_bp'
chat_bp = Blueprint('chat', __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    
    # Using .get() is slightly safer in case 'message' is missing from the payload
    return {
        "response": f"You said: {data.get('message', '')}"
    }