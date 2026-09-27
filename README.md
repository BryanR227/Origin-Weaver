# Origin-Weaver [origin-weaver](https://origin-weaver.design/frontend/index.html)
<p align="center">
  <img width="440" height="440" alt="Screenshot 2026-09-26" src="frontend/docs/pics/favicon.png" />
</p>

## Inspiration
Origin Weaver grew out of a shared experience everyone on the team had. When getting started with tabletop role-playing games it can feel overwhelming. Creating a first character means navigating classes, abilities, and a lot of unfamiliar choices. We wanted to ease that learning curve feel more like a conversation than a looking at a textbook. We decided to start with Dungeons & Dragons 5th Edition as that is the most popular system and the one that new players will most likely interact with first. 

## What it does
Origin Weaver is an AI-assisted character-building chat for D&D 5e. Players can choose a guided path based on their experience level or start a free-form conversation. The guided paths ask about a character's concept, personality, and preferred playstyle, then use those answers to help shape character ideas. The responses will then map the choices to a PDF character sheet. For entries longer than the associated text box then application will splice the content into a printout booklet that the user can attach to the physical sheet. There will be an option for the narration of the chat returning chat logs.

## How we built it
The frontend uses HTML, CSS, and JavaScript for the chatbox and interfaces. Its styles are organized by responsibility into different stylesheets. A Python Flask server serves the frontend and exposes a `/api/chat` endpoint. That endpoint passes messages to a Gemini-powered agent built with Google's Gen AI SDK; the agent's behavior is configured by `personality.json`. The Gemini API key is read from the `GEMINI_API_KEY` environment variable rather than being placed in browser code. A looping video provides the interface background. The context for the game system is provided in organized json files divided into rules, character, etc.


**Challenges we ran into**<br /><br />
The first issue we ran into was not code related as we had to decide what the scope of the project is. Then we portioned the work between the group members based on experience. For the frontend, the landing evolved from a basic chatbot page to themed paged with a animated background. While working on the Elevenlabs text to voice, we ran into the issue that the chat messages were returned in markdown format. As workaround the markdown was rewritten into a text file first. We made sure the voice package could be paused and scrubbed. 


**Accomplishments that we're proud of**<br /><br />
We are proud that we were able to come together and come about withna finished product by the evening of the first day.


**What we learned**<br /><br />



**What's next for Origin Weaver**<br /><br />

## Character Sheet Generation

Install the Python dependencies with `pip install -r requirements.txt`. The app uses `pdf/5E_CharacterSheet_Fillable (3).pdf` as its fillable D&D 5e character sheet template by default. Set `CHARACTER_SHEET_TEMPLATE` only if the template is stored at a different path on the backend. Generated character sheets are stored under `instance/characters/` and returned in chat as a PDF preview and download link.
