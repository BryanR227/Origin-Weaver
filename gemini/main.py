import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from google import genai
from google.genai.errors import ServerError
from gemini.agent import Agent

agent = Agent()

load_dotenv()

app = Flask(__name__, static_folder="../frontend", static_url_path="")

@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        reply = Agent.respond(message)
        return jsonify({"reply": reply})

    except ServerError:
        return jsonify({
            "error": "Gemini is temporarily unavailable."
        }), 503
    
if __name__ == "__main__":
    app.run()