import os
import json

from google import genai

class Agent:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"]
        )

        with open("personality.json", "r", encoding="utf-8") as f:
            personality = json.load(f)

        self.chat = self.client.chats.create(
            model="gemini-3.8-flash",
            config={
                "system_instruction": personality["system_prompt"]
            }
        )

    def respond(self, message):
        response = self.chat.send_message(message)
        return response.text or ""