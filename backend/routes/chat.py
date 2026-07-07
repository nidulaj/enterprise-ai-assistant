from flask import Blueprint, request, jsonify
import traceback    

from services.ai_manager import AIManager
from services.rag_service import RAGService
from services.intent_service import IntentService
from clickup.clickup_service import ClickUpService

chat_bp = Blueprint('chat', __name__)

ai_manager = AIManager()
rag_service = RAGService()
intent_service = IntentService()
clickup_service = ClickUpService()

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
        intent = intent_service.detect(
            message=message,
            model=model
        )
        
        print("Detected Intent:", intent)
        
        if intent["intent"] == "SHOW_TASKS":
            tasks = clickup_service.get_tasks()

            print("TASKS:", tasks)

            answer = "Your current tasks:\n\n"

            for index, task in enumerate(tasks, start=1):
                answer += (
                    f"{index}. {task['name']} "
                    f"({task['status']})\n"
                )

            print("ANSWER:")
            print(answer)
            
            return jsonify({
                "source": "clickup",
                "answer": {
                    "response": answer,
                    "model": model
                }
            })
            
        elif intent["intent"] == "CREATE_TASK":
            task = clickup_service.create_task(
                title=intent["title"]
            )
            
            return jsonify({
                "source": "clickup",
                "answer": {
                    "response":
                        f"Task created successfully.\n\n"
                        f"Task: {task['name']}\n"
                        f"Status: {task['status']}",
                    "model": model
                }
            })
        
        elif intent["intent"] == "UPDATE_TASK_STATUS":
            task = clickup_service.find_task_by_name(
                intent["task_name"]
            )
            
            if not task:
                return jsonify({
                    "source": "clickup",
                    "answer": {
                        "response": f"Task '{intent['task_name']}' not found.",
                        "model": model
                    }
                })
            
            updated = clickup_service.update_task_status(
                task_id=task["id"],
                status=intent["status"]
            )
            
            return jsonify({
                "source": "clickup",
                "answer": {
                    "response":
                        f"Task updated successfully.\n\n"
                        f"Task: {updated['name']}\n"
                        f"Status: {updated['status']}",
                    "model": model
                }
            })
        
    
        rag_answer = rag_service.answer_with_documents(
            question=message,
            model=model
        )
    
        if rag_answer:
            return jsonify({
                "source": "documents",
                "answer": rag_answer
            })
    
    
        ai_answer  = ai_manager.generate(
            prompt=message,
            model=model
        )

        return jsonify({
            "source": "ai",
            "answer": ai_answer
        })
    
    except Exception as e:
        print("\n========== ERROR ==========")
        print(type(e))
        print(e)
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500