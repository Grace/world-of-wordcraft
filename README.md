# World of Wordcraft

## Game Demo
Link to play the game in your browser: [https://world-of-wordcraft.up.railway.app/](https://world-of-wordcraft.up.railway.app/)

If you get disconnected or run into an error, refresh the page and try again in a minute. The app goes to sleep based on traffic.

## Description
A love letter to early MMORPGs from the 70s, 80s, and early 90s (also known as MUDs) designed for accessibility. In-game worldbuilding generated with OpenAI.

## Features
- Screen-reader friendly gameplay (work in progress).
- Dynamic room generation with OpenAI.
- NPCs with dialogues and items.
- Player inventory and trading system.

## Deployment
1. Clone the repository.
2. Set up a Railway project and add `OPENAI_API_KEY` to environment variables.
3. Run `railway up` to deploy.

## Local Development
1. Install dependencies: `pip install -r requirements.txt`.
2. Run the server: `python -m app.server.py`.
3. Connect to `ws://localhost:5001` using a WebSocket client like `wscat` or point your browser to `localhost:5001`.

## Extra Goals
- [ ] Make room generation be based on exits described in previously generated, connected rooms
