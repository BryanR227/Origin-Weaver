import json
import os
import re
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request as UrlRequest
from urllib.request import urlopen

from agent import Agent
from character_sheets import (DEFAULT_PDF_TEMPLATE_PATH, PROJECT_ROOT,
                              generate_character_sheet,
                              get_character_field_keys)
from dotenv import load_dotenv
from flask import (Flask, Response, jsonify, request, send_from_directory,
                   url_for)
from google.genai.errors import ClientError, ServerError
from auth import auth_bp

load_dotenv(override=True)

agent = Agent()
character_output_root = Path(
    os.environ.get("CHARACTER_SHEET_OUTPUT_DIR", PROJECT_ROOT / "instance" / "characters")
).expanduser().resolve()
character_pdf_template = Path(
    os.environ.get("CHARACTER_SHEET_TEMPLATE") or DEFAULT_PDF_TEMPLATE_PATH
).expanduser().resolve()
character_build_pattern = re.compile(
    r"\b(?:build|create|make|generate|design)\b.{0,100}\b(?:character(?: sheet)?|char sheet|class|"
    r"artificer|barbarian|bard|bloodhunter|cleric|druid|fighter|monk|paladin|ranger|rogue|sorcerer|warlock|wizard)\b"
    r"|\b(?:character(?: sheet)?|char sheet|class|artificer|barbarian|bard|bloodhunter|cleric|druid|fighter|"
    r"monk|paladin|ranger|rogue|sorcerer|warlock|wizard)\b.{0,100}\b(?:build|create|make|generate|design)\b",
    re.IGNORECASE | re.DOTALL,
)

app = Flask(__name__, static_folder="../frontend", static_url_path="")
# Needed so Flask can sign session cookies (used for login sessions).
# Set SECRET_KEY in your .env for anything beyond local dev.
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

app.register_blueprint(auth_bp)
@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    if not isinstance(message, str):
        return jsonify({"error": "Message must be text."}), 400
    message = message.strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    generate_sheet = data.get("generate_sheet") is True or bool(character_build_pattern.search(message))
    if generate_sheet:
        if not character_pdf_template.is_file():
            return jsonify({
                "error": "Character sheet PDF template is not configured. Set CHARACTER_SHEET_TEMPLATE to a fillable D&D 5e PDF."
            }), 503

        try:
            reply, field_values = agent.generate_character(message, get_character_field_keys())
            character_id = uuid.uuid4().hex
            generate_character_sheet(
                field_values,
                character_pdf_template,
                character_output_root / character_id,
            )
            return jsonify({
                "reply": reply,
                "pdf_url": url_for("character_sheet", character_id=character_id),
            })
        except ClientError as error:
            if error.code == 429 or error.status == "RESOURCE_EXHAUSTED":
                app.logger.warning("Gemini character request quota exhausted")
                return jsonify({
                    "error": "Gemini's request quota is exhausted. Wait for it to reset or check your Google AI Studio limits and billing."
                }), 429
            app.logger.warning("Gemini rejected the character request with HTTP %s", error.code)
            return jsonify({
                "error": "Gemini rejected the character request. Check the API key and request configuration."
            }), 502
        except ServerError:
            return jsonify({"error": "Gemini is temporarily unavailable."}), 503
        except (ValueError, TypeError) as error:
            app.logger.warning("Could not create character sheet: %s", error)
            return jsonify({"error": "Could not create a valid character sheet. Try refining the character details."}), 502
        except ImportError:
            app.logger.exception("PDF generation dependencies are unavailable")
            return jsonify({"error": "PDF generation dependencies are missing. Install the packages in requirements.txt."}), 503

    try:
        reply = agent.respond(message)
        return jsonify({"reply": reply})

    except ClientError as error:
        if error.code == 429 or error.status == "RESOURCE_EXHAUSTED":
            app.logger.warning("Gemini request quota exhausted")
            return jsonify({
                "error": "Gemini's request quota is exhausted. Wait for it to reset or check your Google AI Studio limits and billing."
            }), 429

        app.logger.warning("Gemini rejected the request with HTTP %s", error.code)
        return jsonify({
            "error": "Gemini rejected the request. Check the API key and request configuration."
        }), 502

    except ServerError as error:
        app.logger.warning("Gemini request failed: %s", error)
        return jsonify({
            "error": "Gemini is temporarily unavailable."
        }), 503
    except Exception:
        app.logger.exception("Unexpected error while handling chat request")
        return jsonify({
            "error": "Could not process your chat message."
        }), 500


@app.get("/api/characters/<character_id>/sheet")
def character_sheet(character_id):
    try:
        safe_character_id = uuid.UUID(character_id).hex
    except ValueError:
        return jsonify({"error": "Character sheet not found."}), 404

    sheet_directory = character_output_root / safe_character_id
    sheet_path = sheet_directory / "filled_character_sheet.pdf"
    if not sheet_path.is_file():
        return jsonify({"error": "Character sheet not found."}), 404

    return send_from_directory(
        sheet_directory,
        sheet_path.name,
        mimetype="application/pdf",
        as_attachment=False,
        max_age=0,
    )

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)