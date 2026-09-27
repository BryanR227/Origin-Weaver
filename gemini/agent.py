import json
import os
from pathlib import Path

from google import genai
from google.genai import types
from tools import get_class_info


class Agent:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"]
        )
        self.model = "gemini-3.8-flash"

        personality_path = Path(__file__).with_name("personality.json")
        with personality_path.open("r", encoding="utf-8") as f:
            personality = json.load(f)
        self.system_instruction = personality["system_prompt"]

        self.chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                tools=[get_class_info],
                max_output_tokens=1000,
            )
        )

    def respond(self, message):
        response = self.chat.send_message(message)
        return response.text or ""

    def generate_character(self, message, field_keys):
        """Return a short explanation and values matching the character CSV schema."""
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "reply": {
                    "type": "STRING"
                },
                "fields": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "key": {
                                "type": "STRING"
                            },
                            "value": {
                                "type": "STRING"
                            }
                        },
                        "required": ["key", "value"]
                    }
                }
            },
            "required": ["reply", "fields"]
        }
        generation_instructions = (
            f"{self.system_instruction}\n\n"
            "Create a D&D character sheet from the user's request. "
            "Return a short, readable character explanation in reply. "
            "Return character-sheet values in the fields array as key/value pairs. "
            "The key must exactly match one of the supplied CSV field keys. "
            "Every value must be a string. "
            "Use an empty string for unknown, optional, or unprovided personal details "
            "instead of inventing them. "
            "Use 0 or 1 for proficiency checkbox values. "
            "Keep comma-separated values suitable for the CSV sheet. "
            "Use standard D&D 5e conventions and do not claim access to exhaustive source catalogs."
        )
        prompt = f"Character request:\n{message}\n\nCSV field keys:\n" + "\n".join(field_keys)
        print("Character field count:", len(field_keys))
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=generation_instructions,
                response_mime_type="application/json",
                response_schema=response_schema,
                max_output_tokens=8192,
            ),
        )

        try:
            result = json.loads(response.text or "")
        except json.JSONDecodeError as error:
            raise ValueError("Gemini returned invalid character-sheet data.") from error
        
        returned_fields = result.get("fields", [])

        if not isinstance(returned_fields, list):
            raise TypeError("Gemini returned invalid character field data.")

        fields = {}

        for item in returned_fields:
            if not isinstance(item, dict):
                raise TypeError("Gemini returned an invalid character field.")

            key = item.get("key", "")
            value = item.get("value", "")

            if not isinstance(key, str) or not isinstance(value, str):
                raise TypeError("Gemini returned a non-text character field.")

            if key not in field_keys:
                raise ValueError(f"Gemini returned an unknown character field: {key}")

            fields[key] = value

        reply = result.get("reply", "")
        if not isinstance(reply, str):
            raise TypeError("Gemini returned a non-text character summary.")
        if not reply.strip():
            raise ValueError("Gemini did not return a character summary.")
        return reply, fields