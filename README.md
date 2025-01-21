# World of Wordcraft

## Game Demo
Link to play the game in your browser: [https://world-of-wordcraft.up.railway.app/](https://world-of-wordcraft.up.railway.app/)

If you get disconnected or run into an error, refresh the page and try again in a minute. The app goes to sleep based on traffic.

## Description
A love letter to early MMORPGs from the 70s, 80s, and early 90s (also known as MUDs) designed for accessibility. In-game worldbuilding generated with OpenAI.

## Features  
- **Text-to-Speech Accessibility**: Activate with the `speech on` command to narrate game events, offering a hands-free, immersive experience. Replay recent updates with the `speech repeat` command.  
- **Dynamic Room Generation**: Immersive environments crafted with OpenAI, with an evolving game engine to add structure to the creative chaos of AI-generated content.  
- **Hierarchical Role System**: Player roles include regular players, moderators, and admins, each with distinct permissions.  
- **Real-Time Player Chat**: Engage with other players using a robust in-game chat system.  
- **Interactive NPCs**: Encounter non-player characters with dialogue options and tradeable items to enhance gameplay.  
- **Inventory and Trading**: Manage your items and trade seamlessly with other players.  

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
- [ ] **Build a Core Game Engine**: Develop a robust game engine to streamline the implementation of all other features and improve maintainability.  
- [ ] **Enhanced Room Generation**: Ensure room generation dynamically accounts for exits in connected rooms, creating a more cohesive world.  
- [ ] **Help Command**: Add a `help` command to provide detailed guidance on all available commands.  
- [x] **Roles and Privileges**: Implement hierarchical roles such as moderators and admins, each with varying levels of permissions.  
- [ ] **Editable World Elements**: Allow moderators and admins to modify rooms, NPCs, items, and interactions in-game.  
- [x] **Player Chat System**: Introduce versatile player communication commands (`say`, `yell`, `tell`) for real-time interaction.  
- [ ] **Fishing System**: Add a fishing mechanic for players, expanding gameplay variety.  
- [ ] **Player Trading System**: Allow players to trade items seamlessly in-game.  
- [ ] **In-Game Currency and Shops**: Introduce a currency system and item shops for economic gameplay elements.  
- [ ] **Functional Puzzles**: Incorporate puzzles that players can solve for rewards or story progression.  
- [ ] **Weather System**: Implement a dynamic weather system to add environmental variety and immersion.  
- [ ] **Crafting Mechanics**: Introduce crafting features for players to create items from materials.  
- [ ] **Scalable Database Support**: Add support for scalable SQL and/or NoSQL database(s)
- [ ] **Unit and Integration Testing**: Set up comprehensive unit and integration tests to ensure stability and reliability.  
- [ ] **Development Build/Deployment**: Establish a robust build and deployment pipeline to streamline development and testing.  

## Disclaimer
This project is entirely unrelated to any commercial MMORPGs, despite its name being a playful pun. It is an open-source project focused on exploring the effective use of AI for generating textual game content. Any resemblance between the generated content and existing copyrighted material is coincidental.
