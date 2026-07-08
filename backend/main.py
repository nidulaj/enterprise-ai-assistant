from flask import Flask
from flask_cors import CORS

from routes.chat import chat_bp
from routes.documents import document_bp
from routes.google_calendar import calendar_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(chat_bp)
app.register_blueprint(document_bp)
app.register_blueprint(calendar_bp)

@app.route("/")
def health():
    return {"message": "API running"}

if __name__ == "__main__":
    app.run(debug=True)