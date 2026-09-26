import os
from google import genai


class Agent:
    def __init__(self):
        self.client = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"]
        )

        self.chat = self.client.chats.create(
            model="gemini-3.8-flash"
        )

    def respond(self, message):
        response = self.chat.send_message(message)
        return response.text or ""