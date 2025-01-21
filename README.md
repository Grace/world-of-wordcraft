# World of Wordcraft

## Game Demo
Link to play the game in your browser: [https://world-of-wordcraft.up.railway.app/](https://world-of-wordcraft.up.railway.app/)

If you get disconnected or run into an error, refresh the page and try again in a minute. The app goes to sleep based on traffic.

## Description
A love letter to early MMORPGs from the 70s, 80s, and early 90s (also known as MUDs) designed for accessibility. In-game worldbuilding generated with OpenAI.

## Features  
- **Screen-Reader Friendly Gameplay**: Currently in development, featuring a built-in `speech on` command for speech-to-text functionality and a `speech repeat` command to replay visible game updates for the player.  
- **Dynamic Room Generation**: Leveraging OpenAI to create immersive environments, with efforts underway to build a game engine that adds structure to the creative chaos of AI-generated prompts.  
- **Player Roles and Privileges**: A hierarchical role system, including players, moderators, and admins, with escalating permissions.  
- **In-Game Player Chat**: A robust chat system for real-time interaction between players.  
- **Interactive NPCs**: Non-player characters equipped with dialogue options and tradeable items to enrich the gameplay experience.  
- **Player Inventory and Trading**: Manage inventory and trade items seamlessly within the game.  

## Deployment
1. Clone the repository.
2. Set up a Railway project and add your `OPENAI_API_KEY` to environment variables.
3. Create a `JWT_SECRET_KEY` (ask ChatGPT to generate one if you don't know how) and add it to environment variables.
4. Run `railway up` to deploy.

## Local Development
1. Install dependencies: `pip install -r requirements.txt`.
2. Run the server: `python -m app.server.py`.
3. Connect to `ws://localhost:5001` using a WebSocket client like `wscat` or point your browser to `localhost:5001`.

## Extra Goals
- [ ] Create game engine to make everything else on this to-do list more managable
- [ ] Make room generation be based on exits described in previously generated, connected rooms
- [ ] Implement help command for more information about other commands
- [x] Add roles such as moderator and admin with varying priviledges
- [ ] Make rooms, NPCs, items, and interactions editable by moderators and/or admins
- [x] Add player chat system (say, yell, tell)
- [ ] Add fishing system
- [ ] Add player trading system
- [ ] Add in-game currency and item shops
- [ ] Implement functional puzzles
- [ ] Add weather system
- [ ] Implement crafting
- [ ] Add support for PostgreSQL instead of or in addition to SQLite
- [ ] Setup unit and/or integration tests
- [ ] Setup development build/deployment

## Disclaimer
This project is entirely unrelated to any commercial MMORPGs, despite its name being a playful pun. It is an open-source initiative focused on exploring the effective use of AI for generating textual game content. Any resemblance between the generated content and existing copyrighted material is purely coincidental.
