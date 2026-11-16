from flask import Flask
from flask_cors import CORS

from routes.chat import chat_bp
from routes.documents import document_bp
from routes.google_calendar import calendar_bp
from routes.auth import auth_bp

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

app.register_blueprint(auth_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(document_bp)
app.register_blueprint(calendar_bp)

@app.route("/")
def health():
    return {"message": "API running"}

if __name__ == "__main__":
    app.run(debug=True)