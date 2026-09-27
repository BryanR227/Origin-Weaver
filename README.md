# Origin-Weaver [origin-weaver](https://origin-weaver.design/)
<p align="center">
  <img width="440" height="440" alt="Screenshot 2026-09-26" src="frontend/docs/pics/favicon.webp" />
</p>

## Built With
[![Aseprite](https://img.shields.io/badge/Aseprite-7D929E?style=for-the-badge\&logo=aseprite\&logoColor=white)](https://www.aseprite.org/)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge\&logo=css3\&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![CSV](https://img.shields.io/badge/CSV-217346?style=for-the-badge\&logo=microsoft-excel\&logoColor=white)](https://en.wikipedia.org/wiki/Comma-separated_values)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-000000?style=for-the-badge\&logo=elevenlabs\&logoColor=white)](https://elevenlabs.io/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge\&logo=flask\&logoColor=white)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Gemini-8E75B2?style=for-the-badge\&logo=google-gemini\&logoColor=white)](https://ai.google.dev/)
[![GoDaddy](https://img.shields.io/badge/GoDaddy-1BDBDB?style=for-the-badge\&logo=godaddy\&logoColor=white)](https://www.godaddy.com/)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge\&logo=html5\&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge\&logo=javascript\&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![JSON](https://img.shields.io/badge/JSON-000000?style=for-the-badge\&logo=json\&logoColor=white)](https://www.json.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge\&logo=postgresql\&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)](https://www.python.org/)
[![TigerData](https://img.shields.io/badge/TigerData-FF6B35?style=for-the-badge\&logo=postgresql\&logoColor=white)](https://www.tigerdata.com/)

## Inspiration
Origin Weaver grew out of a shared experience everyone on the team had. When getting started with tabletop role-playing games it can feel overwhelming. Creating a first character means navigating classes, abilities, and a lot of unfamiliar choices. We wanted to ease that learning curve and make it feel more like a conversation than a looking at a textbook. We decided to start with Dungeons & Dragons 5th Edition, as that is the most popular system and the one that new players will most likely interact with first.

## What it does
Origin Weaver is an AI-assisted character-building chat for D&D 5e. Players can choose a guided path based on their experience level or start a free-form conversation. The guided paths ask about a character's concept, personality, and preferred playstyle, then use those answers to help shape character ideas. The responses will then map the choices to a PDF character sheet. For entries longer than the associated text box then application will splice the content into a printout booklet that the user can attach to the physical sheet. There will be an option for the narration of the chat returning chat logs.

## How we built it
The frontend uses HTML, CSS, and JavaScript for the chatbox and interfaces. Its styles are organized by responsibility into different stylesheets. A Python Flask server serves the frontend and exposes a `/api/chat` endpoint. That endpoint passes messages to a Gemini-powered agent built with Google's Gen AI SDK; the agent's behavior is configured by `personality.json`. The Gemini API key is read from the `GEMINI_API_KEY` environment variable rather than being placed in browser code. A looping video provides the interface background. The context for the game system is provided in organized json files divided into rules, character, etc. A python script is used to generate the character sheet from the information provided to the chatbot by the user. Tiger Data was used to create a basic user account table using PostgreSQL and connected to the frontend to enable user sign-up and authentication.

## Challenges we ran into
The first issue we ran into was not code related as we had to decide what the scope of the project is. After much deliberation the scope of the project was confirmed to be a web application with an AI chat portal that guides new players through the character creation process.
While working on the Elevenlabs text to voice, we ran into the issue that the chat messages were returned in markdown format. As workaround the markdown was rewritten into a text file first. We made sure the voice package could be paused and scrubbed. Similar to other teams' experience, Snowflake was difficult to get running and merged with the Gemini layer. We decided to abandon the integration to focus on other core issues.
We looked at using Vultr for training a overlayer overnight so that it may reduce the current token usage. In the essence of time guardrails were added to achieve similar results.
While using Tiger Data, we had issues correcting the tunnel between the PostgreSQL database and application - specifically while using the API.


## Accomplishments that we're proud of
We are proud that we were able to come together and come about with a finished product by the evening of the first day. Our team was happy about the fact that we deployed our website successfully using a custom domain, and getting all frontend & backend components to work together succcessfully.

## What we learned 
Our team learned the best way to create a project from scratch, using minimal resources and with little prior experience. We also applied a lot of knowledge we gained from courses at our college.

## What's next for Origin Weaver
We look to keep polishing the current project to ensure accuracy and reduce hallucinations. Afterwards, a potential addition would be the AI running a small chatbox based one-shot DnD game to onboard the new player. We'll look into clarifying the different paths. New players will be handheld through the entire character creation. For the backend, We plan to save past user sessions and character builds by using Tiger Data for users to be able to 'level up', as we are currently constrained by time and money. Additionally, the guided paths will be improved, based upon the skill level of the user. For the frontend UI, we plan on adding a feature to change the background of the chatbot (changing bartenders, etc.) and adding easter eggs for the user to interact with. To match different bartender backgrounds, there are plans to add more voicepacks for customizability. Additionally, adding chat bubbles instead of a typical chatbot interface is a feature that we plan on exploring.

## Character Sheet Generation
Install the Python dependencies with `pip install -r requirements.txt`. The app uses `pdf/5E_CharacterSheet_Fillable (3).pdf` as its fillable D&D 5e character sheet template by default. Set `CHARACTER_SHEET_TEMPLATE` only if the template is stored at a different path on the backend. Generated character sheets are stored under `instance/characters/` and returned in chat as a PDF preview and download link.
