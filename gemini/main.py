import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError

load_dotenv()

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        break

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=user_input,
        )

        print("Advisor:", response.text)

    except ServerError as e:
        print("Gemini is temporarily unavailable. Try again in a moment.")
        print(f"Error: {e}")