# World of Wordcraft
An open-source, text-based MMORPG designed for screen readers. In-game worldbuilding generated with OpenAI. Proof of concept.

## Demo
[https://world-of-wordcraft-production.up.railway.app/](https://world-of-wordcraft-production.up.railway.app/)

## Features
- Screen-reader-friendly gameplay.
- Dynamic room generation with OpenAI.
- NPCs with dialogues and items.
- Player inventory and trading system.

## Deployment
1. Clone the repository.
2. Set up a Railway project and add `OPENAI_API_KEY` to environment variables.
3. Run `railway up` to deploy.

## Local Development
1. Install dependencies: `pip install -r requirements.txt`.
2. Run the server: `python app/server.py`.
3. Connect to `ws://localhost:8765` using a WebSocket client or point your browser to `localhost:5001`.
