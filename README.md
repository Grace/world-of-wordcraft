# World of Wordcraft

<img width="1222" alt="image" src="https://github.com/user-attachments/assets/1f1422bf-13b0-42d2-baa1-75534747ff03" />

## Game Demo  
[Play the Game in Your Browser](https://world-of-wordcraft.up.railway.app/)  

Dive into **World of Wordcraft**, a real-time text-based MMORPG powered by AI! This open-source project allows players to explore a procedurally generated world of words and interact in real time.


**Note:**  
- If you encounter disconnections or errors, simply refresh the page and try again after a minute. The app may go into sleep mode during periods of low traffic to conserve resources.  
- For the best experience, use a modern browser with WebSocket support enabled.

## Features  
- **Text-to-Speech Accessibility**: Activate with the `speech on` command to narrate game events, offering a more immersive and accessible experience. Replay recent updates with the `speech repeat` command.
- **Dynamic Room Generation**: Dynamic environments crafted with OpenAI, with an evolving game engine to add structure to the creative chaos of AI-generated content.
- **Real-Time Player Chat**: Engage with other players using a robust in-game chat system.  
- **Interactive NPCs**: Encounter non-player characters with dialogue options and tradeable items to enhance gameplay.
- **Inventory and Trading**: Manage your items and trade seamlessly with other players.
- **Hierarchical Role System**: Player roles include regular players, moderators, and admins, each with distinct permissions.

## Deployment
1. Clone the repository.
2. Create .env file in the root folder of the project
3. Set up a Railway project and add your `OPENAI_API_KEY` to the .env file.
4. Run `railway up` to deploy.

## Local Development
1. Install dependencies: `pip install -r requirements.txt`.
2. Add `OPENAI_API_KEY=<your OPENAI API key>` and `ENVIRONMENT=development` to a .env file in the root folder.
3. Run the server: `python -m app.main`.
4. Connect to `ws://localhost:5001` using a WebSocket client like `wscat` or point your browser to `localhost:5001`.

Example .env file content:
```
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 🤝 Contributing

Contributions encouraged! Whether it's fixing a bug, improving gameplay mechanics, or adding new features, your help is appreciated.

To contribute:
1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Submit a pull request with a clear description of your changes.

## Extra Goals
- [ ] **Build a Core Game Engine**: Develop a robust game engine to streamline the implementation of all other features and improve maintainability.  
- [ ] **Enhanced Room Generation**: Ensure room generation dynamically accounts for exits in connected rooms, creating a more cohesive world.  
- [x] **Help Command**: Add a `help` command to provide detailed guidance on all available commands.  
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
- [ ] **Super Big Font**: Enable horizontal scrolling to accommodate players who benefit from larger font sizes
- [ ] **Text-to-speech Customization**: Add user controls to adjust how far back the built-in text-to-speech repeats from output history.

## Disclaimer
This project, **World of Wordcraft**, is an independent, open-source text-based game developed as an experimental exploration of AI's role in generating interactive textual game content. It is not affiliated with, endorsed by, or associated with Blizzard Entertainment or any other entity that holds trademarks or intellectual property rights for similarly named or related works. The use of the name is intended as a lighthearted pun and is not intended to cause confusion or infringe upon any existing trademarks or intellectual property.

The AI-generated content used in this game is produced using OpenAI's language model and is derived from publicly available datasets. While every effort is made to ensure originality, the creators of this project do not claim ownership over the AI-generated content and cannot guarantee that such content does not inadvertently resemble or draw from existing copyrighted works. Any similarities to copyrighted material are purely coincidental.

This project is provided "as is" without warranty of any kind, express or implied. By using this project, you acknowledge and agree that the developers are not liable for any claims, damages, or disputes arising from:
1. The use of the name **World of Wordcraft** or any potential confusion it may cause.
2. The content generated by the AI, including but not limited to claims of copyright infringement or plagiarism.
3. Any loss, harm, or issues arising from the use or misuse of this open-source software.

Users and contributors are encouraged to engage responsibly and to ensure compliance with applicable laws and regulations. If you believe that any aspect of this project infringes upon your intellectual property or other rights, please contact the developers to resolve the matter promptly.
