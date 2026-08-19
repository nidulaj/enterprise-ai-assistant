from flask import Blueprint, request, jsonify
import traceback    

from agents.base.router_agent import RouterAgent

chat_bp = Blueprint('chat', __name__)
agent_router = RouterAgent()

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    
    message = data.get("message", "")
    model = data.get("model", "auto")
    print("REQUEST:", data)

    if not message:
        return jsonify({
            "error": "Message is required."
        }), 400
    
    try:
        response = agent_router.route(message=message, model=model)
        
        source = response.source
        response_text = response.response_text
        
        # Map source fields to adapt to the exact frontend contract
        if source == "clickup":
            # Sprint summary maps answer to string, while tasks map to {response, model} dict
            if response.data and "summary" in response.data:
                return jsonify({
                    "source": "clickup",
                    "answer": response_text,
                    "model": response.model
                })
            else:
                return jsonify({
                    "source": "clickup",
                    "answer": {
                        "response": response_text,
                        "model": response.model
                    }
                })
        elif source == "documents":
            return jsonify({
                "source": "documents",
                "answer": response_text
            })
        elif source == "ai":
            return jsonify({
                "source": "ai",
                "answer": response_text,
                "model": response.model
            })
        else:
            # Fallback for calendar or other newly introduced agents
            return jsonify({
                "source": source,
                "answer": {
                    "response": response_text,
                    "model": response.model
                }
            })
        
    except Exception as e:
        print("\n========== ERROR ==========")
        print(type(e))
        print(e)
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500