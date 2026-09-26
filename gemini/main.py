import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from google import genai
from google.genai.errors import ServerError

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

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
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=message,
        )
        return jsonify({"reply": response.text or ""})
    except ServerError:
        return jsonify({"error": "Gemini is temporarily unavailable."}), 503

if __name__ == "__main__":
    app.run()