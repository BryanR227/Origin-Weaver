import os
import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request as UrlRequest, urlopen

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_from_directory
from google import genai
from google.genai.errors import ServerError
from agent import Agent

load_dotenv()

agent = Agent()

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
        reply = agent.respond(message)
        return jsonify({"reply": reply})

    except ServerError:
        return jsonify({
            "error": "Gemini is temporarily unavailable."
        }), 503

@app.post("/api/speech")
def speech():
    data = request.get_json(silent=True) or {}
    text = data.get("text")

    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Text is required"}), 400

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID")
    if not api_key or not voice_id:
        return jsonify({"error": "Set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID in .env to enable speech."}), 503

    endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{quote(voice_id, safe='')}"
    payload = json.dumps({
        "text": text,
        "model_id": "eleven_multilingual_v2"
    }).encode("utf-8")
    upstream_request = UrlRequest(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "xi-api-key": api_key
        },
        method="POST"
    )

    try:
        with urlopen(upstream_request, timeout=60) as upstream_response:
            audio = upstream_response.read()
    except HTTPError as error:
        app.logger.warning("ElevenLabs returned HTTP %s", error.code)
        return jsonify({"error": "ElevenLabs could not generate speech. Check the API key, voice ID, and account access."}), 502
    except (URLError, TimeoutError):
        app.logger.exception("Could not reach ElevenLabs")
        return jsonify({"error": "Could not reach ElevenLabs. Try again."}), 502

    return Response(audio, mimetype="audio/mpeg", headers={"Cache-Control": "no-store"})
    
if __name__ == "__main__":
    app.run()